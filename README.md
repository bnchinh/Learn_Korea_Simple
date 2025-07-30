# Korean Vocab Learner App

A simple web-based app to help you learn Korean vocabulary from a customized Excel file. Randomly selects 50 words for a quiz, with paginated inputs and scoring. Built with Streamlit for easy deployment and use—perfect for quick study sessions while exploring spots like Children's Grand Park in Gwangjin District, Seoul.

Live Demo: [https://learnkoreasimple.streamlit.app/](https://learnkoreasimple.streamlit.app/)

## Features

- **Random Vocabulary Selection**: Picks 50 unique Vietnamese-Korean pairs from your `vocab_modified.xlsx` file.
- **Paginated Quiz**: Displays 10 words per page with text inputs for Korean answers.
- **Scoring and Feedback**: Calculates score out of 50 with detailed feedback on mistakes or blanks.
- **Welcome Screen**: Blurred background image (`image.jpg`) with motivational text, styled with a green border and black text.
- **Stable Navigation**: Updates only on button clicks (Next, Previous, Submit); pressing Enter does nothing to avoid resets.
- **Restart Option**: Generates a new random set after scoring.


## Prerequisites

- Python 3.8+
- Dependencies: `streamlit`, `pandas`, `pillow`, `openpyxl`


## Installation (Local Setup)

1. Clone the repo or download the script:

```
git clone <your-repo-url>
cd <repo-folder>
```

2. Install dependencies:

```
pip install -r requirements.txt
```

(Create `requirements.txt` with the dependencies listed above if not present.)
3. Place `vocab_modified.xlsx` and `image.jpg` in the root folder.
4. Run the app:

```
streamlit run web_vocab_app.py
```

Open in your browser at `http://localhost:8501`.

## Usage

1. Open the app in your browser.
2. On the welcome screen, click "Start Quiz" to generate a random set of 50 words.
3. Enter Korean translations for each Vietnamese word (10 per page).
4. Use "Next" or "Previous" to navigate—inputs save on button click.
5. On the last page, click "Submit and Score" to see results.
6. Click "Restart Quiz" for a new set.

Great for practicing Sino-Korean and native Korean numbers (1-100) or general vocab while commuting in Seoul.

## Deployment

- Hosted on Streamlit Community Cloud: Deploy your own version by forking the repo and connecting to share.streamlit.io.
- For Hugging Face Spaces or similar: Upload the script, files, and `requirements.txt`; set as a Streamlit app.


## Technologies

- **Streamlit**: For the web interface and interactivity.
- **Pandas**: For loading and processing the Excel file.
- **Pillow**: For image blurring and base64 encoding.
- **Python Standard Libraries**: For randomization and I/O.

If you encounter issues (e.g., in Safari), clear your cache or test in another browser. Feel free to fork and customize for your Korean learning needs!

