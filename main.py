from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from typing import List
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    UnstructuredHTMLLoader,
)
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please check your .env file.")

app = FastAPI()

UPLOAD_FOLDER = Path("uploaded_files")
UPLOAD_FOLDER.mkdir(exist_ok=True)

vector_store = None
qa_chain = None


@app.get("/")
def read_root():
    return {"message": "Welcome to KnowledgeRAG!"}


@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_paths = []
    for file in files:
        file_path = UPLOAD_FOLDER / file.filename
        with file_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(str(file_path))
    return {"message": "Files uploaded successfully", "file_paths": file_paths}


@app.post("/vectorize/")
def vectorize_documents():
    global vector_store, qa_chain
    documents = []
    for file_path in UPLOAD_FOLDER.iterdir():
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                elif file_path.suffix.lower() in [".docx", ".doc"]:
                    loader = UnstructuredWordDocumentLoader(str(file_path))
                elif file_path.suffix.lower() == ".txt":
                    loader = TextLoader(str(file_path))
                elif file_path.suffix.lower() == ".html":
                    loader = UnstructuredHTMLLoader(str(file_path))
                else:
                    continue  # Skip unsupported file types

                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

    if not documents:
        raise HTTPException(status_code=400, detail="No documents found to vectorize.")

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(documents, embeddings)

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        retriever=retriever
    )
    return {"message": "Documents vectorized and stored successfully"}


@app.post("/search/")
def search_documents(query: str = Body(..., embed=True)):
    if vector_store is None:
        raise HTTPException(status_code=400, detail="Vector store not initialized. Run /vectorize/ first.")
    results = vector_store.similarity_search(query, k=5)
    return {
        "query": query,
        "results": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]
    }


@app.post("/generate/")
def generate_response(query: str = Body(..., embed=True)):
    if qa_chain is None:
        raise HTTPException(status_code=400, detail="QA chain not initialized. Run /vectorize/ first.")
    response = qa_chain.invoke(query)
    return {"query": query, "response": response}


# Mount the static files directory for serving favicon
app.mount("/static", StaticFiles(directory="static"), name="static")
