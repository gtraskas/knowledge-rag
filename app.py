from fastapi import FastAPI, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import tempfile
import os

app = FastAPI()

# Simple in-memory storage for development
document_store = None

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global document_store
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    # Load and process the document
    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings and store
    embeddings = OpenAIEmbeddings()
    document_store = FAISS.from_documents(texts, embeddings)
    
    os.unlink(temp_path)  # Clean up temp file
    
    return {"status": "success", "message": f"Processed {len(texts)} text chunks"}

@app.post("/query")
async def query(question: str):
    if document_store is None:
        return {"error": "No documents have been uploaded yet"}
    
    # Create a question-answering chain
    llm = ChatOpenAI(temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=document_store.as_retriever()
    )
    
    # Get response
    response = qa_chain.invoke(question)
    
    return {"response": response["result"]}