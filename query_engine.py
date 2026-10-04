import os
import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

# Load environment variables for local dev (.env)
load_dotenv()

# 1. Path setup & Cached Model/DB Loading
DB_PATH = "vector_db"

@st.cache_resource
def get_vector_db():
    """
    Caches the HuggingFace embedding model and Chroma DB instance in memory 
    to prevent cold-start delays on every rerun.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# Initialize cached Vector DB
vector_db = get_vector_db()

# 2. Groq API Key Setup
_groq_api_key = os.getenv("GROQ_API_KEY")
if not _groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Local dev: add GROQ_API_KEY=<your_key> to the root .env file. "
        "Streamlit Cloud: add GROQ_API_KEY under App Settings -> Secrets."
    )

# Initialize Groq client
groq_client = Groq(api_key=_groq_api_key)

def query_rag(user_query: str) -> str:
    try:
        # A. Retrieve top 2 most relevant chunks for conciseness
        results = vector_db.similarity_search(user_query, k=2)
        context_text = "\n\n".join([doc.page_content for doc in results])

        # B. Construct Prompt
        prompt = f"""
        You are EcoBot, an expert assistant on energy efficiency and sustainability.

        Reference Context:
        {context_text}

        User Question:
        {user_query}

        STRICT RESPONSE RULES:
        1. Keep your total response STRICTLY under 8 to 10 lines long.
        2. Be direct, clear, and concise. Avoid long introductions or filler text.
        3. Use 3 to 4 short bullet points if listing key reasons or tips.
        4. Focus immediately on the practical core answer.
        """

        # C. Call Groq Model using official model ID
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You give ultra-concise answers strictly under 8-10 lines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )

        # D. Return answer text
        ans = response.choices[0].message.content

        if ans:
            return str(ans)
        else:
            return "Retrieved data, but LLM returned empty text."

    except Exception as e:
        return f"Error inside query_engine: {str(e)}"