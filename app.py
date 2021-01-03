from flask import Flask, flash, request, redirect, url_for, render_template, send_file

from werkzeug.utils import secure_filename
import sqlite3
from werkzeug.exceptions import abort
import process

app = Flask(__name__)

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
    uploaded_file = request.files['file']
    if uploaded_file.filename != '' and request.form['btn'] == "convertMIDI":
        uploaded_file.filename = uploaded_file.filename[:-4]
        file_processed = process.getFileAndConvertMIDI(uploaded_file,  uploaded_file.filename + '.mid')
        
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()

        cur.execute("INSERT INTO files (title) VALUES (?)",
                    (uploaded_file.filename,)) 
        connection.commit()
        connection.close()
        
        return send_file(file_processed, attachment_filename= uploaded_file.filename + '.mid',as_attachment=True)  

if __name__ == 'main':
    app.run(ssl_context='adhoc', host='0.0.0.0', port=51100, debug=True, threaded=True) 