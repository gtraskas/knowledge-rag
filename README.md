# KnowledgeRAG

A modern document knowledge base with conversational AI capabilities, built using a Retrieval-Augmented Generation (RAG) architecture.

## Features

- 📄 Document ingestion (PDF, DOCX, TXT, HTML)
- 🔍 Semantic search across all documents
- 💬 Conversational interface for natural queries
- 🧠 Context-aware responses with citations
- 🚀 FastAPI backend for high performance

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **RAG Framework**: LangChain/LlamaIndex
- **Vector Database**: Qdrant (or Chroma/FAISS)
- **LLM Integration**: OpenAI API (configurable for other providers)
- **Frontend**: Streamlit or React (based on your preference)
- **Deployment**: Docker, optionally with docker-compose

## Quick Start

1. Clone the repository

    ```bash
    git clone https://github.com/gtraskas/knowledge-rag.git
    cd knowledge-rag
    ```

2. Set up environment

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Set up environment variables

    ```bash
    # Edit .env with your API keys
    ```

4. Run the application

    ```bash
    cd app
    python -m app.main
    ```

## Project Structure

```plaintext
knowledge-rag/
├── app/
│   ├── api/            # FastAPI routes
│   ├── core/           # Core RAG functionality
│   ├── db/             # Vector DB connections
│   ├── models/         # Pydantic models
│   ├── services/       # Business logic
│   └── main.py         # Application entry point
├── frontend/           # Streamlit or React frontend
├── tests/              # Test suite
├── docs/               # Documentation
├── .env.example        # Example environment variables
├── requirements.txt    # Python dependencies
└── Dockerfile          # Container definition
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Thoughts

Why RAG Is More Manageable for Solo Development

Off-the-shelf Components: LangChain provides pre-built components that handle most of the complex logic:

Document loaders for various file types
Text splitters and chunking strategies
Embedding generation
Retrieval logic
Simpler Frontend Requirements: Just a chat interface, compared to complex dashboards and visualization tools

The LLM Does the Heavy Lifting: The LLM handles the "intelligence" part, generating insights and explanations

Less Domain-Specific Logic: You don't need to write code to detect data patterns, suggest visualizations, or implement statistical tests

Modular Architecture: You can build one piece at a time and have a working system at each stage

1. Start with a Minimum Viable Product (2-3 weeks)

2. Add Core Features (Weeks 3-5)

Replace the simple in-memory FAISS with a persistent vector database (Chroma, Qdrant)
Add support for more document types (Word, text, HTML)
Implement better chunking strategies
Add source attribution to responses
3. Enhance User Experience (Weeks 6-8)

Build a better frontend (Streamlit or React)
Add conversation history
Implement document management (delete, update)
Add visualizations of retrieved contexts
4. Advanced Features (Optional)

Implement user authentication
Add domain-specific prompt templates
Support for private or fine-tuned models
Implement evaluation metrics
Cost Considerations

LLM API Costs: OpenAI API costs can add up, but you can:

Use open-source models (Llama 3, Mistral) with a service like Fireworks.ai or local deployment
Implement rate limiting and cost monitoring
Start with GPT-3.5-Turbo for development (much cheaper than GPT-4)
Vector Database: Most have free tiers adequate for development:

Qdrant Cloud free tier
Pinecone starter plan
Chroma (self-hosted) is free
Why This Is More Approachable Than the Data Analysis Platform

The data analysis platform requires you to implement complex logic for:

Automated data cleaning for multiple data types
Intelligent visualization selection
Statistical analysis across various distributions
Feature engineering and ML model selection
Custom dashboards and visualization components
This demands deep expertise in statistics, ML, and data visualization, plus significantly more custom code.
