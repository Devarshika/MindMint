import streamlit as st
import PyPDF2
import docx2txt
import os
import groq

# Load Groq client
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="MindMint | Smart Summarizer", page_icon="🧠")

st.title("🧠 MindMint – Smart AI Summarizer")
st.write("Upload any document and get an accurate, human-like summary powered by LLaMA 3.1 (Free!).")

# ---------------------- TEXT EXTRACTION --------------------------
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


# ---------------------- SUMMARIZER --------------------------
def summarize_with_gpt(text):
    CHUNK_SIZE = 4000  # LLaMA handles 4k chars safely
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    summaries = []

    # Summarize each section
    for i, chunk in enumerate(chunks[:10], start=1):  # limit to 10 chunks max
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert academic summarizer."},
                    {"role": "user", "content": f"Summarize this section:\n\n{chunk}"}
                ],
                max_tokens=300
            )

            summaries.append(f"### Section {i} Summary\n" + response.choices[0].message.content)

        except Exception as e:
            summaries.append(f"### Section {i} Summary\n(Skipped due to error: {str(e)})")

    combined = "\n\n".join(summaries)

    # Final summary synthesis
    final = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert summarizer."},
            {"role": "user", "content": f"Create a final short summary of the following sections:\n\n{combined}"}
        ],
        max_tokens=250
    )

    return final.choices[0].message.content


# ---------------------- UI & EXECUTION --------------------------
uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if text and text.strip():
        try:
            st.info("📄 Large document handling enabled. Summarizing in sections...")

            with st.spinner("Generating summary..."):
                summary = summarize_with_gpt(text)

            st.success("✅ Summary generated")
            st.write(summary)

        except Exception as e:
            st.error("⚠️ An error occurred while summarizing. Details below:")
            st.error(str(e))

    else:
        st.error("❌ Could not extract text from the file.")
