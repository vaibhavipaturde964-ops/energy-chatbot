import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

# Load .env for local development.
# On Railway/production this is a no-op — the env var is injected by the platform.
load_dotenv()

# 1. Path setup & Model loading
DB_PATH = "vector_db"
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# 2. Groq API key — read exclusively from environment.
#    Local dev:  set GROQ_API_KEY in root .env file.
#    Railway:    set GROQ_API_KEY in Railway project → Variables tab.
#    The actual key value must never appear in source code.
_groq_api_key = os.getenv("GROQ_API_KEY")
if not _groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Local dev: add GROQ_API_KEY=<your_key> to the root .env file. "
        "Railway: add GROQ_API_KEY in the project Variables tab."
    )

groq_client = Groq(api_key=_groq_api_key)
 
def query_rag(user_query: str) -> str:
    try:
        # A. Retrieve top 2 most relevant chunks for conciseness
        results = vector_db.similarity_search(user_query, k=2)
        context_text = "\n\n".join([doc.page_content for doc in results])

        # B. Construct Prompt with Strict Length & Line Limits
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

        # C. Call Groq Model with max token cap
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You give ultra-concise answers strictly under 8-10 lines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800  # Caps total text length
        )

        # D. Return answer text
        ans = response.choices[0].message.content

        if ans:
            return str(ans)
        else:
            return "Retrieved data, but LLM returned empty text."

    except Exception as e:
        return f"Error inside query_engine: {str(e)}"