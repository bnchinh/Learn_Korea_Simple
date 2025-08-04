import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageFilter
import base64
from io import BytesIO
from random_words import pick_random_words

# Custom CSS for background image
def set_background(image_path):
    try:
        img = Image.open(image_path)
        # Apply blur
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))  # Adjust radius for more/less blur
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/png;base64,{img_to_base64(blurred_img)});
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("image.jpg not found. Skipping background.")

def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Load Excel directly (once)
vocab_path = "vocab_modified.xlsx"
try:
    df = pd.read_excel(vocab_path, header=None, engine='openpyxl')
    if len(df) < 50:
        st.error("File has fewer than 50 entries. Add more vocabulary!")
        st.stop()
except FileNotFoundError:
    st.error("vocab_modified.xlsx not found! Place it in the same folder or repo.")
    st.stop()
except ImportError:
    st.error("Missing dependency: Install openpyxl by adding it to requirements.txt.")
    st.stop()
except Exception as e:
    st.error(f"Error loading file: {str(e)}")
    st.stop()

numbers_path = "numbers.xlsx"
try:
    df = pd.read_excel(numbers_path, header=None, engine='openpyxl')
    if len(df) < 50:
        st.error("File has fewer than 100 entries. Add more numbers!")
        st.stop()
except FileNotFoundError:
    st.error("numbers.xlsx not found! Place it in the same folder or repo.")
    st.stop()
except ImportError:
    st.error("Missing dependency: Install openpyxl by adding it to requirements.txt.")
    st.stop()
except Exception as e:
    st.error(f"Error loading file: {str(e)}")
    st.stop()

# Session state setup
if 'page' not in st.session_state:
    st.session_state.page = 0
    st.session_state.user_inputs = [""] * 50
    st.session_state.vietnamese = None
    st.session_state.korean_correct = None

words_per_page = 10
total_pages = 50 // words_per_page

st.title("Korean Vocab Learner")

# Welcome page
if st.session_state.page == 0:
    set_background("image.jpg")  # Apply blurred hardcoded background
    # Styled welcome text with green border and black text
    st.markdown(
        """
        <div style="border: 2px solid green; padding: 20px; background-color: rgba(255, 255, 255, 0.7); border-radius: 10px; text-align: center; color: black;">
            <p>Welcome! This app quizzes you on 50 random Vietnamese-Korean pairs from your file. You'll see 10 words per page.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Start Quiz"):
        # Generate random 50 words ONLY here, before quiz starts
        selected_vocab = pick_random_words(vocab_path=vocab_path, numbers_path=numbers_path, n_vocab=40, n_numbers=10)
        st.session_state.vietnamese = selected_vocab["Vietnamese"].tolist()
        st.session_state.korean_correct = selected_vocab["Korean"].tolist()
        st.session_state.page = 1
        st.rerun()

# Quiz pages
else:
    if st.session_state.vietnamese is None:
        st.error("Quiz not started. Return to welcome page.")
        st.stop()

    vietnamese = st.session_state.vietnamese
    korean_correct = st.session_state.korean_correct

    st.subheader(f"Page {st.session_state.page} of {total_pages}")
    start_idx = (st.session_state.page - 1) * words_per_page
    end_idx = start_idx + words_per_page

    with st.form(key=f"quiz_form_{st.session_state.page}"):
        for i in range(start_idx, end_idx):
            st.write(f"{i + 1}. {vietnamese[i]}")
            st.session_state.user_inputs[i] = st.text_input(
                f"Enter Korean for {vietnamese[i]}",
                value=st.session_state.user_inputs[i],
                key=f"input_{i}",
            )

        # This is the crucial part:
        submitted = st.form_submit_button("Submit Answers")

        # Navigation and submit buttons inside form for batch saving
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.page > 1:
                previous = st.form_submit_button("Previous")
            else:
                previous = False
        with col2:
            if st.session_state.page < total_pages:
                next_btn = st.form_submit_button("Next")
            else:
                submit = st.form_submit_button("Submit and Score")
                next_btn = False
                previous = False  # No previous on submit

    # Handle button actions after form submission (saves inputs automatically via session state)
    if previous:
        st.session_state.page -= 1
        st.rerun()
    elif next_btn:
        st.session_state.page += 1
        st.rerun()
    elif 'submit' in locals() and submit:
        score = 0
        feedback = []
        for i in range(50):
            user_input = st.session_state.user_inputs[i].strip().lower()
            correct = str(korean_correct[i]).strip().lower()
            corrects = correct.split(sep=",")
            if user_input in corrects:
                score += 1
            elif user_input:
                feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You entered: '{st.session_state.user_inputs[i]}')")
            else:
                feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You left it blank)")

        percentage = (score / 50) * 100
        st.success(f"Your score: {score}/50 ({percentage:.2f}%)")
        if feedback:
            st.subheader("Feedback on incorrect/blank ones:")
            with st.expander("See details (scrollable)"):
                for item in feedback:
                    st.write(item)
        else:
            st.success("Perfect! All correct.")
        if st.button("Restart Quiz"):
            # Clear session state to allow new randomization on next start
            st.session_state.user_inputs = [""] * 50
            st.session_state.vietnamese = None
            st.session_state.korean_correct = None
            del st.session_state.page
            st.cache_resource.clear()
            st.rerun()
