# AI Dog Matchmaker 🐕

Welcome to the **AI Dog Matchmaker**! This project was built for the Smart Robotics Hackathon to help users find their perfect robotic (or real-world!) dog companion based on their lifestyle and personality.

## Features 🚀
- **Conversational UI**: Uses Google's Gemini LLM to naturally ask users questions and extract their preferences (activity level, kids, allergies, etc.).
- **Data-Driven Matching**: Maps the extracted JSON preferences to a curated dataset of dog breeds and calculates a weighted similarity score to find the Top 3 matches.
- **Image Integration**: Displays high-quality images of the matched dog breeds.
- **Social Media Generation**: Automatically generates a fun, shareable social media post for the #1 match using AI.

## How to Run 🛠️

1. **Prerequisites**: Make sure you have Python installed.
2. **Install Dependencies**:
   Open a terminal in this directory and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```
4. **API Key**: 
   When the app opens in your browser, paste your [Google Gemini API Key](https://aistudio.google.com/) into the sidebar to start the conversation!

## Judging Criteria Addressed 🏆
- **Creativity & Functionality**: The chatbot drives the conversation naturally, doesn't overwhelm the user, and robustly handles incomplete information by asking follow-up questions until 5 core traits are identified.
- **Data Use & Insight**: We use a weighted scoring algorithm (+2 for critical traits like Kid-friendly and Hypoallergenic, +1 for lifestyle fits like Size and Activity).
- **Presentation & Storytelling**: A clean Streamlit UI with clear trait breakdowns, images, and an auto-generated viral social media post!
