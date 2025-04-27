#!/bin/bash

# Start the FastAPI backend
uvicorn main:app --reload &

# Start the Streamlit frontend
streamlit run frontend.py