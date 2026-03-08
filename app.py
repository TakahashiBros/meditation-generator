from flask import Flask, render_template, request
from gtts import gTTS
import os
import uuid
import csv
from datetime import datetime

app = Flask(__name__)
os.makedirs('static/audio', exist_ok=True)
os.makedirs('static/bgm', exist_ok=True)

LOG_FILE = 'meditations_log.csv'

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Age', 'Mood', 'Context', 'Style', 'Length', 'Audio Filepath'])

def log_request(age, mood, context, style, length, filepath):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, age, mood, context, style, length, filepath])

def generate_script(age, mood, context, style, length):
    """Builds the expanded meditation script using dynamic text padding for duration."""
    
    script = f"Welcome, and thank you for taking this time for yourself. Take a moment to settle into a comfortable position, either sitting up straight or lying down. Gently close your eyes. It is completely normal to feel {mood} right now. Acknowledge that feeling without judgment. You don't need to fight it, and you don't need to fix it. Just let it be. "
    
    try:
        age_num = int(age)
    except ValueError:
        age_num = 15
        
    if age_num <= 15:
        script += f"Being {age_num} years old is an incredibly complex time. You are caught right in the middle of so many transitions—navigating new social dynamics, handling harder classes, and figuring out who you are. It can feel like everyone is watching you, and the pressure to fit in or succeed can be completely overwhelming. You are dealing with a lot of noise right now, and it is perfectly okay to feel exhausted by it. Give yourself permission to just pause. "
    else:
        script += f"Being {age_num} carries a uniquely heavy burden. You are standing on the edge of adulthood, and suddenly it feels like every decision you make has massive consequences for your future. The expectations from your family, your teachers, and yourself can feel like a heavy weight pressing down on your chest. You are handling an immense amount of pressure as you prepare for the next chapter of your life, but right now, in this exact moment, you don't need to figure any of it out. The future can wait. "

    script += "Let's begin by relaxing your physical body. Notice the top of your head, and let any tension there melt away. Relax your forehead, unfurrow your brow, and let your jaw drop slightly. Let this wave of relaxation travel down your neck, releasing the tight muscles in your shoulders. Let your arms become heavy and relaxed, all the way down to your fingertips. Notice the gentle rise and fall of your chest. Relax your stomach, your back, your legs, all the way down to your toes. You are completely supported by the surface beneath you. "

    if context == "exam soon":
        script += "I know you have an important exam coming up. Your mind might be racing with facts, dates, formulas, and a lingering fear that you haven't done enough. Notice where you are holding that anxiety in your body—maybe a tightness in your chest, or a knot in your stomach—and on your next exhale, intentionally let it go. An exam is just a single piece of paper on a single day. It does not define your worth, your intelligence, or your future. For now, let go of the studying. You have prepared, and when the time comes, you will simply do your best. That is all anyone can ask of you. "
    elif context == "big project":
        script += "You have a massive project weighing heavily on your mind. When we look at a mountain of work, it is easy to feel paralyzed by perfectionism or completely drained of creative energy. You might be feeling the guilt of taking a break right now, but let me assure you: resting is a crucial part of the creative process. Let's take a conscious step back from the planning, the drafting, and the execution. You don't need to produce anything right now. Just allow yourself to exist separately from your work. When you return to it later, your mind will be sharper and your energy restored. "
    else:
        script += "The daily grind of studying, homework, and looking at screens can blur the lines between your personal time and your academic life. It might feel like you should always be doing something productive. But a machine cannot run continuously without breaking down, and neither can you. Whatever reading or assignments you have left to do today, they can wait. The books and the notifications will still be there later. These next few minutes are a strict boundary you have set for yourself—a safe space where your only job is to recharge your mind and restore your nervous system. "

    if style == "motivational":
        script += "As you rest here, remind yourself of the incredible resilience you possess. You have faced difficult weeks before, you have navigated stress before, and you have survived 100 percent of your bad days. You have put in the work, and you are capable of truly amazing things. Do not let temporary fatigue convince you that you are not strong enough. You have a deep well of potential inside of you. Visualize yourself walking into your next challenge with your head held high, radiating quiet confidence and clarity. "
    elif style == "concentration":
        script += "As we continue, let's practice bringing our focus entirely to the present moment. Your mind will naturally want to wander to past conversations or future worries. When it does, do not be frustrated. Simply notice the thought, imagine it placing it on a leaf floating down a gentle stream, and watch it drift away. Gently guide your spotlight of attention back to the sound of my voice, and the physical sensation of the air moving in and out of your body. Train your mind to stay anchored right here, in the stillness of the present. "
    else:
        script += "For the rest of this practice, give yourself radical permission to just relax. Wrap yourself in a heavy, comforting blanket of peace. Imagine a soft, warm light surrounding your body, shielding you from the demands of the outside world. Within this space, there is no rush, there are no deadlines, and there is no pressure to perform. You are safe, you are grounded, and you are allowed to simply rest. "

    script += "Now, let's transition into a period of deep, restorative breathing to anchor this feeling of calm. "
    
    try:
        minutes = int(length)
    except ValueError:
        minutes = 5
        
    breathing_prompts = [
        "Breathe in deeply through your nose, filling your lungs entirely... hold it at the top... and exhale slowly and audibly through your mouth, letting all the stale air out. ",
        "With your next inhale, imagine drawing in a bright, clearing energy... and with your exhale, push out any lingering stress, doubt, or physical tension. ",
        "Notice the cool air entering your nostrils, and the warm air leaving. Keep your focus strictly on this subtle, physical sensation. ",
        "Inhale, expanding your belly outward like a balloon... hold the breath for just a moment... and release, letting your body sink even deeper into complete relaxation. ",
        "Allow your breath to find its own natural rhythm now. Don't force it to be deep or shallow. Just become a quiet observer of the gentle wave of your breathing. "
    ]
    
    # Loop the breathing text to pad the audio out
    loops = minutes * 2 
    for i in range(loops):
        script += breathing_prompts[i % len(breathing_prompts)]
        script += "Let your mind drift gently, remaining completely at peace. "

    script += "As we bring this meditation to a close, slowly bring your awareness back to the physical room around you. Notice the feeling of the air on your skin and the sounds in the distance. Gently wiggle your fingers and your toes, waking your body back up. Take one last, deep, energizing breath in... and let it out. When you are ready, gently open your eyes. You have everything you need to face the rest of your day. You've got this."
    
    return script

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        age = request.form.get('age')
        mood = request.form.get('mood')
        context = request.form.get('context')
        style = request.form.get('style')
        length = request.form.get('length')
        
        if not all([age, mood, context, style, length]):
            return render_template('index.html', error="Oops! Please make sure all fields are selected.")

        custom_script = generate_script(age, mood, context, style, length)
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join('static', 'audio', filename)
        
        try:
            print("Generating audio... please wait...")
            tts = gTTS(text=custom_script, lang='en', slow=False)
            tts.save(filepath)
            print("Audio saved successfully!")
            
            log_request(age, mood, context, style, length, filepath)
            
            return render_template('result.html', audio_file=filename)
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return render_template('index.html', error="Sorry, we had trouble generating the audio. Please check your internet connection and try again.")
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)