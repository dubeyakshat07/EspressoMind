import os
from langchain.document_loaders import PyPDFLoader, UnstructuredImageLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma

def ingest_documents():
    documents = []
    # Load PDFs
    pdf_dir = "data/documents"
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_dir, file))
            documents.extend(loader.load())

    # Load Images
    image_dir = "data/images"
    for file in os.listdir(image_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            loader = UnstructuredImageLoader(os.path.join(image_dir, file))
            documents.extend(loader.load())

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    # Generate embeddings
    embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_MODEL"))

    # Store in ChromaDB
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="vectorstore")
    vectorstore.persist()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_documents()
