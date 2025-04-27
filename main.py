from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from typing import List
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import shutil
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please check your .env file.")

app = FastAPI()

UPLOAD_FOLDER = Path("uploaded_files")
UPLOAD_FOLDER.mkdir(exist_ok=True)

VECTOR_STORE_PATH = "vector_store.faiss"

vector_store = None
qa_chain = None


def remove_pycache_and_vector_store():
    if Path(VECTOR_STORE_PATH).exists():
        shutil.rmtree(VECTOR_STORE_PATH, ignore_errors=True)
    if UPLOAD_FOLDER.exists():
        for file in UPLOAD_FOLDER.iterdir():
            if file.is_file():
                file.unlink()
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name), ignore_errors=True)


def load_vector_store():
    global vector_store, qa_chain
    if Path(VECTOR_STORE_PATH).exists():
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            retriever=retriever
        )
    else:
        vector_store = None
        qa_chain = None


# --- On startup, remove all previous files for a fresh start ---
remove_pycache_and_vector_store()


@app.on_event("startup")
def on_startup():
    logging.info("Application startup initiated.")
    remove_pycache_and_vector_store()
    load_vector_store()
    logging.info("Application startup completed.")


@app.get("/")
def read_root():
    logging.info("Root endpoint accessed.")
    return {"message": "Welcome to KnowledgeRAG!"}


@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    logging.info("Upload endpoint accessed with %d files.", len(files))
    file_paths = []
    for file in files:
        file_path = UPLOAD_FOLDER / file.filename
        try:
            with file_path.open("wb") as f:
                content = await file.read()
                f.write(content)
            file_paths.append(str(file_path))
            logging.info("File %s uploaded successfully.", file.filename)
        except Exception as e:
            logging.error("Error uploading file %s: %s", file.filename, str(e))
            raise HTTPException(status_code=500, detail=f"Error uploading file {file.filename}")
    return {"message": "Files uploaded successfully", "file_paths": file_paths}


@app.post("/vectorize/")
def vectorize_documents():
    logging.info("Vectorize endpoint accessed.")
    global vector_store, qa_chain
    documents = []
    for file_path in UPLOAD_FOLDER.iterdir():
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                else:
                    continue
                docs = loader.load()
                # Set source metadata for provenance
                for doc in docs:
                    doc.metadata['source'] = file_path.name
                documents.extend(docs)
                logging.info("File %s processed successfully.", file_path.name)
            except Exception as e:
                logging.error("Error processing file %s: %s", file_path.name, str(e))
                continue

    if not documents:
        logging.warning("No documents found to vectorize.")
        raise HTTPException(status_code=400, detail="No documents found to vectorize.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    split_docs = []
    for doc in documents:
        splits = text_splitter.split_documents([doc])
        for split in splits:
            # propagate source metadata to chunks
            split.metadata['source'] = doc.metadata.get('source', 'unknown')
        split_docs.extend(splits)

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(split_docs, embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)

    retriever = vector_store.as_retriever(search_kwargs={"k": 10})  # k=10 for more diverse retrieval
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        retriever=retriever
    )
    logging.info("Documents vectorized and stored successfully.")
    return {"message": "Documents vectorized and stored successfully"}


@app.post("/search/")
def search_documents(query: str = Body(..., embed=True)):
    logging.info("Search endpoint accessed with query: %s", query)
    load_vector_store()
    if vector_store is None:
        logging.warning("Vector store not initialized.")
        raise HTTPException(status_code=400, detail="Vector store not initialized. Run /vectorize/ first.")
    results = vector_store.similarity_search(query, k=10)
    logging.info("Search completed with %d results.", len(results))
    return {
        "results": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]
    }


def get_diverse_chunks(chunks, max_files=2, chunks_per_file=2):
    """Returns up to `chunks_per_file` chunks from up to `max_files` different files."""
    file_chunks = defaultdict(list)
    for chunk in chunks:
        source = chunk.metadata.get('source', 'unknown')
        if len(file_chunks[source]) < chunks_per_file:
            file_chunks[source].append(chunk)
        # Stop if enough files have been added
        if len(file_chunks) >= max_files and all(len(lst) >= chunks_per_file for lst in file_chunks.values()):
            break
    # Flatten the result
    result = []
    for file_list in file_chunks.values():
        result.extend(file_list)
    return result


@app.post("/generate/")
def generate_response(query: str = Body(..., embed=True)):
    logging.info("Generate endpoint accessed with query: %s", query)
    load_vector_store()
    if qa_chain is None:
        logging.warning("QA chain not initialized.")
        raise HTTPException(status_code=400, detail="QA chain not initialized. Run /vectorize/ first.")
    # Retrieve more chunks than needed to diversify sources
    all_chunks = vector_store.similarity_search(query, k=20)
    diverse_chunks = get_diverse_chunks(all_chunks, max_files=2, chunks_per_file=2)
    # Prepare context
    if not diverse_chunks:
        logging.warning("No relevant chunks found for generation.")
        raise HTTPException(status_code=400, detail="No relevant content found to answer the query.")
    # Use combine_documents_chain to explicitly pass context
    try:
        response = qa_chain.combine_documents_chain.run(
            input_documents=diverse_chunks, question=query
        )
    except Exception as e:
        logging.error("LLM call failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer. Try a shorter question or fewer documents."
        )
    logging.info("Response generated successfully.")
    # Optionally, return source info for UI transparency
    sources = [doc.metadata.get('source', 'unknown') for doc in diverse_chunks]
    return {"response": response, "sources": sources}


@app.post("/clear-all/")
def clear_all():
    logging.info("Clear-all endpoint accessed.")
    remove_pycache_and_vector_store()
    load_vector_store()
    logging.info("All uploaded documents and vector store have been removed.")
    return {"message": "All uploaded documents and vector store have been removed."}


# Mount the static files directory for serving favicon
app.mount("/static", StaticFiles(directory="static"), name="static")
