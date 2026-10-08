import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# Set page config
st.set_page_config(page_title="🐶 AI Dog Matchmaker", page_icon="🐕", layout="centered")

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("breeds.csv")

df = load_data()

# Sidebar for API Key
with st.sidebar:
    st.title("⚙️ Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    st.markdown("### 👨‍💻 About the Project")
    st.markdown("Created by **Hammad** as a personal project to explore Generative AI and logic-based matchmaking.")
    st.markdown("---")
    st.markdown("**Tech Stack**:")
    st.markdown("- **Frontend**: Streamlit")
    st.markdown("- **AI Brain**: Gemini 3.5 Flash")
    st.markdown("- **Logic**: Python & Pandas")
    st.markdown("---")
    st.markdown("**Features**:")
    st.markdown("💬 Conversational Flow")
    st.markdown("🧠 Data-Driven Matching")

# Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferences" not in st.session_state:
    st.session_state.preferences = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "social_post" not in st.session_state:
    st.session_state.social_post = None

SYSTEM_PROMPT = """
You are the "Dog Matchmaker", a playful, friendly, and enthusiastic AI assistant.
Your goal is to recommend the best real-world dog breeds based on the user's lifestyle and personality.

You need to organically extract the following 5 preferences from the user:
1. Activity level (Low, Medium, or High)
2. Living space size (Small, Medium, or Large)
3. Good with Kids (Yes or No)
4. Hypoallergenic (Yes or No)
5. Time for training (Low, Medium, or High)

Ask 1 or 2 conversational, friendly questions at a time. Do not interrogate them, make it a natural chat! 
Acknowledge their answers playfully.

CRITICAL INSTRUCTION:
ONCE you have gathered all 5 preferences, you MUST stop asking questions and output a summary of the preferences in this EXACT JSON format enclosed in markdown code blocks:

```json
{
  "activity_level": "High",
  "size": "Large",
  "kids": "Yes",
  "hypoallergenic": "No",
  "training": "High"
}
```

Do not output the JSON until you have all 5 pieces of information.
"""

def parse_preferences(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None

def compute_matches(prefs, df):
    # Clean up preferences to match dataset format
    def safe_get(key, default=""):
        val = prefs.get(key, default)
        return str(val).strip().lower() if val else ""

    activity = safe_get('activity_level')
    size = safe_get('size')
    kids = safe_get('kids')
    hypo = safe_get('hypoallergenic')
    training = safe_get('training')

    def score_row(row):
        score = 0
        if row['Activity Level'].lower() == activity: score += 1
        if row['Size'].lower() == size: score += 1
        if row['Good with Kids'].lower() == kids: score += 2 # Weighted higher
        if row['Hypoallergenic'].lower() == hypo: score += 2 # Weighted higher
        if row['Trainability'].lower() == training: score += 1
        return score
    
    df['Match Score'] = df.apply(score_row, axis=1)
    return df.sort_values(by='Match Score', ascending=False).head(3)

st.title("🐶 AI Dog Matchmaker")
st.markdown("Chat with our AI to find your perfect furry companion! We'll ask you a few questions about your lifestyle and match you with the top 3 dog breeds.")

if not api_key:
    st.warning("👈 Please enter your Gemini API Key in the sidebar to start.")
    st.stop()

# Configure GenAI
genai.configure(api_key=api_key)

# Initialize Chat Session
if st.session_state.chat_session is None:
    model = genai.GenerativeModel('gemini-3.5-flash')
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [SYSTEM_PROMPT]},
        {"role": "model", "parts": ["Understood! I am ready to be the Dog Matchmaker."]}
    ])
    # Kick off the conversation
    response = st.session_state.chat_session.send_message("Hello! I'm ready to find a dog.")
    st.session_state.messages.append({"role": "assistant", "content": response.text})

# Display Chat History (hide JSON if it exists)
for message in st.session_state.messages:
    # Don't show the raw JSON block to the user
    display_text = re.sub(r'```json\s*(\{.*?\})\s*```', '*(Computing your matches...)*', message["content"], flags=re.DOTALL)
    if display_text.strip():
        with st.chat_message(message["role"]):
            st.markdown(display_text)

# Chat Input & Logic
if st.session_state.preferences is None:
    if prompt := st.chat_input("Type your answer here..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text
                
                # Check if JSON is in the response
                prefs = parse_preferences(full_response)
                
                if prefs:
                    st.markdown("*(Computing your matches...)*")
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.session_state.preferences = prefs
                    st.rerun()
                else:
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Results Display
if st.session_state.preferences is not None:
    st.markdown("---")
    st.header("🏆 Your Perfect Matches")
    
    top_matches = compute_matches(st.session_state.preferences, df)
    
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_matches.iterrows()):
        with cols[i]:
            st.image(row['Image URL'], use_container_width=True)
            st.subheader(f"#{i+1} {row['Breed']}")
            st.write(f"**Score**: {row['Match Score']}/7")
            st.caption(row['Description'])
            with st.expander("Trait Breakdown"):
                st.write(f"- **Size**: {row['Size']}")
                st.write(f"- **Activity**: {row['Activity Level']}")
                st.write(f"- **Kids**: {row['Good with Kids']}")
                st.write(f"- **Hypoallergenic**: {row['Hypoallergenic']}")
                st.write(f"- **Trainability**: {row['Trainability']}")
                
    st.markdown("---")
    st.subheader("📱 Social Media Post for your #1 Match")
    
    # Generate Social Post
    if st.session_state.social_post is None:
        with st.spinner("Generating viral social post..."):
            top_breed = top_matches.iloc[0]['Breed']
            model = genai.GenerativeModel('gemini-3.5-flash')
            post_prompt = f"Write a short, engaging, and playful social media post (with emojis and hashtags) announcing that I just matched with a {top_breed} as my perfect furry companion using the AI Dog Matchmaker! Keep it under 280 characters."
            post_response = model.generate_content(post_prompt)
            st.session_state.social_post = post_response.text
            
    st.info(st.session_state.social_post)
    
    if st.button("Start Over"):
        st.session_state.messages = []
        st.session_state.preferences = None
        st.session_state.chat_session = None
        st.session_state.social_post = None
        st.rerun()
