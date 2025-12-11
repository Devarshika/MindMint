import streamlit as st
import PyPDF2
import docx2txt
import os
import requests

st.set_page_config(page_title="MindMint | Smart Summarizer", page_icon="🧠")

st.title("🧠 MindMint – Smart AI Summarizer")
st.write("Upload any document and get an accurate, human-like summary powered by Gemini (Free).")

# ---------------------- TEXT EXTRACTION -------------------------
def extract_text(uploaded_file):
    file_name = uploaded_file.name.lower()

    # ---------- PDF Handling ----------
    if file_name.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(uploaded_file)

            text_pages = []
            for page in reader.pages:
                try:
                    txt = page.extract_text() or ""
                    text_pages.append(txt)
                except:
                    text_pages.append("")

            full_text = "\n".join(text_pages)

            if full_text.strip():
                return full_text

            # If still empty → fallback using pdfminer API via requests
            return ""

        except Exception:
            return ""

    # ---------- DOCX ----------
    elif file_name.endswith(".docx"):
        try:
            return docx2txt.process(uploaded_file)
        except:
            return ""

    # ---------- TXT ----------
    elif file_name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except:
            return ""

    else:
        return ""


# ---------------------- GEMINI SUMMARIZER --------------------------
def gemini_request(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    params = {"key": os.getenv("GEMINI_API_KEY")}

    response = requests.post(url, headers=headers, json=data, params=params)

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"ERROR: {response.text}"


def summarize_large_document(text):
    CHUNK_SIZE = 3500  
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    summaries = []

    for i, chunk in enumerate(chunks[:10], start=1):
        prompt = f"Summarize this section clearly:\n\n{chunk}"
        section_summary = gemini_request(prompt)

        summaries.append(f"### Section {i} Summary\n{section_summary}")

    combined = "\n\n".join(summaries)

    final_prompt = f"Create one final summary from all sections:\n\n{combined}"
    final_summary = gemini_request(final_prompt)

    return final_summary


# ---------------------- UI EXECUTION --------------------------
uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if text and text.strip():
        try:
            st.info("📄 Large document handling enabled (Chunked Summary).")

            with st.spinner("Generating summary..."):
                summary = summarize_large_document(text)

            st.success("✅ Summary generated")
            st.write(summary)

        except Exception as e:
            st.error("⚠️ Error during summarization:")
            st.error(str(e))

    else:
        st.error("❌ Could not extract text from the file.")
