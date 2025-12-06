# MindMint — AI Study Assistant 
MindMint helps students learn smarter by converting study material into:
-> Smart Summaries  
-> Quizzes (MCQ / True-False / Fill-in-the-blank)  
-> Flashcards 
-> Progress tracking

## Features
- Upload any PDF (notes, textbooks, handouts)
- Adjustable summary length (short / medium / detailed)
- AI quiz generator with difficulty selection
- Flashcards for memory recall
- Allows to track progress 

## How to Run (Local)
```bash
pip install -r requirements.txt
python -m nltk.downloader punkt
streamlit run mindmint_app.py