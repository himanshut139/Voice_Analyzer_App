from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from langdetect import detect
from googletrans import Translator
from collections import Counter
import re
import speech_recognition as sr
from pydub import AudioSegment
import io

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voice_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

recognizer = sr.Recognizer()
translator = Translator()

class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    original_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)
    language = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class WordFrequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    word = db.Column(db.String(50))
    frequency = db.Column(db.Integer)

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    phrase = db.Column(db.String(255))
    frequency = db.Column(db.Integer)

# Creating the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    return "Hello from Voice Analyzer"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.form
    user_id = data.get('user_id')
    audio_file = request.files.get('audio')

    if not audio_file:
        return jsonify({'status': 'error', 'message': 'No audio file provided.'}), 400

    # Converting audio to text
    recognizer = sr.Recognizer()
    try:
        if audio_file.filename.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_file)
            audio = audio.set_channels(1).set_frame_rate(16000)  
            with io.BytesIO() as buffer:
                audio.export(buffer, format="wav")
                buffer.seek(0)
                with sr.AudioFile(buffer) as source:
                    audio = recognizer.record(source)
        else:
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
        
        original_text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return jsonify({'status': 'error', 'message': 'Could not understand audio.'}), 400
    except sr.RequestError:
        return jsonify({'status': 'error', 'message': 'Could not request results from Google Speech Recognition service.'}), 500

    # Detecting language
    language = detect(original_text)
    
    if language != 'en':
        translated_text = translator.translate(original_text, src=language, dest='en').text
    else:
        translated_text = original_text
    
    transcription = Transcription(user_id=user_id, original_text=original_text, translated_text=translated_text, language=language)
    db.session.add(transcription)
    db.session.commit()
    
    update_word_frequencies(user_id, translated_text)
    update_phrases(user_id, translated_text)
    
    return jsonify({'status': 'success', 'translated_text': translated_text})

def update_word_frequencies(user_id, text):
    # Removing punctuation and lowercase
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    
    # Updating/inserting word frequencies
    for word, count in word_counts.items():
        existing = WordFrequency.query.filter_by(user_id=user_id, word=word).first()
        if existing:
            existing.frequency += count
        else:
            new_entry = WordFrequency(user_id=user_id, word=word, frequency=count)
            db.session.add(new_entry)
    db.session.commit()

def update_phrases(user_id, text):
    phrases = re.findall(r'\b\w+\b(?:\s+\b\w+\b){0,2}', text.lower())  # Top 3-word phrases
    phrase_counts = Counter(phrases)
    
    for phrase, count in phrase_counts.items():
        existing = Phrase.query.filter_by(user_id=user_id, phrase=phrase).first()
        if existing:
            existing.frequency += count
        else:
            new_entry = Phrase(user_id=user_id, phrase=phrase, frequency=count)
            db.session.add(new_entry)
    db.session.commit()

@app.route('/transcribe_live', methods=['POST'])
def transcribe_live():
    if 'audio' not in request.files:
        return jsonify({'status': 'error', 'message': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    user_id = request.form.get('user_id')  # Ensure user_id is provided in the form data
    if not user_id:
        return jsonify({'status': 'error', 'message': 'No user_id provided'}), 400

    try:
        # Converting file to WAV if it's not in WAV format
        if audio_file.mimetype != 'audio/wav':
            audio = AudioSegment.from_file(audio_file)
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_io.seek(0)
            audio_file = wav_io

        recognizer = sr.Recognizer()
        audio_data = sr.AudioFile(audio_file)
        with audio_data as source:
            audio = recognizer.record(source)
        
        # Trying to recognize speech
        original_text = recognizer.recognize_google(audio)
        
        # Checking if transcription is empty
        if not original_text.strip():
            return jsonify({'status': 'error', 'message': 'No speech detected in the audio file'}), 400
        
        # Detecting language
        language = detect(original_text)
        
        if language != 'en':
            translated_text = translator.translate(original_text, src=language, dest='en').text
        else:
            translated_text = original_text
        
        # Save transcription data to the database
        transcription = Transcription(user_id=user_id, original_text=original_text, translated_text=translated_text, language=language)
        db.session.add(transcription)
        db.session.commit()
        
        update_word_frequencies(user_id, translated_text)
        update_phrases(user_id, translated_text)
        
        return jsonify({'status': 'success', 'transcription': original_text, 'translated_text': translated_text})

    except sr.UnknownValueError:
        return jsonify({'status': 'error', 'message': 'Could not understand audio. The audio may be too unclear.'}), 400
    except sr.RequestError as e:
        return jsonify({'status': 'error', 'message': f'Could not request results from Google Speech Recognition service; {e}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing audio file: {e}'}), 500

@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    transcriptions = Transcription.query.filter_by(user_id=user_id).all()
    if not transcriptions:
        return jsonify({'error': 'No data found for this user.'}), 404
    return jsonify([{
        'id': t.id,
        'original_text': t.original_text,
        'translated_text': t.translated_text,
        'language': t.language,
        'timestamp': t.timestamp
    } for t in transcriptions])

@app.route('/frequencies/<user_id>', methods=['GET'])
def get_word_frequencies(user_id):
    frequencies = WordFrequency.query.filter_by(user_id=user_id).all()
    if not frequencies:
        return jsonify({'error': 'No data found for this user.'}), 404
    return jsonify([{
        'word': f.word,
        'frequency': f.frequency
    } for f in frequencies])

@app.route('/phrase-frequencies/<user_id>', methods=['GET'])
def get_phrase_frequencies(user_id):
    phrases = Phrase.query.filter_by(user_id=user_id).all()
    if not phrases:
        return jsonify({'error': 'No data found for this user.'}), 404
    return jsonify([{
        'phrase': p.phrase,
        'frequency': p.frequency
    } for p in phrases])

@app.route('/comparison/<user_id>', methods=['GET'])
def compare_word_frequencies(user_id):
    user_frequencies = WordFrequency.query.filter_by(user_id=user_id).all()
    all_frequencies = WordFrequency.query.all()
    
    if not user_frequencies:
        return jsonify({'error': 'No data found for this user.'}), 404

    user_word_counts = {f.word: f.frequency for f in user_frequencies}
    all_word_counts = Counter(f.word for f in all_frequencies)
    
    comparison = {}
    for word, count in user_word_counts.items():
        comparison[word] = {
            'user_frequency': count,
            'all_users_frequency': all_word_counts.get(word, 0)
        }
    
    return jsonify(comparison)

if __name__ == '__main__':
    app.run(debug=True)
