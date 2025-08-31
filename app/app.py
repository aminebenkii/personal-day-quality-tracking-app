import streamlit as st
from datetime import datetime
from metrics import metrics
from save import save_to_google_sheets

st.set_page_config(page_title="Daily Reflection", layout="centered")
st.title("🧠 Daily Reflection Tracker")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.responses = {}
    st.session_state.gratitude = ""
    st.session_state.notes = ""

metric_keys = list(metrics.keys())
total_steps = len(metric_keys) + 1  

def next_step():
    if st.session_state.step < total_steps:
        st.session_state.step += 1

def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

# Slider steps
if st.session_state.step < len(metric_keys):
    key = metric_keys[st.session_state.step]
    data = metrics[key]

    st.header(data["label"])
    current_value = st.session_state.responses.get(key, 3)

    rating = st.slider(
        "Rate it:",
        min_value=1,
        max_value=5,
        key=f"{key}_slider",  # avoid conflict with response dict
        value=current_value
    )
    st.session_state.responses[key] = rating

    # Show the legend for the current rating (safe)
    st.markdown(f"**{data['legend'][rating]}**")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.step > 0:
            st.button("← Back", on_click=prev_step)
    with col2:
        st.button("Next →", on_click=next_step)

# Gratitude + Notes step
elif st.session_state.step == len(metric_keys):
    st.header("Gratitude & Notes")

    st.session_state.gratitude = st.text_input(
        "🙏 One thing I'm grateful for today",
        value=st.session_state.gratitude
    )
    st.session_state.notes = st.text_area(
        "📝 Notes about today",
        value=st.session_state.notes
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("← Back", on_click=prev_step)
    with col2:
        if st.button("✅ Save Entry"):
            today = datetime.now().strftime("%Y-%m-%d")
            entry = {
                "date": today,
                **st.session_state.responses,
                "gratitude": st.session_state.gratitude,
                "notes": st.session_state.notes
            }

            save_to_google_sheets(entry)
            st.success("Saved to Google Sheets! ✅")
            st.session_state.step += 1

# Final confirmation step
else:
    st.success("Reflection saved. See you tomorrow! 🙌")
    if st.button("🔁 Start Over"):
        st.session_state.step = 0
        st.session_state.responses = {}
        st.session_state.gratitude = ""
        st.session_state.notes = ""
