from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
import sqlite3
from werkzeug.exceptions import abort
import process
import requests
import json
import logging
import audio2midi

app = Flask(__name__)

app.config.update({'RECAPTCHA_ENABLED': True,
                   'RECAPTCHA_SITE_KEY':
                       '6LeJeB8aAAAAAMr27aI8yHkk-XycRtakq-DlZ5AL',
                   'RECAPTCHA_SECRET_KEY':
                       '6LeJeB8aAAAAACWovBpSv-1Ws4s-KxPocaa-jxE2'})


logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger
handler = logging.FileHandler('logging.log') # creates handler for the log file
logger.addHandler(handler) # adds handler to the werkzeug WSGI logger

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_file(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?',
                        (file_id,)).fetchone()
    conn.close()
    if file is None:
        abort(404)
    return file    

@app.route('/')
def index():
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_file_convert():
    captcha_response = request.form['g-recaptcha-response']
    uploaded_file = request.files['file']

    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data = {'secret' :
                                  '6LeJeB8aAAAAACWovBpSv-1Ws4s-KxPocaa-jxE2',
                                  'response' :
                                  request.form['g-recaptcha-response']})

    google_response = json.loads(r.text)
    print('JSON: ', google_response)

    if google_response['success']:
        if uploaded_file.filename != '' and request.form['btn'] == "convertMIDI":
            uploaded_file.filename = uploaded_file.filename[:-4]
            file_processed = audio2midi.run(file_upload, output_file_name)
            
            connection = sqlite3.connect('database.db')
            cur = connection.cursor()

            cur.execute("INSERT INTO files (title) VALUES (?)",
                        (uploaded_file.filename,)) 
            connection.commit()
            connection.close()
            logger.info("Converting wav file:" + uploaded_file.filename)
            return send_file(file_processed, attachment_filename= uploaded_file.filename + '.mid',as_attachment=True)  
    else:
        logger.info("Recaptcha failed.")
        return render_template('index.html')