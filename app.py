"""
Meditation Generator MVP
------------------------
A Flask-based web application that dynamically generates personalized meditation audio.
It uses rule-based string generation for the script, gTTS for text-to-speech, 
and pydub for precise audio manipulation and background track mixing.
"""

from flask import Flask, render_template, request
from gtts import gTTS
import os
import uuid
import csv
from datetime import datetime
from pydub import AudioSegment

app = Flask(__name__)

# Ensure required directories exist for static assets
os.makedirs('static/audio', exist_ok=True)
os.makedirs('static/bgm', exist_ok=True)

LOG_FILE = 'meditations_log.csv'

# Initialize the CSV log file with headers if it doesn't exist yet
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Age', 'Mood', 'Context', 'Style', 'Length', 'Audio Filepath'])

def log_request(age, mood, context, style, length, filepath):
    """Logs generation metadata to a local CSV file for basic analytics."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, age, mood, context, style, length, filepath])

def generate_script_parts(age, mood, context, style):
    """Builds the meditation script based on user inputs."""
    
    # --- PART 1: The Intro and Empathy ---
    intro = f"Welcome, and thank you for taking this time for yourself. Take a moment to settle into a comfortable position, either sitting up straight or lying down. Gently close your eyes. It is completely normal to feel {mood} right now. Acknowledge that feeling without judgment. You don't need to fight it, and you don't need to fix it. Just let it be. "
    
    # Safely cast age to integer for conditional logic
    try:
        age_num = int(age)
    except ValueError:
        age_num = 15
        
    if age_num <= 15:
        intro += f"Being {age_num} years old is an incredibly complex time. You are caught right in the middle of so many transitions—navigating new social dynamics, handling harder classes, and figuring out who you are. It can feel like everyone is watching you, and the pressure to fit in or succeed can be completely overwhelming. You are dealing with a lot of noise right now, and it is perfectly okay to feel exhausted by it. Give yourself permission to just pause. "
    else:
        intro += f"Being {age_num} carries a uniquely heavy burden. You are standing on the edge of adulthood, and suddenly it feels like every decision you make has massive consequences for your future. The expectations from your family, your teachers, and yourself can feel like a heavy weight pressing down on your chest. You are handling an immense amount of pressure as you prepare for the next chapter of your life, but right now, in this exact moment, you don't need to figure any of it out. The future can wait. "

    intro += "Let's begin by relaxing your physical body. Notice the top of your head, and let any tension there melt away. Relax your forehead, unfurrow your brow, and let your jaw drop slightly. Let this wave of relaxation travel down your neck, releasing the tight muscles in your shoulders. Let your arms become heavy and relaxed, all the way down to your fingertips. Notice the gentle rise and fall of your chest. Relax your stomach, your back, your legs, all the way down to your toes. You are completely supported by the surface beneath you. "

    if context == "exam soon":
        intro += "I know you have an important exam coming up. Your mind might be racing with facts, dates, formulas, and a lingering fear that you haven't done enough. Notice where you are holding that anxiety in your body—maybe a tightness in your chest, or a knot in your stomach—and on your next exhale, intentionally let it go. An exam is just a single piece of paper on a single day. It does not define your worth, your intelligence, or your future. For now, let go of the studying. You have prepared, and when the time comes, you will simply do your best. That is all anyone can ask of you. "
    elif context == "big project":
        intro += "You have a massive project weighing heavily on your mind. When we look at a mountain of work, it is easy to feel paralyzed by perfectionism or completely drained of creative energy. You might be feeling the guilt of taking a break right now, but let me assure you: resting is a crucial part of the creative process. Let's take a conscious step back from the planning, the drafting, and the execution. You don't need to produce anything right now. Just allow yourself to exist separately from your work. When you return to it later, your mind will be sharper and your energy restored. "
    else:
        intro += "The daily grind of studying, homework, and looking at screens can blur the lines between your personal time and your academic life. It might feel like you should always be doing something productive. But a machine cannot run continuously without breaking down, and neither can you. Whatever reading or assignments you have left to do today, they can wait. The books and the notifications will still be there later. These next few minutes are a strict boundary you have set for yourself—a safe space where your only job is to recharge your mind and restore your nervous system. "

    if style == "motivational":
        intro += "As you rest here, remind yourself of the incredible resilience you possess. You have faced difficult weeks before, you have navigated stress before, and you have survived 100 percent of your bad days. You have put in the work, and you are capable of truly amazing things. Do not let temporary fatigue convince you that you are not strong enough. You have a deep well of potential inside of you. Visualize yourself walking into your next challenge with your head held high, radiating quiet confidence and clarity. "
    elif style == "concentration":
        intro += "As we continue, let's practice bringing our focus entirely to the present moment. Your mind will naturally want to wander to past conversations or future worries. When it does, do not be frustrated. Simply notice the thought, imagine it placing it on a leaf floating down a gentle stream, and watch it drift away. Gently guide your spotlight of attention back to the sound of my voice, and the physical sensation of the air moving in and out of your body. Train your mind to stay anchored right here, in the stillness of the present. "
    else:
        intro += "For the rest of this practice, give yourself radical permission to just relax. Wrap yourself in a heavy, comforting blanket of peace. Imagine a soft, warm light surrounding your body, shielding you from the demands of the outside world. Within this space, there is no rush, there are no deadlines, and there is no pressure to perform. You are safe, you are grounded, and you are allowed to simply rest. "

    intro += "Now, let's transition into a period of deep, restorative breathing to anchor this feeling of calm. "

    # --- PART 2: The Breathing Loop ---
    # This segment is isolated so pydub can measure its exact length and duplicate it dynamically
    breath = "Breathe in deeply through your nose, filling your lungs entirely... hold it at the top... and exhale slowly and audibly through your mouth, letting all the stale air out. Notice the cool air entering your nostrils, and the warm air leaving. Allow your breath to find its own natural rhythm now. Just become a quiet observer of the gentle wave of your breathing. Let your mind drift gently, remaining completely at peace. "

    # --- PART 3: The Outro ---
    outro = "As we bring this meditation to a close, slowly bring your awareness back to the physical room around you. Notice the feeling of the air on your skin and the sounds in the distance. Gently wiggle your fingers and your toes, waking your body back up. Take one last, deep, energizing breath in... and let it out. When you are ready, gently open your eyes. You have everything you need to face the rest of your day. You've got this."

    return intro, breath, outro

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route handling both the frontend form display and backend audio generation."""

    if request.method == 'POST':
        # Extract form data
        age = request.form.get('age')
        mood = request.form.get('mood')
        context = request.form.get('context')
        style = request.form.get('style')
        length = request.form.get('length')
        
        # Basic validation to ensure no missing parameters
        if not all([age, mood, context, style, length]):
            return render_template('index.html', error="Oops! Please make sure all fields are selected.")

        # Generate the distinct script segments
        intro_text, breath_text, outro_text = generate_script_parts(age, mood, context, style)
        
        # Setup file paths
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join('static', 'audio', filename)
        
        temp_intro = os.path.join('static', 'audio', f"temp_i_{filename}")
        temp_breath = os.path.join('static', 'audio', f"temp_b_{filename}")
        temp_outro = os.path.join('static', 'audio', f"temp_o_{filename}")
        
        try:
            # Generate raw TTS audio files separately
            print("Generating voice segments...")
            gTTS(text=intro_text, lang='en', slow=False).save(temp_intro)
            gTTS(text=breath_text, lang='en', slow=False).save(temp_breath)
            gTTS(text=outro_text, lang='en', slow=False).save(temp_outro)
            
            # Load into pydub for duration math and assembly
            print("Calculating perfect audio length...")
            audio_intro = AudioSegment.from_file(temp_intro)
            audio_breath = AudioSegment.from_file(temp_breath)
            audio_outro = AudioSegment.from_file(temp_outro)
            
            # Convert user requested length (minutes) to milliseconds
            try:
                target_minutes = int(length)
            except ValueError:
                target_minutes = 5
            target_ms = target_minutes * 60 * 1000
            
            # Calculate how much time remains after the fixed intro and outro
            current_ms = len(audio_intro) + len(audio_outro)
            remaining_ms = target_ms - current_ms
            
            if remaining_ms > 0:
                # Determine exactly how many times the breathing loop fits into the remaining time
                loops = int(remaining_ms // len(audio_breath))
                # Assemble the finalized voice track
                voice = audio_intro + (audio_breath * loops) + audio_outro
            else:
                voice = audio_intro + audio_breath + audio_outro
                
            print("Mixing with background audio...")
            bgm_path = os.path.join('static', 'bgm', 'ambient.mp3')
            
            # Mix background track if it exists
            if os.path.exists(bgm_path):
                bgm = AudioSegment.from_file(bgm_path)
                bgm = bgm - 13 # Lower the BGM volume so the guide's voice remains clear
                
                # Loop background music until it covers the entire voice track
                while len(bgm) < len(voice):
                    bgm += bgm
                # Trim the tail off the background music for an exact match
                bgm = bgm[:len(voice)]
                
                final_audio = voice.overlay(bgm)
                final_audio.export(filepath, format="mp3")
            else:
                voice.export(filepath, format="mp3")

            # Cleanup: Remove intermediate TTS files to save disk space
            for temp_file in [temp_intro, temp_breath, temp_outro]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            print("Audio saved successfully!")
            log_request(age, mood, context, style, length, filepath)
            
            return render_template('result.html', audio_file=filename)
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return render_template('index.html', error="Sorry, we had trouble generating the audio. Please check your internet connection and try again.")
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)