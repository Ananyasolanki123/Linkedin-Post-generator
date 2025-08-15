import streamlit as st
import streamlit.components.v1 as components
import json
from fewshots import FewShotPosts
from post_generator import generate_post_from_sheet, generate_analytics_feedback
from fetch_url import fetch_latest_form_data
from llm_helper import llm
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSehElyFaX904bv3Ch7IFZnHoFTFFfNY-ikFoMa1fkESmad81w/viewform?usp=preview"  # Replace with your Google Form link


# --- Utility ---
def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
def render_two_cards(post_text, feedback_text):
    st.markdown("""
        <style>
        .page-wrap {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .cards-container {
            display: flex;
            justify-content: center;
            align-items: stretch;
            width: 80%;
            max-width: 1200px;
            gap: 30px;
        }
        .card {
            border: 1px solid rgba(79, 195, 247, 0.4); /* Soft blue border */
            border-radius: 16px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
            padding: 20px;
            width: 50%;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            position: relative;
        }
       
        .card-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            color: #4FC3F7;
        }
        .card-body {
            flex-grow: 1;
            overflow-y: auto;
            font-size: 16px;
            line-height: 1.6;
        }
     
        </style>

       
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="page-wrap">
            <div class="cards-container">
                <div class="card">
                    <div class="card-title">Generated LinkedIn Post</div>
                    <div class="card-body">{post_text}</div>
                </div>
                <div class="card">
                    <div class="card-title">AI Tips</div>
                    <div class="card-body">{feedback_text}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
def render_cards(feedback_text):
    st.markdown("""
        <style>
        .page-wrap {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .cards-container {
            display: flex;
            justify-content: center;
            align-items: stretch;
            width: 80%;
            max-width: 1200px;
        }
        .card {
            border: 1px solid rgba(79, 195, 247, 0.4); /* Soft blue border */
            border-radius: 16px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
            padding: 20px;
            width: 50%;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            position: relative;
        }
       
        .card-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            color: #4FC3F7;
        }
        .card-body {
            flex-grow: 1;
            overflow-y: auto;
            font-size: 16px;
            line-height: 1.6;
        }
     
        </style>

       
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="page-wrap">
            <div class="cards-container">
                <div class="card">
                    <div class="card-title">AI Tips</div>
                    <div class="card-body">{feedback_text}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)





def main():
            
    st.set_page_config(page_title="LinkedIn Post Generator", page_icon="📢", layout="wide")

        # Custom CSS for title styling
    st.markdown("""
    <style>
    @keyframes glow {
        0% { text-shadow: 0 0 5px #5EF2E9, 0 0 10px #5EF2E9, 0 0 20px #5EF2E9; }
        50% { text-shadow: 0 0 15px #5EF2E9, 0 0 25px #5EF2E9, 0 0 35px #5EF2E9; }
        100% { text-shadow: 0 0 5px #5EF2E9, 0 0 10px #5EF2E9, 0 0 20px #5EF2E9; }
    }
    .title {
        font-size: 42px;
        font-weight: bold;
        color: #6FFFE9;
        text-align: center;
        padding-bottom: 10px;
        border-bottom: 2px solid #6FFFE9;
        letter-spacing: 3px;
        animation: glow 2s ease-in-out infinite;
    }
    </style>
""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    .email {
        font-size: 30px;
        margin-top:20px;
        color: #6EE7F5; /* Lighter cyan */
        font-weight: 600; /* Slightly less bold */
        text-align: left;
        padding-bottom: 10px;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)

    # Render the styled title
    st.markdown('<div class="title">LinkedIn Post Generator</div>', unsafe_allow_html=True)

    st.write("Generate, review, and enhance LinkedIn posts with actionable AI feedback.")

    fs = FewShotPosts()


    st.markdown('<div class="email">Enter Your Email</div>', unsafe_allow_html=True)
    user_email = st.text_input("Your Gmail address (used in the form):", placeholder="example@gmail.com")

  

    all_form_data = fetch_latest_form_data()
    form_data = [
        row for row in all_form_data
        if row.get("Email Address") == user_email or row.get("Email Address_2") == user_email
    ]
    if not form_data:
        st.error("⚠ No submissions found for this email.")

        st.markdown(
            f"""
            Please fill out the form below to proceed:  
            👉 [**Fill the Google Form**]({FORM_URL})  
            """,
            unsafe_allow_html=True
        )

        if st.button("🔄 Refresh Data"):
            st.rerun()

        return

    st.markdown('<div class="email">Select Your Submission</div>', unsafe_allow_html=True)
    submission_labels = [
        f"{row.get('Full Name') or row.get('Full Name_2', 'N/A')} - {row.get('Post Type', 'N/A')}"
        for row in form_data
    ]
    selected_label = st.selectbox("Choose a form submission to work with:", options=submission_labels)
    selected_index = submission_labels.index(selected_label)
    selected_data = form_data[selected_index]
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        width:200px;
        height:50px;
        background-color: #6FFFE9; /* Soft cyan */
        color: black; /* Text color */
        font-weight: bold;
        border-radius: 8px;
        border: 1px solid #4FC3F7;
        padding: 0.6em 1em;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #4FC3F7; /* Darker cyan on hover */
        color: white;
        border-color: #6FFFE9;
    }
    </style>
    """, unsafe_allow_html=True)



    if st.button("Generate LinkedIn Post"):
        post = generate_post_from_sheet(selected_data)
        st.success("✅ LinkedIn Post Generated!")

        feedback_prompt = f"""
        You are a LinkedIn post coach.
        Here is a generated LinkedIn post:

        {post}

        Analyze it and give 3 short, actionable tips that how to present this post so reach increases or increase scalability of project or user's work.
        Keep it under 30 words, simple for beginners, and specific to the topic.
        """
        feedback = llm.invoke(feedback_prompt).content

        render_two_cards(post_text=post, feedback_text=feedback)
       


    send_pred = (
        selected_data.get("Send Engagement Prediction?") or
        selected_data.get("Send Engagement Prediction?_2") or
        selected_data.get("Send Engagement Prediction?_3") or
        selected_data.get("Send Engagement Prediction?_4")
    )

    if st.button("Generate Feedback"):
        if send_pred == "Yes":
            impressions = safe_int(selected_data.get("Impressions") or selected_data.get("Impressions_2"))
            reactions = safe_int(selected_data.get("Reactions") or selected_data.get("Reactions_2"))
            comments = safe_int(selected_data.get("Comments") or selected_data.get("Comments_2"))
            shares = safe_int(selected_data.get("Shares") or selected_data.get("Shares_2"))

            analytics_fb = generate_analytics_feedback(impressions, reactions, comments, shares)
            st.success("✅ Analytics Feedback Generated")

            render_cards(feedback_text=analytics_fb)
        else:
            st.info("ℹ This submission did not request engagement prediction, so no analytics feedback is available.")

if __name__ == "__main__":
    main()
