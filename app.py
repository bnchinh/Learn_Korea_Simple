import streamlit as st
import pandas as pd
from PIL import Image, ImageFilter
import base64
from io import BytesIO

# ===============================
# Helper functions
# ===============================
def set_background(image_path):
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
    st.session_state.vietnamese = []
    st.session_state.korean_correct = []
    st.session_state.chapters = []
    st.session_state.total_pages = 0
    st.session_state.chapter_page_ends = []  # page indices where chapters end
    st.session_state.current_chapter = None  # currently finished chapter to show score

words_per_page = 10
st.title("Korean Vocab Learner")

# ===============================
# Prepare data grouped by chapter
# ===============================
def prepare_quiz_data():
    # Convert Chapter to str
    vocab_df["Chapter"] = vocab_df["Chapter"].astype(str)

    def chapter_sort_key(ch):
        try:
            return (0, int(ch))
        except:
            return (1, ch)

    # Sort vocab by Chapter numerically where possible, others last
    vocab_sorted = vocab_df.sort_values(
        by=["Chapter"],
        key=lambda col: col.map(chapter_sort_key)
    ).reset_index(drop=True)

    # Append Numbers chapter at the end
    numbers_sample = numbers_df.sample(n=10, random_state=None).copy()
    numbers_sample["Chapter"] = "Numbers"

    full_df = pd.concat([vocab_sorted, numbers_sample], ignore_index=True)

    # Flatten columns to lists
    vietnamese = full_df["Vietnamese"].tolist()
    korean = full_df["Korean"].tolist()
    chapters = full_df["Chapter"].tolist()

    # Calculate page ends for chapters to detect when chapter ends
    chapter_page_ends = []
    current_page = 1
    words_in_current_page = 0
    last_chapter = chapters[0]
    for i, ch in enumerate(chapters):
        words_in_current_page += 1
        # If chapter changed or page full, increment page
        if ch != last_chapter or words_in_current_page > words_per_page:
            if ch != last_chapter:
                chapter_page_ends.append(current_page)
                last_chapter = ch
                words_in_current_page = 1
            else:
                current_page += 1
                words_in_current_page = 1

    chapter_page_ends.append(current_page)
    total_pages = current_page

    return vietnamese, korean, chapters, chapter_page_ends, total_pages


# ===============================
# Welcome page
# ===============================
if st.session_state.page == 0:
    set_background("image.jpg")
    st.markdown(
        """
        <div style="border: 2px solid green; padding: 20px; background-color: rgba(255, 255, 255, 0.7); border-radius: 10px; text-align: center; color: black;">
            <p>Welcome! This app quizzes you chapter-by-chapter on all Vietnamese-Korean pairs from your file, plus 10 random numbers at the end. You'll see 10 items per page. After finishing each chapter, you'll get immediate feedback!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Start Quiz"):
        vocab, korean, chapters, chapter_page_ends, total_pages = prepare_quiz_data()
        st.session_state.vietnamese = vocab
        st.session_state.korean_correct = korean
        st.session_state.chapters = chapters
        st.session_state.chapter_page_ends = chapter_page_ends
        st.session_state.total_pages = total_pages
        st.session_state.user_inputs = [""] * len(vocab)
        st.session_state.page = 1
        st.session_state.current_chapter = None
        st.rerun()

# ===============================
# Quiz pages
# ===============================
else:
    vietnamese = st.session_state.vietnamese
    korean_correct = st.session_state.korean_correct
    chapters = st.session_state.chapters
    chapter_page_ends = st.session_state.chapter_page_ends
    total_pages = st.session_state.total_pages
    user_inputs = st.session_state.user_inputs
    current_page = st.session_state.page

    st.subheader(f"Page {current_page} of {total_pages}")

    start_idx = (current_page - 1) * words_per_page
    end_idx = min(start_idx + words_per_page, len(vietnamese))

    with st.form(key=f"quiz_form_{current_page}"):
        for i in range(start_idx, end_idx):
            st.write(f"{i + 1}. {vietnamese[i]}")
            user_inputs[i] = st.text_input(
                f"Enter Korean for {vietnamese[i]}",
                value=user_inputs[i],
                key=f"input_{i}",
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            previous = st.form_submit_button("Previous") if current_page > 1 else False
        with col2:
            next_btn = st.form_submit_button("Next") if current_page < total_pages else False
        with col3:
            submit = st.form_submit_button("Submit and Score") if current_page == total_pages else False

    if previous:
        st.session_state.page -= 1
        st.rerun()
    elif next_btn:
        st.session_state.page += 1
        st.rerun()
    elif submit:
        # Final submission - show total score
        total_items = len(vietnamese)
        score = 0
        feedback = []

        for i in range(total_items):
            user_input = user_inputs[i].strip().lower()
            correct = str(korean_correct[i]).strip().lower()
            corrects = [c.strip() for c in correct.split(",")]
            if user_input in corrects:
                score += 1
            elif user_input:
                feedback.append(f"{vietnamese[i]} (Chapter {chapters[i]}): Correct is '{korean_correct[i]}' (You entered: '{user_inputs[i]}')")
            else:
                feedback.append(f"{vietnamese[i]} (Chapter {chapters[i]}): Correct is '{korean_correct[i]}' (You left it blank)")

        percentage = (score / total_items) * 100
        st.success(f"Your total score: {score}/{total_items} ({percentage:.2f}%)")

        if feedback:
            st.subheader("Feedback on incorrect/blank answers:")
            with st.expander("See details"):
                for f in feedback:
                    st.write(f)
        else:
            st.success("Perfect! All correct!")

        if st.button("Restart Quiz"):
            st.session_state.clear()
            st.rerun()

    else:
        # Check if current page is last page of a chapter
        if current_page in chapter_page_ends:
            # Identify which chapter just finished
            idx_last_word = end_idx - 1
            finished_chapter = chapters[idx_last_word]
            st.session_state.current_chapter = finished_chapter

            # Calculate chapter score
            ch_indices = [i for i, ch in enumerate(chapters) if ch == finished_chapter]
            ch_score = 0
            ch_feedback = []
            for i in ch_indices:
                user_input = user_inputs[i].strip().lower()
                correct = str(korean_correct[i]).strip().lower()
                corrects = [c.strip() for c in correct.split(",")]
                if user_input in corrects:
                    ch_score += 1
                elif user_input:
                    ch_feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You entered: '{user_inputs[i]}')")
                else:
                    ch_feedback.append(f"{vietnamese[i]}: Correct is '{korean_correct[i]}' (You left it blank)")

            ch_total = len(ch_indices)
            ch_percent = (ch_score / ch_total) * 100

            st.info(f"**You finished Chapter '{finished_chapter}'!**")
            st.success(f"Score: {ch_score}/{ch_total} ({ch_percent:.2f}%)")

            if ch_feedback:
                with st.expander(f"Feedback for Chapter '{finished_chapter}' (incorrect/blank)"):
                    for f in ch_feedback:
                        st.write(f)
