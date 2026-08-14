import os
import pandas as pd
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def load_csv_summaries(file_path: str) -> Document:
    """Loads CSV files with encoding fallback for non-UTF-8 characters."""
    filename = os.path.basename(file_path)
    
    # Try reading with utf-8 first, fall back to latin1 if special symbols like £ exist
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1')
    
    summary_text = f"Dataset File: {filename}\n"
    summary_text += f"Columns: {', '.join(df.columns.tolist())}\n"
    summary_text += f"Total Rows: {len(df)}\n\n"
    summary_text += f"Sample Data Snapshot:\n{df.head(5).to_string(index=False)}"
    
    return Document(
        page_content=summary_text,
        metadata={"source": filename, "type": "csv_summary"}
    )

def load_html_doc(file_path: str) -> Document:
    """Extracts raw readable text from HTML documentation files."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin1") as f:
            content = f.read()
            
    soup = BeautifulSoup(content, "html.parser")
    for script_or_style in soup(["script", "style", "nav", "footer"]):
        script_or_style.extract()
        
    text = soup.get_text(separator="\n")
    clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    
    return Document(
        page_content=clean_text,
        metadata={"source": os.path.basename(file_path), "type": "html_doc"}
    )

def load_pdf_doc(file_path: str) -> list[Document]:
    """Extracts text page by page from PDF files."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    for doc in documents:
        doc.metadata["type"] = "pdf_paper"
        doc.metadata["source"] = os.path.basename(file_path)
    return documents