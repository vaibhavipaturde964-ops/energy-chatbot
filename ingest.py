import os
import shutil
from ingestion.data_loader import load_csv_summaries, load_html_doc, load_pdf_doc
from ingestion.chunker import chunk_documents
from ingestion.embedder import store_in_chroma

DATA_DIR = "data/raw"
DB_PATH = "vector_db"  # Path where your Chroma DB is saved

def run_pipeline():
    print("🚀 Starting Data Ingestion Pipeline...")
    all_documents = []

    # 0. Clean old database to prevent mixed chunk data
    if os.path.exists(DB_PATH):
        print("🧹 Clearing old database to re-index fresh overlapping chunks...")
        shutil.rmtree(DB_PATH)

    # 1. Load CSVs
    csv_files = [
        "acorn_details.csv", 
        "daily_dataset.csv", 
        "informations_households.csv", 
        "uk_bank_holidays.csv", 
        "weather_daily_darksky.csv", 
        "weather_hourly_darksky.csv"
    ]
    for csv_f in csv_files:
        path = os.path.join(DATA_DIR, csv_f)
        if os.path.exists(path):
            all_documents.append(load_csv_summaries(path))
            print(f"  [✓] Loaded CSV summary: {csv_f}")

    # 2. Load HTML
    html_path = os.path.join(DATA_DIR, "darksky_parameters_docs.html")
    if os.path.exists(html_path):
        all_documents.append(load_html_doc(html_path))
        print("  [✓] Loaded HTML: darksky_parameters_docs.html")

    # 3. Load PDF
    pdf_path = os.path.join(DATA_DIR, "JETIR1405001.pdf")
    if os.path.exists(pdf_path):
        all_documents.extend(load_pdf_doc(pdf_path))
        print("  [✓] Loaded PDF: JETIR1405001.pdf")

    # 4. Chunk Documents with Overlap
    print("\n✂️ Chunking Documents...")
    chunks = chunk_documents(all_documents)
    print(f"  Total overlapping chunks created: {len(chunks)}")

    # 5. Embed & Store
    print("\n🧠 Generating Embeddings & Saving to Vector DB...")
    store_in_chroma(chunks)
    print("\n✅ Ingestion finished successfully!")

if __name__ == "__main__":
    run_pipeline()