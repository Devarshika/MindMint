import streamlit as st
import PyPDF2
import docx2txt
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="MindMint | Smart Summarizer", page_icon="🧠")

st.title("🧠 MindMint – Smart AI Summarizer")
st.write("Upload any document and get an accurate, human-like summary powered by GPT.")

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )

    elif file_name.endswith(".docx"):
        return docx2txt.process(uploaded_file)

    elif file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    else:
        return ""

def summarize_with_gpt(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert academic summarizer."},
            {"role": "user", "content": f"Summarize the following text clearly in under 200 words:\n\n{text}"}
        ]
    )
    return response.choices[0].message.content


uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if text.strip():
        with st.spinner("Generating summary with GPT..."):
            summary = summarize_with_gpt(text)

        st.success("✅ Summary generated")
        st.write(summary)
    else:
        st.error("❌ Could not extract text from the file.")
