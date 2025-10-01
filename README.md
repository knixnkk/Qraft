Flashcard generator using Gemini or local fallback

Setup

- Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Optionally set `GOOGLE_API_KEY` in your environment to enable Gemini Files + model usage.

Run

```bash
export FLASK_APP=app.py
flask run
```

Usage

- Open `http://127.0.0.1:5000/` and upload a PDF or text file. If no `GOOGLE_API_KEY` is set, the app will create placeholder questions.
