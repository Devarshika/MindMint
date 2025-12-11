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
st.info("📄 Large document detected. Summaries will be generated section-by-section.")

def summarize_with_gpt(text):
    # Split text into safe chunks
    CHUNK_SIZE = 2000  # Processable without rate-limit
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    summaries = []

    # Limit to first 8 chunks for now (16k chars) - safe for deployment
    for i, chunk in enumerate(chunks[:8], start=1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert academic summarizer. Summarize clearly and concisely."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this section:\n\n{chunk}"
                    }
                ],
                max_tokens=250
            )

            summaries.append(f"### Section {i} Summary\n" + response.choices[0].message.content)

        except Exception:
            summaries.append(f"### Section {i} Summary\n(Section skipped due to API limit.)")

    # Combine all section summaries
    combined = "\n\n".join(summaries)

    # Final overall summary
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert summarizer."},
            {
                "role": "user",
                "content": f"Create one final summary from these section summaries:\n\n{combined}"
            }
        ],
        max_tokens=300
    )

    return final_response.choices[0].message.content




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
