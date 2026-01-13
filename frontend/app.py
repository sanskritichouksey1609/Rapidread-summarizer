import streamlit as st
from auth import init_session_state, is_logged_in, show_auth_page, logout_user
from utils import summarize_article, summarize_pdf, summarize_youtube, summarize_github

# Configure the page
st.set_page_config(page_title="Rapidread", layout="wide")


def show_main_app():
    """
    Display the main application interface
    
    This function shows the main Rapidread interface that users see
    after they've successfully logged in.
    """
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Rapidread — Summarizer")
        st.markdown(f"Welcome back, **{st.session_state.full_name}**! 👋")
    
    with col2:
        st.write("")  # Add some spacing
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    st.markdown("---")
    
    # Sidebar options
    st.sidebar.title("📋 Summarization Options")
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.full_name}")
    st.sidebar.markdown(f"**Email:** {st.session_state.email}")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.selectbox(
        "Choose Input Type", 
        ["Upload PDF", "Article URL", "YouTube URL", "GitHub Repo"],
        help="Select the type of content you want to summarize"
    )
    
    # Main content area based on selected mode
    if mode == "Upload PDF":
        st.header("📄 PDF Document Summarizer")
        st.markdown("Upload a PDF file to get an AI-powered summary")
        
        uploaded = st.file_uploader(
            "Choose a PDF file", 
            type=["pdf"],
            help="Maximum file size: 10MB"
        )
        
        if uploaded:
            st.success(f"File uploaded: {uploaded.name}")
            if st.button("🔍 Summarize PDF", use_container_width=True):
                with st.spinner("Analyzing PDF..."):
                    # Read file content
                    file_content = uploaded.read()
                    
                    # Call backend API
                    result = summarize_pdf(file_content, uploaded.name)
                    
                    if result.get("success"):
                        st.success("✅ PDF summarized successfully!")
                        summary_data = result["summary"]
                        
                        # Display summary
                        st.subheader("📋 Summary")
                        st.write(summary_data["summary"])
                        
                        # Display metadata
                        with st.expander("📊 Details"):
                            st.write(f"**Filename:** {summary_data['filename']}")
                            st.write(f"**Created:** {summary_data['created_at']}")
                            st.write(f"**Summary ID:** {summary_data['id']}")
                    else:
                        st.error(f"❌ {result.get('error', 'Summarization failed')}")
    
    elif mode == "Article URL":
        st.header("🌐 Web Article Summarizer")
        st.markdown("Enter a URL to summarize any web article")
        
        url = st.text_input(
            "Article URL",
            placeholder="https://example.com/article",
            help="Enter the full URL of the article you want to summarize"
        )
        
        if st.button("🔍 Summarize Article", use_container_width=True):
            if url:
                with st.spinner("Fetching and analyzing article..."):
                    # Call backend API
                    result = summarize_article(url)
                    
                    if result.get("success"):
                        st.success("✅ Article summarized successfully!")
                        summary_data = result["summary"]
                        
                        # Display summary
                        st.subheader("📋 Summary")
                        st.write(summary_data["summary"])
                        
                        # Display metadata
                        with st.expander("📊 Article Details"):
                            st.write(f"**Title:** {summary_data.get('title', 'Article')}")
                            st.write(f"**URL:** {summary_data['source_url']}")
                            st.write(f"**Domain:** {summary_data.get('domain', 'Unknown')}")
                            
                            # Authors
                            authors = summary_data.get('authors', [])
                            if authors:
                                st.write(f"**Authors:** {', '.join(authors)}")
                            
                            # Publish date
                            publish_date = summary_data.get('publish_date', '')
                            if publish_date:
                                st.write(f"**Published:** {publish_date}")
                            
                            # Keywords
                            keywords = summary_data.get('keywords', [])
                            if keywords:
                                st.write(f"**Keywords:** {', '.join(keywords)}")
                            
                            # Technical details
                            st.write(f"**Extraction Method:** {summary_data.get('extraction_method', 'Unknown')}")
                            st.write(f"**Created:** {summary_data['created_at']}")
                            st.write(f"**Summary ID:** {summary_data['id']}")
                            
                            # Top image
                            top_image = summary_data.get('top_image', '')
                            if top_image:
                                try:
                                    st.image(top_image, caption="Article Image", width=300)
                                except:
                                    st.write(f"**Image URL:** {top_image}")
                    else:
                        st.error(f"❌ {result.get('error', 'Summarization failed')}")
            else:
                st.error("Please enter a valid URL")
    
    elif mode == "YouTube URL":
        st.header("🎥 YouTube Video Summarizer")
        st.markdown("Get summaries of YouTube videos from their transcripts")
        st.info("📝 **Note:** This feature extracts actual transcripts from YouTube videos. The video must have captions/subtitles enabled.")
        
        url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=... or https://youtu.be/...",
            help="Enter the YouTube video URL. The video must have captions enabled."
        )
        
        if st.button("🔍 Summarize Video", use_container_width=True):
            if url:
                with st.spinner("Extracting transcript and analyzing video..."):
                    # Call backend API
                    result = summarize_youtube(url)
                    
                    if result.get("success"):
                        st.success("✅ YouTube video summarized successfully!")
                        summary_data = result["summary"]
                        
                        # Display summary
                        st.subheader("📋 Summary")
                        st.write(summary_data["summary"])
                        
                        # Display metadata
                        with st.expander("📊 Video Details"):
                            st.write(f"**Video URL:** {summary_data['source_url']}")
                            st.write(f"**Video ID:** {summary_data.get('video_id', 'N/A')}")
                            st.write(f"**Language:** {summary_data.get('language', 'Unknown')}")
                            st.write(f"**Transcript Type:** {summary_data.get('transcript_type', 'Unknown')}")
                            st.write(f"**Transcript Length:** {summary_data.get('transcript_length', 0)} characters")
                            st.write(f"**Created:** {summary_data['created_at']}")
                            st.write(f"**Summary ID:** {summary_data['id']}")
                    else:
                        error_msg = result.get('error', 'Summarization failed')
                        
                        # Provide helpful error messages
                        if "Invalid YouTube URL" in error_msg:
                            st.error("❌ Invalid YouTube URL. Please enter a valid YouTube video URL.")
                            st.info("💡 **Supported formats:**\n- https://youtube.com/watch?v=VIDEO_ID\n- https://youtu.be/VIDEO_ID\n- https://youtube.com/embed/VIDEO_ID")
                        elif "transcript" in error_msg.lower() or "captions" in error_msg.lower():
                            st.error("❌ This video doesn't have transcripts/captions available.")
                            st.info("💡 **Try these solutions:**\n- Choose a different video that has captions\n- Look for videos with the 'CC' icon\n- Try educational or news videos (they usually have captions)")
                        elif "too short" in error_msg:
                            st.error("❌ The video transcript is too short to generate a meaningful summary.")
                        else:
                            st.error(f"❌ {error_msg}")
            else:
                st.error("Please enter a valid YouTube URL")
    
    else:  # GitHub Repo
        st.header("💻 GitHub Repository Summarizer")
        st.markdown("Analyze and summarize GitHub repositories")
        
        repo = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository",
            help="Enter the GitHub repository URL"
        )
        
        if st.button("🔍 Summarize Repository", use_container_width=True):
            if repo:
                with st.spinner("Analyzing repository..."):
                    # Call backend API
                    result = summarize_github(repo)
                    
                    if result.get("success"):
                        st.success("✅ GitHub repository summarized successfully!")
                        summary_data = result["summary"]
                        
                        # Display summary
                        st.subheader("📋 Summary")
                        st.write(summary_data["summary"])
                        
                        # Display metadata
                        with st.expander("📊 Details"):
                            st.write(f"**Repository:** {summary_data.get('owner', '')}/{summary_data.get('repo', '')}")
                            st.write(f"**URL:** {summary_data['source_url']}")
                            st.write(f"**Created:** {summary_data['created_at']}")
                            st.write(f"**Summary ID:** {summary_data['id']}")
                    else:
                        st.error(f"❌ {result.get('error', 'Summarization failed')}")
            else:
                st.error("Please enter a valid GitHub repository URL")
    
    # Footer
    st.markdown("---")
    st.markdown("**Rapidread** - AI-powered content summarization made simple")


def main():
    """
    Main Application Function
    
    This is the entry point of the application. It handles the overall flow:
    1. Initialize session state
    2. Check if user is logged in
    3. Show appropriate interface (auth or main app)
    """
    # Initialize session state for authentication
    init_session_state()
    
    # Check if user is logged in
    if is_logged_in():
        # User is logged in - show main application
        show_main_app()
    else:
        # User is not logged in - show authentication page
        show_auth_page()


# Run the application
if __name__ == "__main__":
    main()
