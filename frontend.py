import streamlit as st
import requests


# ---------- Custom Styles ----------
st.set_page_config(page_title="KnowledgeRAG", page_icon=":books:", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #4f8cff, #0072ff 70%);
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1.1em;
        margin: 0.5em 0;
        border: none;
        transition: background 0.3s;
        box-shadow: 0 2px 8px rgba(79,140,255,0.16);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0072ff, #4f8cff 70%);
        color: #fff;
        border: 1px solid #4f8cff;
        box-shadow: 0 4px 16px rgba(79,140,255,0.32);
        transform: translateY(-2px) scale(1.04);
    }
    .uploaded-file {
        color: #2e4053;
        background: #eaf1fb;
        padding: 0.6em 1.2em;
        border-radius: 7px;
        margin-bottom: 0.2em;
        font-weight: 500;
        font-size: 1em;
        border-left: 5px solid #4f8cff;
    }
    .custom-header {
        font-size: 2.6em;
        font-weight: 700;
        color: #0072ff;
        margin-bottom: 0.2em;
        letter-spacing: 1px;
    }
    .desc {
        font-size: 1.1em;
        color: #4f5b6b;
        margin-bottom: 1.2em;
        margin-top: -0.7em;
    }
    .result-box {
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0,80,255,0.07);
        padding: 1.2em 1.4em;
        margin-bottom: 1.2em;
        font-size: 1.12em;
        color: #1a1a1a;
        word-break: break-word;
        border-left: 5px solid #4f8cff;
    }
    .clear-btn>button {
        background: #ff6565 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 1.05em !important;
        margin-top: 0.3em !important;
        box-shadow: 0 2px 8px rgba(255,0,0,0.10);
    }
    .clear-btn>button:hover {
        background: #d13030 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- App Title & Description ----------
st.markdown('<div class="custom-header">KnowledgeRAG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="desc">'
    'KnowledgeRAG lets you ask questions about your own PDF documents! <br>'
    'Upload files, let the system "learn" from them, and then ask anything in natural language. <br>'
    '<b>What is <span style="color:#0072ff;">RAG</span>?</b> <br>'
    '<b>RAG</b> stands for <b>Retrieval-Augmented Generation</b>: it means the AI can search through your documents '
    'to find the most relevant information, and then generate a smart answer just for you.<br>'
    'This lets you quickly find answers or summaries from your files—no technical knowledge needed!'
    '</div>',
    unsafe_allow_html=True,
)

# ---------- Helper API endpoints ----------
API_URL = "http://localhost:8000"
CLEAR_URL = f"{API_URL}/clear-all/"

# ---------- Upload Section ----------
st.header("1. Upload Your Documents")
st.markdown(
    "Choose PDF files you want to ask questions about. "
    "After uploading, click <b>Vectorize</b> to let the system learn from them.",
    unsafe_allow_html=True
)
uploaded_files = st.file_uploader(
    "Select files",
    accept_multiple_files=True,
    type=["pdf"]
)

if uploaded_files:
    for file in uploaded_files:
        st.markdown(f'<div class="uploaded-file">{file.name}</div>', unsafe_allow_html=True)

if st.button("Upload Files", help="Upload the selected files to the server."):
    if uploaded_files:
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        with st.spinner("Uploading files..."):
            response = requests.post(f"{API_URL}/upload/", files=files)
        if response.status_code == 200:
            st.success("Files uploaded successfully!")
        else:
            st.error("Upload failed. Please try again.")
    else:
        st.warning("Please select at least one file.")

# ---------- Vectorize Section ----------
st.header("2. Learn from your documents (Vectorize)")
st.markdown(
    "This step lets the system analyze your files so you can search & ask questions about their content.",
    unsafe_allow_html=True
)
if st.button("Vectorize", help="Process your uploaded files for Q&A."):
    with st.spinner("Vectorizing documents..."):
        response = requests.post(f"{API_URL}/vectorize/")
    if response.status_code == 200:
        st.success("Documents vectorized and ready for search!")
    else:
        st.error(response.json().get("detail") or "Vectorization failed. Please upload documents first.")

# ---------- Search Section ----------
st.header("3. Ask Questions About Your Documents")
st.markdown(
    "Type a question about the content of your uploaded files. Click <b>Search</b> to get relevant passages. "
    "Then use <b>Generate</b> for a smart answer based on your question and the documents.",
    unsafe_allow_html=True
)
query = st.text_input("Ask a question (e.g., What is the main conclusion of my report?)")

col1, col2 = st.columns(2)
with col1:
    search_btn = st.button("Search", help="Find relevant info from your documents.")
with col2:
    generate_btn = st.button("Generate", help="Get a smart answer to your question.")

if search_btn:
    if query:
        with st.spinner("Searching documents..."):
            response = requests.post(f"{API_URL}/search/", json={"query": query})
        results = response.json()
        passages = results.get("results", [])
        if passages:
            st.subheader("Relevant Document Passages")
            for idx, result in enumerate(passages, start=1):
                st.markdown(f'<div class="result-box">{result["content"]}</div>', unsafe_allow_html=True)
        else:
            st.info("No relevant passages found.")
    else:
        st.warning("Please enter a question before searching.")

if generate_btn:
    if query:
        with st.spinner("Generating answer..."):
            response = requests.post(f"{API_URL}/generate/", json={"query": query})
        generated_response = response.json()
        answer = generated_response.get("response", "")
        # If the answer is in a dict (as in some LLM chains), get the answer text
        if isinstance(answer, dict):
            answer = answer.get("result", "") or answer.get("output_text", "")
        if answer:
            st.subheader("Your Answer")
            st.markdown(f'<div class="result-box">{answer}</div>', unsafe_allow_html=True)
        else:
            st.info("No answer generated.")
    else:
        st.warning("Please enter a question before generating an answer.")

# ---------- Clear Documents Section ----------
st.markdown("---")
st.header("Start Over / Remove All Documents")
st.markdown(
    "Click the button below to remove all uploaded documents and reset the system. "
    "You can then start fresh with new files.",
    unsafe_allow_html=True
)
if st.button(
    "Clear All Documents",
    key="clear",
    help="Remove all uploaded files and reset the system.",
    type="primary"
):
    with st.spinner("Clearing all uploaded documents and resetting..."):
        response = requests.post(CLEAR_URL)
    if response.status_code == 200:
        st.success("All documents and data cleared! You can upload new files now.")
    else:
        st.error("Failed to clear files. Please try again.")

st.markdown(
    "<br><center style='color:#aab6c9; font-size:0.9em;'>"
    "Powered by LangChain, OpenAI, and Streamlit. Your documents are never shared."
    "</center>",
    unsafe_allow_html=True
)
