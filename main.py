from flask import Flask, render_template, request
from libs.reader.file import FileReader
from random import randint
import os

app = Flask(__name__)

@app.route('/audiodata', methods = ['GET', 'POST'])
def audiorecog():
    if request.method == 'POST':
        file = request.files['file']
        filename = os.path.join("recordings", f"{randint(100000,999999)}.wav")
        with open(filename, "wb") as aud:
            aud_stream = file.read()
            aud.write(aud_stream)
        reader = FileReader(filename)
        detection = reader.recognize()
        os.remove(filename)
        if detection:
            if detection['CONFIDENCE'] > 2:
                return clean_song_name(detection['SONG_NAME'])    
            return 'Failed to match song'
        return 'Failed'
    return 'Error: request from GET'

def clean_song_name(name):
    return name.replace('_', ' ').strip('.mp3')

@app.route('/')
def index():
    return render_template('index.html', address=request.host)

if __name__=="__main__":
    app.run(debug=True)