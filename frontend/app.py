import streamlit as st

st.set_page_config(page_title="Rapidread", layout="wide")

st.title("Rapidread — Summarizer")

st.sidebar.title("Options")
mode = st.sidebar.selectbox("Mode", ["Upload PDF", "Article URL", "YouTube URL", "GitHub Repo"]) 

if mode == "Upload PDF":
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"]) 
    if uploaded:
        st.write("(file uploaded — connect to backend to summarize)")

elif mode == "Article URL":
    url = st.text_input("Article URL")
    if st.button("Summarize"):
        st.write("(call backend to summarize article)")

elif mode == "YouTube URL":
    url = st.text_input("YouTube URL")
    if st.button("Summarize"):
        st.write("(call backend to summarize YouTube)")

else:
    repo = st.text_input("GitHub Repo URL")
    if st.button("Summarize"):
        st.write("(call backend to summarize repo)")
