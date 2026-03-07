from flask import Flask, render_template, request
from gtts import gTTS
import os
import uuid
import csv
from datetime import datetime

app = Flask(__name__)
# Ensure the folder for audio files exists
os.makedirs('static/audio', exist_ok=True)

# Define our log file path
LOG_FILE = 'meditations_log.csv'

# Create the CSV file with headers if it doesn't exist yet
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Age', 'Mood', 'Context', 'Style', 'Length', 'Audio Filepath'])

def log_request(age, mood, context, style, length, filepath):
    """Saves the generation details to a CSV file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, age, mood, context, style, length, filepath])

def generate_script(age, mood, context, style, length):
    """This function builds the custom meditation script based on form inputs."""
    script = f"Welcome. Take a moment to settle in. It is completely normal to feel {mood} right now. "
    
    if age == "13-15":
        script += "Being in middle school or starting high school can be really overwhelming, and that is okay. "
    elif age == "16-18":
        script += "The later years of high school carry a lot of pressure, but you are handling it as best as you can. "

    if context == "exam soon":
        script += "I know you have an exam coming up. Let's release the physical tension you are holding about it. "
    elif context == "big project":
        script += "That big project is weighing on your mind. Let's take a step back from it for just a moment. "
    else:
        script += "Whatever studying you have left to do, it can wait for just a few minutes while you recharge. "

    if style == "motivational":
        script += "You have put in the work, and you are capable of amazing things. "
    elif style == "concentration":
        script += "Let's bring our focus entirely to the present moment, clearing away any distractions. "
    else:
        script += "Give yourself permission to just relax, be still, and let go of any expectations. "

    script += "Now, let's focus on your breath. "
    
    try:
        minutes = int(length)
    except ValueError:
        minutes = 5 # Fallback just in case
        
    for _ in range(minutes * 2): 
        script += "Breathe in deeply... hold it... and breathe out slowly. Let your shoulders drop. "

    script += "When you are ready, gently open your eyes. You've got this."
    return script

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. Grab form data
        age = request.form.get('age')
        mood = request.form.get('mood')
        context = request.form.get('context')
        style = request.form.get('style')
        length = request.form.get('length')
        
        # ERROR HANDLING 1: Check for missing inputs
        if not all([age, mood, context, style, length]):
            return render_template('index.html', error="Oops! Please make sure all fields are selected.")

        custom_script = generate_script(age, mood, context, style, length)
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join('static', 'audio', filename)
        
        # ERROR HANDLING 2: Try/Except block for TTS generation
        try:
            print("Generating audio... please wait...")
            tts = gTTS(text=custom_script, lang='en', slow=False)
            tts.save(filepath)
            print("Audio saved successfully!")
            
            # LOGGING: Save the record to our CSV
            log_request(age, mood, context, style, length, filepath)
            
            return render_template('result.html', audio_file=filename)
            
        except Exception as e:
            # If Google's API fails or there is no internet connection
            print(f"Error generating audio: {e}")
            return render_template('index.html', error="Sorry, we had trouble generating the audio. Please check your internet connection and try again.")
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)