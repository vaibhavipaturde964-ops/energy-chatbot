from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(documents)