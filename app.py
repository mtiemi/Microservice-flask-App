from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.exceptions import abort
import datetime
import sqlite3
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

@app.route('/')
def index():
    return render_template('index.html')

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
            file_processed = audio2midi.run(uploaded_file,  uploaded_file.filename + '.mid')
            
            connection = sqlite3.connect('database.db')
            cur = connection.cursor()

            cur.execute("INSERT INTO files (title) VALUES (?)",
                        (uploaded_file.filename,)) 
            connection.commit()
            connection.close()
            logger.info( '[{date:%d/%B/%Y %H:%M:%S}]'.format(date=datetime.datetime.now()) + " -  Converting wav file:" + uploaded_file.filename)
            return send_file(file_processed, attachment_filename= uploaded_file.filename + '.mid',as_attachment=True)  
    else:
        logger.info( '[{date:%d/%B/%Y %H:%M:%S}]'.format(date=datetime.datetime.now()) + " - Recaptcha failed.")

        return render_template('index.html')