import streamlit as st
import PyPDF2
import docx2txt
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="MindMint | Smart Summarizer", page_icon="🧠")

st.title("🧠 MindMint – Smart AI Summarizer")
st.write(
    "Upload any document and get an accurate, human-like summary powered by GPT."
)

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
    CHUNK_SIZE = 2000
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    partial_summaries = []

    for chunk in chunks[:5]:  # limit to first 5 chunks (safe for free tier)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic summarizer."
                },
                {
                    "role": "user",
                    "content": f"Summarize this content briefly:\n\n{chunk}"
                }
            ],
            max_tokens=200
        )

        partial_summaries.append(response.choices[0].message.content)

    # Final combined summary
    final_summary = "\n\n".join(partial_summaries)
    return final_summary


uploaded_file = st.file_uploader(
    "Upload a file (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if text and text.strip():
        try:
            with st.spinner("Generating summary with GPT..."):
                summary = summarize_with_gpt(text)

            st.success("✅ Summary generated")
            st.write(summary)

        except Exception:
            st.error(
                "⚠️ The document is too large or the API limit "
                "was reached. Please try a smaller file."
            )
    else:
        st.error("❌ Could not extract text from the file.")
