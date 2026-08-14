from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

VECTOR_DB_DIR = "vector_db"

def test_query(query: str):
    print(f"\n🔍 Querying Vector DB for: '{query}'\n" + "-"*50)
    
    # Load embedding model and existing Chroma DB
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    
    # Search top 3 most similar chunks
    results = vectorstore.similarity_search(query, k=3)
    
    for i, doc in enumerate(results, 1):
        print(f"📄 Result {i} [Source: {doc.metadata.get('source', 'Unknown')} | Type: {doc.metadata.get('type', 'N/A')}]")
        print(f"{doc.page_content[:300]}...\n")

if __name__ == "__main__":
    # Test with a question related to your dataset
    test_query("What columns exist in the daily weather dataset?")