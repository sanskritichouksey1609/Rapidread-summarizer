import streamlit as st
from auth import is_logged_in

if is_logged_in():
    st.title("Home")
    st.markdown(f"Welcome to Rapidread, **{st.session_state.full_name}**!")
    st.markdown("---")
    
    st.markdown("""
    ### What you can do with Rapidread:
    
    - **PDF Summarization**: Upload PDF documents and get AI-powered summaries
    - **Article Summarization**: Paste any web article URL for instant summaries  
    - **YouTube Summarization**: Get summaries from YouTube video transcripts
    - **GitHub Repository Analysis**: Analyze and summarize GitHub repositories
    
    ### How to get started:
    1. Use the sidebar to select your input type
    2. Provide your content (file, URL, etc.)
    3. Click the summarize button
    4. Get your AI-powered summary!
    
    ### Tips:
    - Make sure your backend server is running on `http://localhost:8000`
    - PDF files should be under 10MB for best performance
    - YouTube videos need to have captions/transcripts available
    """)
    
else:
    st.error("Please log in to access this page")
    st.stop()
