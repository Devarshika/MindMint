import streamlit as st
from PyPDF2 import PdfReader
import nltk
import openai

# Initialize NLTK
nltk.download('punkt')

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

# GPT-based summarizer
def summarize_text_gpt(text, depth="short"):
    depth_map = {"short": "a brief summary",
                 "medium": "a detailed summary",
                 "detailed": "a very detailed summary with key points"}
    prompt = f"Please provide {depth_map.get(depth,'a brief summary')} of the following text:\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=500
        )
        summary = response['choices'][0]['message']['content']
    except Exception as e:
        summary = f"Error generating summary: {e}"
    
    return summary

# Streamlit UI
st.set_page_config(page_title="MindMint AI", page_icon="🧠")
st.title("🧠 MindMint — AI Study Companion")

uploaded_file = st.file_uploader("Upload a PDF to summarize", type="pdf")

if uploaded_file:
    st.info("Extracting text...")
    text = extract_pdf_text(uploaded_file)
    
    st.info("Select summary depth:")
    depth = st.radio("Summary depth", ["short", "medium", "detailed"])
    
    if st.button("Generate Summary"):
        with st.spinner("Generating summary using GPT..."):
            summary = summarize_text_gpt(text, depth)
        st.success("Summary generated!")
        st.write(summary)
