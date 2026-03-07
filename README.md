# Meditation Generator – Take-Home Challenge

A lightweight Python web application that generates personalized, guided meditation scripts and converts them into downloadable audio files based on user inputs.

## 🌐 Live Demo
**Try it here:** `https://meditation-generator-2ws5.onrender.com`

*(Note: Deployed on Render's free tier. The first load may take up to 50 seconds if the instance has spun down due to inactivity. Due to ephemeral file storage on the free tier, generated audio files and CSV logs will reset when the server restarts).*

---

☁️ How I would run this on Google Cloud (Production)
To scale this MVP into a production-ready application, I would leverage the following Google Cloud architecture:

* Compute (Cloud Run): I would containerize the Flask application using Docker and deploy it to Cloud Run. This provides a fully managed, serverless environment that auto-scales based on incoming web traffic.

* Asset Storage (Cloud Storage): Instead of saving .mp3 files to a local static folder (which fails in stateless containers), the Python backend would write the generated audio directly to a Cloud Storage bucket and serve the public URLs from there.

* Database & Logging (Cloud SQL): I would replace the local meditations_log.csv file with a managed Cloud SQL (PostgreSQL) database for robust, relational data storage.

* TTS Engine & Security: I would upgrade gTTS to the official Google Cloud Text-to-Speech API for higher fidelity voices. The required API credentials would be stored securely using Secret Manager.

___

⏱️ Timebox Notes & Future Improvements
This MVP was completed within the suggested ~6-hour timebox. Demonstrating the prioritization and efficiency required for a 10-hour/week role, I focused entirely on delivering a reliable core loop (web form → script → audio → download).

* If I had more time, my immediate next steps would be:

* LLM Integration: Replace the rule-based script generation with an LLM API combined with strict system prompts to generate truly dynamic, highly personalized scripts.

* Frontend Polish: Extract the inline CSS into a dedicated stylesheet or utilize a lightweight framework like Tailwind CSS for a more responsive UI.

* Automated Cleanup: Implement a background job or cron task to delete audio files older than 24 hours to prevent storage bloat.
