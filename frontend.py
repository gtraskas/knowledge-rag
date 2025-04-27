import streamlit as st
import requests

st.title("KnowledgeRAG Interface")

# Upload documents
st.header("Upload Documents")
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
if st.button("Upload"):
    if uploaded_files:
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        response = requests.post("http://localhost:8000/upload/", files=files)
        st.write(response.json())
    else:
        st.warning("Please upload at least one file.")

# Vectorize documents
st.header("Vectorize Documents")
if st.button("Vectorize"):
    response = requests.post("http://localhost:8000/vectorize/")
    st.write(response.json())

# Search documents
st.header("Search Documents")
query = st.text_input("Enter your query")
if st.button("Search"):
    if query:
        response = requests.post("http://localhost:8000/search/", json={"query": query})
        st.write(response.json())
    else:
        st.warning("Please enter a query.")

# Generate response
st.header("Generate Response")
if st.button("Generate"):
    if query:
        response = requests.post("http://localhost:8000/generate/", json={"query": query})
        st.write(response.json())
    else:
        st.warning("Please enter a query.")
