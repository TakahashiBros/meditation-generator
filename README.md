# Meditation Generator – Take-Home Challenge

A lightweight Python web application that generates personalized, guided meditation scripts and converts them into downloadable audio files based on user inputs.

## 🌐 Live Demo
**Try it here:** `https://meditation-generator-2ws5.onrender.com`

*(Note: Deployed on Render's free tier. The first load may take up to 50 seconds if the instance has spun down due to inactivity. Due to ephemeral file storage on the free tier, generated audio files and CSV logs will reset when the server restarts).*

---

🧠 Engineering Decisions & Workarounds
  * LLM Integration vs. Stability: During development, I struggled to integrate Google's Gemini API. I encountered strict rate limits and "429 Quota Exceeded" errors on the free tier. To guarantee a 100% stable and reliable testing experience for the review team, I reverted to a robust, mathematically padded rule-based generation system.

  * Audio Mixing for UX: While gTTS is efficient, its delivery is robotic and lacks the emotional inflection needed for a true meditation guide. To mitigate this and elevate the user experience, I utilized pydub to dynamically calculate the duration of the generated voice track and overlay a looping ambient background track.

___

☁️ How I would run this on Google Cloud (Production)
To scale this MVP into a production-ready application, I would leverage the following Google Cloud architecture:

  * Compute (Cloud Run): I would containerize the Flask application using Docker and deploy it to Cloud Run. This provides a fully managed, serverless environment that auto-scales based on incoming web traffic.

  * Asset Storage (Cloud Storage): Instead of saving .mp3 files to a local static folder (which fails in stateless containers), the Python backend would write the generated audio directly to a Cloud Storage bucket and serve the public URLs from there.

  * Database & Logging (Cloud SQL): I would replace the local meditations_log.csv file with a managed Cloud SQL (PostgreSQL) database for robust, relational data storage.

  * Automation (Cloud Scheduler): I would use Cloud Scheduler to trigger a daily Cloud Run job or Cloud Function to automatically delete audio files older than 24 hours from Cloud Storage, preventing storage bloat.

  * TTS Engine & Security: I would upgrade gTTS to the official Google Cloud Text-to-Speech API (Journey Voices) for higher fidelity, neural voices. The required API credentials would be stored securely using Secret Manager.

___

⏱️ Timebox Notes & Future Improvements
This MVP was completed within the suggested ~6-hour timebox. Demonstrating the prioritization and efficiency required for a 10-hour/week role, I focused entirely on delivering a reliable core loop (web form → script → audio math → download). If I had more time, my next steps would be:

  * Paid LLM Integration: Re-introduce the Gemini API or OpenAI using a paid tier to bypass quota limits, combined with strict system prompts for true personalization.

  * Frontend Polish: Extract the inline CSS into a dedicated stylesheet or utilize a lightweight framework like Tailwind CSS for a more responsive UI.
