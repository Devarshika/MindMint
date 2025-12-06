import streamlit as st
import PyPDF2
import docx2txt
import openai
import os

st.set_page_config(page_title="MindMint | Smart Summarizer", page_icon="🧠")

st.title("🧠 MindMint – Smart AI Summarizer")
st.write("Upload any document and get an accurate, human-like summary powered by GPT.")

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() for page in reader.pages)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        return ""

def summarize_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert summarizer."},
            {"role": "user", "content": f"Summarize the following text in under 200 words:\n\n{text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = docx2txt.process(uploaded_file)
    if text:
        with st.spinner("Generating summary with GPT..."):
            summary = summarize_with_gpt(text)
        st.success("Summary:")
        st.write(summary)
    else:
        st.error("Unable to read file.")
