import streamlit as st
import pandas as pd
import random
from PIL import Image  # For background image

# Custom CSS for background image (optional, to mimic your Tkinter welcome)
def set_background(image_file):
    img = Image.open(image_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{img_to_base64(img)});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def img_to_base64(img):
    from io import BytesIO
    import base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Load Excel
uploaded_vocab = st.file_uploader("Upload vocab_modified.xlsx", type="xlsx")
uploaded_bg = st.file_uploader("Upload background image (optional, for welcome)", type=["jpg", "png"])

if uploaded_vocab:
    df = pd.read_excel(uploaded_vocab, header=None)
    if len(df) < 50:
        st.error("File has fewer than 50 entries. Add more vocabulary!")
        st.stop()

    # Random select 50
    selected_indices = random.sample(range(len(df)), 50)
    selected_vocab = df.iloc[selected_indices].reset_index(drop=True)
    vietnamese = selected_vocab[0].tolist()
    korean_correct = selected_vocab[1].tolist()
else:
    st.error("Upload your Excel file to start.")
    st.stop()

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 0
    st.session_state.user_inputs = [""] * 50

words_per_page = 10
total_pages = 50 // words_per_page

st.title("Korean Vocab Learner")

# Welcome page
if st.session_state.page == 0:
    if uploaded_bg:
        set_background(uploaded_bg)  # Apply background
    st.write("Welcome! This app quizzes you on 50 random Vietnamese-Korean pairs from your file. You'll see 10 words per page.")
    st.write("Since you're in Gwangjin District, Seoul, try practicing these at local spots like Children's Grand Park—maybe count items in native Korean while walking!")
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
