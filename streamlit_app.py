import streamlit as st
from itertools import permutations

st.set_page_config(page_title="Color Towers", layout="centered")
st.title("Color Tower Combinations")

# Student Information
st.write("### Student Information")
roll_number = st.text_input("Roll Number")
nickname = st.text_input("Nickname")

# Use full color names
colors = ["", "Red", "Blue", "Green"]

st.write("**Instruction:** Select blocks to create towers using Red, Blue, and Green blocks (no repeats in a tower).")
st.image("rbg.png")

# Tower Inputs
tower_inputs = {}
cols = st.columns(6)
for i, col in enumerate(cols):
    with col:
        st.markdown(f"**Tower {i+1}**")
        tower_inputs[i] = []
        for block in range(3):
            tower_inputs[i].append(
                st.selectbox(
                    "Select",
                    colors,
                    key=f"tower{i}_block{block}",
                    label_visibility="collapsed"
                )
            )

# Questions
st.write("### Questions")

questions = {
    1: "How many different 3-block towers can you make out of these blocks?",
    2: "How many towers can you make if you cannot put the Blue block at the top?",
    3: "How many towers can you make if you cannot put the Blue and the Green block at the top?",
    4: "How many towers can you make if you cannot put the Red block in the middle?",
    5: "How many towers can you make if you cannot put the Red and the Green block in the middle?",
    6: "How many towers can you make if you cannot put the Green block at the bottom?"
}

correct_answers = {
    1: 6,
    2: 4,
    3: 2,
    4: 4,
    5: 2,
    6: 4
}

answers = {}
for qnum, question in questions.items():
    answers[qnum] = st.number_input(
        f"{qnum}. {question}",
        min_value=0,
        step=1,
        key=f"answer_{qnum}"
    )

# Check logic
if st.button("Check Towers and Answers"):

    valid_towers = list(permutations(["Red", "Blue", "Green"]))
    student_towers = []

    for i in range(6):
        tower = [
            st.session_state.get(f"tower{i}_block0", ""),
            st.session_state.get(f"tower{i}_block1", ""),
            st.session_state.get(f"tower{i}_block2", "")
        ]

        if (
            all(color in ["Red", "Blue", "Green"] for color in tower)
            and len(set(tower)) == 3
        ):
            student_towers.append(tuple(tower))

    unique_valid = set(student_towers) & set(valid_towers)

    towers_correct = len(unique_valid) == 6
    answers_correct = all(
        answers[q] == correct_answers[q]
        for q in correct_answers
    )

    st.session_state.all_correct = towers_correct and answers_correct

    if towers_correct and answers_correct:
        st.success("🎉 All towers and answers are correct!")
        st.balloons()

    elif towers_correct:
        st.warning("✅ Towers are correct, but some answers are not.")

    elif answers_correct:
        st.warning("✅ Answers are correct, but some towers are not.")

    else:
        st.error("❌ Some towers and answers are incorrect.")

# Submit button only appears after everything is correct
if st.session_state.get("all_correct", False):

    if st.button("Submit"):

        if nickname.strip() and roll_number.strip():

            import gspread
            from google.oauth2.service_account import Credentials
            import datetime

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            service_account_info = st.secrets["gcp_service_account"]

            creds = Credentials.from_service_account_info(
                service_account_info,
                scopes=scopes
            )

            client = gspread.authorize(creds)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                sheet = client.open("GCF").worksheet("Color Towers")
            except gspread.WorksheetNotFound:
                st.error("Worksheet 'Color Towers' not found.")
                st.stop()

            sheet.append_row([
                roll_number.strip(),
                nickname.strip(),
                timestamp
            ])

            st.success("✅ Submission successful!")

        else:
            st.warning("Please enter your roll number and nickname.")
