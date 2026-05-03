import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

from dotenv import load_dotenv
import os
import uuid
import re


# ================================
# Load environment variables
# ================================
load_dotenv()


# ================================
# Configure OpenRouter
# ================================
llm_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ================================
# Embedding model
# ================================
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ================================
# ChromaDB setup
# ================================
vector_client = chromadb.PersistentClient(
    path="./EmbeddingData/vector_store"
)


# ================================
# Chat memory
# ================================
chat_history = []


# ================================
# Clean collection name
# ================================
def clean_collection_name(name):

    name = name.split(".")[0]

    name = re.sub(
        r'[^a-zA-Z0-9._-]',
        '_',
        name
    )

    if len(name) < 3:
        name += "_collection"

    return name


# ================================
# Rewrite query using memory
# ================================
def rewrite_query(query):

    global chat_history

    if len(chat_history) == 0:
        return query

    history_text = "\n".join(
        chat_history[-6:]
    )

    prompt = f"""
Rewrite the current question by replacing
pronouns like he, him, his, she, her, they
with actual names from chat history.

Do NOT answer.
Only rewrite.

Chat History:
{history_text}

Current Question:
{query}

Rewritten Question:
"""

    try:

        response = llm_client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        rewritten = response.choices[0].message.content

        if rewritten:
            return rewritten.strip()

        return query

    except:
        return query


# ================================
# Process PDF
# ================================
def process_pdf(uploaded_file):

    pdf_name = clean_collection_name(
        uploaded_file.name
    )

    collection = vector_client.get_or_create_collection(
        name=pdf_name
    )

    reader = PdfReader(
        uploaded_file
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100
    )

    documents = []
    metadatas = []

    for page_number, page in enumerate(
        reader.pages
    ):

        page_text = page.extract_text()

        if not page_text:
            continue

        chunks = splitter.split_text(
            page_text
        )

        for chunk in chunks:

            documents.append(chunk)

            metadatas.append({
                "page": page_number + 1
            })

    if not documents:
        return None

    embeddings = embedding_model.encode(
        documents
    ).tolist()

    ids = [
        str(uuid.uuid4())
        for _ in documents
    ]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    return pdf_name


# ================================
# Generate Quiz
# ================================
def generate_quiz(
    pdf_name,
    num_questions=10
):

    collection = vector_client.get_collection(
        name=pdf_name
    )

    results = collection.get()

    docs = results["documents"]

    if not docs:
        return "No content found."

    context = "\n\n".join(
        docs[:15]
    )

    prompt = f"""
Based ONLY on the provided document context,
generate {num_questions} MCQs.

Rules:
1. Each question must have 4 options:
   A, B, C, D
2. Mention correct answer.
3. Use only context.
4. No outside knowledge.

Context:
{context}
"""

    models = [
        "openrouter/free",
        "deepseek/deepseek-r1:free"
    ]

    for model_name in models:

        try:

            response = llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4
            )

            quiz = response.choices[0].message.content

            if quiz:
                return quiz

        except:
            continue

    return "Unable to generate quiz."

def generate_flashcards(
    pdf_name,
    num_cards=10
):

    collection = vector_client.get_collection(
        name=pdf_name
    )

    results = collection.get()

    docs = results["documents"]

    if not docs:
        return "No content found."

    context = "\n\n".join(
        docs[:15]
    )

    prompt = f"""
Based ONLY on the given document context,
generate {num_cards} study flashcards.

Rules:
1. Each flashcard must have:
   Front: Question
   Back: Answer
2. Use only document context.
3. No outside knowledge.
4. Keep answers concise.

Output format:

Card 1:
Front: Question
Back: Answer

Card 2:
Front: Question
Back: Answer

Context:
{context}
"""

    models = [
        "openrouter/free",
        "deepseek/deepseek-r1:free"
    ]

    for model_name in models:

        try:

            response = llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4
            )

            flashcards = response.choices[0].message.content

            if flashcards:
                return flashcards

        except:
            continue

    return "Unable to generate flashcards."
# ================================
# Ask Question
# ================================
def ask_question(
    query,
    pdf_name
):

    global chat_history

    rewritten_query = rewrite_query(
        query
    )

    collection = vector_client.get_collection(
        name=pdf_name
    )

    query_embedding = embedding_model.encode(
        [rewritten_query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    if min(distances) > 1.2:
        return (
            "The document does not contain "
            "this information."
        )

    best_distance = min(
        distances
    )

    confidence = round(
        (1 - (best_distance / 1.5)) * 100,
        2
    )

    if confidence < 0:
        confidence = 0

    context = ""

    for i, doc in enumerate(
        docs
    ):

        page = metas[i]["page"]

        context += (
            f"Page {page}:\n"
            f"{doc}\n\n"
        )

    prompt = f"""
Use ONLY the given context.

If answer is unavailable, say:
"The document does not contain this information."

Context:
{context}

Question:
{rewritten_query}

Answer:
"""

    models = [
        "openrouter/free",
        "deepseek/deepseek-r1:free"
    ]

    answer = None

    for model_name in models:

        try:

            response = llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )

            answer = response.choices[0].message.content

            if answer:
                break

        except:
            continue

    if not answer:
        answer = (
            "Unable to generate answer."
        )

    chat_history.append(
        f"User: {query}"
    )

    chat_history.append(
        f"Assistant: {answer}"
    )

    return (
        f"{answer}\n\n"
        f"Confidence: {confidence}%"
    )


# ================================
# Local test
# ================================
if __name__ == "__main__":

    print("Conversational RAG ready.")