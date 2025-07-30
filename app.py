import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageFilter
import base64
from io import BytesIO

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

# Load Excel directly
file_path = "vocab_modified.xlsx"
try:
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
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

# Random select 50
selected_indices = random.sample(range(len(df)), 50)
selected_vocab = df.iloc[selected_indices].reset_index(drop=True)
vietnamese = selected_vocab[0].tolist()
korean_correct = selected_vocab[1].tolist()

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 0
    st.session_state.user_inputs = [""] * 50

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
        st.session_state.page = 1
        st.rerun()

# Quiz pages
else:
    st.subheader(f"Page {st.session_state.page} of {total_pages}")
    start_idx = (st.session_state.page - 1) * words_per_page
    end_idx = start_idx + words_per_page

    for i in range(start_idx, end_idx):
        st.write(f"{i + 1}. {vietnamese[i]}")
        st.session_state.user_inputs[i] = st.text_input(
            f"Enter Korean for {vietnamese[i]}", value=st.session_state.user_inputs[i], key=f"input_{i}"
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.page > 1 and st.button("Previous"):
            st.session_state.page -= 1
            st.rerun()
    with col2:
        if st.session_state.page < total_pages:
            if st.button("Next"):
                st.session_state.page += 1
                st.rerun()
        else:
            if st.button("Submit and Score"):
                score = 0
                feedback = []
                for i in range(50):
                    user_input = st.session_state.user_inputs[i].strip().lower()
                    correct = str(korean_correct[i]).strip().lower()
                    if user_input == correct:
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
                    st.session_state.page = 0
                    st.session_state.user_inputs = [""] * 50
                    st.rerun()
