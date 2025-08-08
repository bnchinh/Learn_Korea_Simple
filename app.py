import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageFilter
import base64
from io import BytesIO

# ===============================
# Helper functions
# ===============================
def set_background(image_path):
    """Set a blurred background image for the Streamlit app."""
    try:
        img = Image.open(image_path)
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))
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
        st.warning(f"{image_path} not found. Skipping background.")

def img_to_base64(img):
    """Convert a PIL image to base64."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ===============================
# Load Excel files
# ===============================
vocab_path = "vocab_modified.xlsx"
numbers_path = "numbers.xlsx"

try:
    vocab_df = pd.read_excel(vocab_path, header=None, engine='openpyxl')
    vocab_df.columns = ["Vietnamese", "Korean", "Chapter"]
    if len(vocab_df) < 1:
        st.error("Vocab file has no entries!")
        st.stop()
except FileNotFoundError:
    st.error(f"{vocab_path} not found!")
    st.stop()
except Exception as e:
    st.error(f"Error loading {vocab_path}: {str(e)}")
    st.stop()

try:
    numbers_df = pd.read_excel(numbers_path, header=None, engine='openpyxl')
    numbers_df.columns = ["Vietnamese", "Korean"]
    if len(numbers_df) < 10:
        st.error("Numbers file must have at least 10 entries!")
        st.stop()
except FileNotFoundError:
    st.error(f"{numbers_path} not found!")
    st.stop()
except Exception as e:
    st.error(f"Error loading {numbers_path}: {str(e)}")
    st.stop()

# ===============================
# Session state init
# ===============================
if 'page' not in st.session_state:
    st.session_state.page = 0
    st.session_state.user_inputs = []
    st.session_state.vietnamese = None
    st.session_state.korean_correct = None
    st.session_state.total_pages = 0

words_per_page = 10

st.title("Korean Vocab Learner")

# ===============================
# Welcome Page
# ===============================
if st.session_state.page == 0:
    set_background("image.jpg")
    st.markdown(
        """
        <div style="border: 2px solid green; padding: 20px; background-color: rgba(255, 255, 255, 0.7); border-radius: 10px; text-align: center; color: black;">
            <p>Welcome! This app quizzes you on all Vietnamese-Korean pairs from your file, plus 10 random numbers at the end. You'll see 10 items per page.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Start Quiz"):
        # Randomly choose 10 numbers
        numbers_sample = numbers_df.sample(n=10, random_state=None)

        # Combine all vocab + 10 random numbers
        full_set = pd.concat([vocab_df, numbers_sample], ignore_index=True)

        # Save into session
        st.session_state.vietnamese = full_set["Vietnamese"].tolist()
        st.session_state.korean_correct = full_set["Korean"].tolist()
        st.session_state.user_inputs = [""] * len(st.session_state.vietnamese)

        # Set total pages dynamically
        total_items = len(st.session_state.vietnamese)
        st.session_state.total_pages = (total_items + words_per_page - 1) // words_per_page

        st.session_state.page = 1
        st.rerun()

# ===============================
# Quiz Pages
# ===============================
else:
    if st.session_state.vietnamese is None:
        st.error("Quiz not started. Return to welcome page.")
        st.stop()

    vietnamese = st.session_state.vietnamese
    korean_correct = st.session_state.korean_correct
    total_items = len(vietnamese)
    total_pages = st.session_state.total_pages

    st.subheader(f"Page {st.session_state.page} of {total_pages}")
    start_idx = (st.session_state.page - 1) * words_per_page
    end_idx = min(start_idx + words_per_page, total_items)

    with st.form(key=f"quiz_form_{st.session_state.page}"):
        for i in range(start_idx, end_idx):
            st.write(f"{i + 1}. {vietnamese[i]}")
            st.session_state.user_inputs[i] = st.text_input(
                f"Enter Korean for {vietnamese[i]}",
                value=st.session_state.user_inputs[i],
                key=f"input_{i}",
            )

        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            previous = st.form_submit_button("Previous") if st.session_state.page > 1 else False
        with col2:
            next_btn = st.form_submit_button("Next") if st.session_state.page < total_pages else False
        with col3:
            submit = st.form_submit_button("Submit and Score") if st.session_state.page == total_pages else False

    # Navigation logic
    if previous:
        st.session_state.page -= 1
        st.rerun()
    elif next_btn:
        st.session_state.page += 1
        st.rerun()
    elif submit:
        score = 0
        feedback = []
        for i in range(total_items):
            user_input = st.session_state.user_inputs[i].strip().lower()
            correct = str(korean_correct[i]).strip().lower()
            corrects = [c.strip() for c in correct.split(",")]
            if user_input in corrects:
                score += 1
            elif user_input:
                feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You entered: '{st.session_state.user_inputs[i]}')")
            else:
                feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You left it blank)")

        percentage = (score / total_items) * 100
        st.success(f"Your score: {score}/{total_items} ({percentage:.2f}%)")

        if feedback:
            st.subheader("Feedback on incorrect/blank ones:")
            with st.expander("See details (scrollable)"):
                for item in feedback:
                    st.write(item)
        else:
            st.success("Perfect! All correct.")

        if st.button("Restart Quiz"):
            st.session_state.clear()
            st.rerun()
