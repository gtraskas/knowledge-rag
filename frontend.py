import streamlit as st
import requests


st.set_page_config(
    page_title="KnowledgeRAG",
    page_icon=":books:",
    layout="centered"
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .main { background-color: #f5f7fa; }
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
    .tips-box {
        background: #eaf1fb;
        border-left: 6px solid #0072ff;
        border-radius: 7px;
        padding: 1em 1.2em 1em 1.2em;
        margin-bottom: 1.2em;
        font-size: 1.06em;
        color: #1a3050;
    }
    .section-header {
        margin-top: 2.2em;
        margin-bottom: 0.25em;
        color: #0072ff;
        font-size: 1.35em;
        font-weight: 650;
    }
    .order-badge {
        display: inline-block;
        background: #4f8cff;
        color: #fff;
        border-radius: 50%;
        width: 2em;
        height: 2em;
        font-size: 1.05em;
        font-weight: bold;
        text-align: center;
        line-height: 2em;
        margin-right: 0.7em;
        margin-bottom: 0.1em;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Header and Description ----------
st.markdown(
    '<div class="custom-header">KnowledgeRAG</div>',
    unsafe_allow_html=True
)
st.markdown(
    """<div class="desc">
    KnowledgeRAG lets you ask questions about your own PDF documents!<br>
    Upload files, let the system "learn" from them, and then ask anything in natural language.<br>
    <b>What is <span style="color:#0072ff;">RAG</span>?</b><br>
    <b>RAG</b> stands for <b>Retrieval-Augmented Generation</b>: it means the AI can search through your documents
    to find the most relevant information, and then generate a smart answer just for you.<br>
    This lets you quickly find answers or summaries from your files—no technical knowledge needed!
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div class="tips-box">
    <b>Best Practices for Great Results:</b>
    <ul>
        <li><b>Upload only relevant files</b> for your current session. Remove old files with "Clear All"
        before starting a new project.</li>
        <li><b>Use clear, descriptive file names</b> to help organize your uploads.</li>
        <li><b>Prefer smaller or focused documents</b> over huge ones. If your documents are very large,
        consider splitting them into separate files for more accurate answers.</li>
        <li>When asking a question, <b>be as specific as possible</b>. For example:
        "What is the conclusion in <i>report_A.pdf</i>?" or "Summarize section 3 of the user manual."</li>
        <li>If you want answers from <b>multiple files</b>, use a query that clearly references both,
        or ask a question that would reasonably require information from both documents.</li>
        <li>If your files have very similar content, the answer may focus on the most relevant one.</li>
        <li>For best performance, avoid uploading files with the same name, even if their content differs.</li>
        <li>Click "Clear All Documents" before uploading a new batch of files for a fresh session.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)

API_URL = "http://backend:8000"
CLEAR_URL = f"{API_URL}/clear-all/"

# ---------- Step 1: Upload ----------
st.markdown(
    '<div class="section-header">'
    '<span class="order-badge">1</span>Upload Your Documents'
    '</div>',
    unsafe_allow_html=True
)

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

upload_col, vector_col = st.columns([1, 1])
with upload_col:
    upload_clicked = st.button("Upload Files", help="Upload the selected files to the server.")
with vector_col:
    vectorize_clicked = st.button("Vectorize", help="Process your uploaded files for Q&A.")

if upload_clicked:
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

if vectorize_clicked:
    with st.spinner("Vectorizing documents..."):
        response = requests.post(f"{API_URL}/vectorize/")
    if response.status_code == 200:
        st.success("Documents vectorized and ready for search!")
    else:
        st.error(response.json().get("detail") or "Vectorization failed. Please upload documents first.")

# ---------- Step 2: Ask ----------
st.markdown(
    '<div class="section-header">'
    '<span class="order-badge">2</span>Ask Questions About Your Documents'
    '</div>',
    unsafe_allow_html=True
)
st.markdown(
    "Type a question about your uploaded files. Click <b>Search</b> to preview relevant passages. "
    "Then click <b>Generate Answer</b> for a smart, synthesized answer based on your question and the documents.",
    unsafe_allow_html=True
)
query = st.text_input("Ask a question (e.g., What is the main conclusion of my report?)")

search_col, generate_col = st.columns([1, 1])
with search_col:
    search_btn = st.button("Search", key="search_btn", help="Preview relevant info from your documents.")
with generate_col:
    generate_btn = st.button("Generate Answer", key="generate_btn", help="Get a smart answer to your question.")

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
        try:
            generated_response = response.json()
            answer = generated_response.get("response", "")
            if isinstance(answer, dict):
                answer = answer.get("result", "") or answer.get("output_text", "")
            if answer:
                st.subheader("Your Answer")
                st.markdown(f'<div class="result-box">{answer}</div>', unsafe_allow_html=True)
                sources = generated_response.get("sources", [])
                if sources:
                    st.markdown(
                        "<div style='color:#4f8cff;font-size:0.98em; margin-top:-0.5em;'>Sources used: " +
                        ", ".join([f"<i>{src}</i>" for src in set(sources)]) +
                        "</div>", unsafe_allow_html=True
                    )
            else:
                st.info("No answer generated.")
        except Exception:
            st.error("An error occurred. Please try a shorter question or fewer documents.")
    else:
        st.warning("Please enter a question before generating an answer.")

# ---------- Step 3: Clear All ----------
st.markdown(
    '<div class="section-header">'
    '<span class="order-badge">3</span>Start Over / Remove All Documents'
    '</div>',
    unsafe_allow_html=True
)

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
