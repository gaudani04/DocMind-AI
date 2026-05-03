# DocMind AI

An AI-powered PDF learning assistant built using conversational :contentReference[oaicite:0]{index=0}.

DocMind AI allows users to upload PDF documents and:

- Chat with PDFs
- Ask follow-up contextual questions
- Generate quizzes automatically
- Generate flashcards for revision
- Get confidence-based responses
- Prevent hallucinated answers using similarity thresholds

---

## Features

### 1. Conversational PDF Chat
Ask questions from uploaded PDFs.

Example:

Who is Raj Shamani?

Follow-up:

What companies did he start?

The system remembers previous conversation context and resolves pronouns like:

- he
- him
- his
- she
- her

---

### 2. Hallucination Control
If the information is not present in the document, the system responds:

> The document does not contain this information.

This prevents AI-generated false answers.

---

### 3. Confidence Score
Each response includes retrieval confidence.

Example:

Confidence: 84.25%

---

### 4. Quiz Generator
Generate multiple-choice questions from uploaded study notes.

Example:

Generate 10 MCQs from this PDF.

---

### 5. Flashcards Generator
Create study flashcards automatically.

Example:

Front: What is entrepreneurship?  
Back: The process of building and managing a business.

---

## Tech Stack

### Frontend
- :contentReference[oaicite:1]{index=1}

### Backend
- Python

### Embeddings
- :contentReference[oaicite:2]{index=2} (`all-MiniLM-L6-v2`)

### Vector Database
- :contentReference[oaicite:3]{index=3}

### LLM Provider
- :contentReference[oaicite:4]{index=4}

---

## System Architecture

PDF Upload  
↓  
Text Extraction  
↓  
Chunking  
↓  
Embedding Generation  
↓  
Vector Storage  
↓  
Semantic Retrieval  
↓  
LLM Response Generation  
↓  
Quiz / Flashcards

---

## Installation

### Clone repository

```bash
git clone YOUR_REPOSITORY_URL
cd DocMind-AI
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create environment file

Create `.env`

```env
OPENROUTER_API_KEY=your_api_key_here
```

### Run application

```bash
streamlit run app.py
```

---

## Future Improvements

- Multi-PDF comparison
- Voice-based interaction
- Topic-wise summaries
- User learning analytics

---

## Author

**Siddhi Gaudani**  
Computer Science Engineering Student