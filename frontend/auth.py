import streamlit as st
import requests
from typing import Dict, Any
import json

BACKEND_URL = "http://localhost:8000"


class AuthService:
    
    def __init__(self):
        self.backend_url = BACKEND_URL
    
    def register_user(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.backend_url}/auth/register",
                json={
                    "full_name": full_name,
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "message": "Account created successfully! Please log in.",
                    "data": response.json()
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "message": error_data.get("detail", "Registration failed")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": "Login successful!",
                    "token": data.get("access_token"),
                    "user": data.get("user", {})
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "message": error_data.get("detail", "Login failed")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }


auth_service = AuthService()


def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'user_token' not in st.session_state:
        st.session_state.user_token = None
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    
    if 'email' not in st.session_state:
        st.session_state.email = ""


def is_logged_in() -> bool:
  
    return st.session_state.get('logged_in', False)


def logout_user():
   
    st.session_state.logged_in = False
    st.session_state.user_token = None
    st.session_state.user_info = {}
    st.session_state.full_name = ""
    st.session_state.email = ""
    st.rerun()


def show_login_form():
  
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        # Input fields for login
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="The email address you used when registering"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
       
        login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if email and password:
                with st.spinner("Logging you in..."):
                    result = auth_service.login_user(email, password)
                
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user_token = result["token"]
                    st.session_state.user_info = result["user"]
                    st.session_state.full_name = result["user"].get("full_name", "")
                    st.session_state.email = result["user"].get("email", "")
                    
                    st.success(result["message"])
                    st.rerun() 
                else:
                    st.error(result["message"])
            else:
                st.error("Please fill in both email and password")


def show_signup_form():
   
    st.subheader("Create New Account")
    
    with st.form("signup_form"):
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            help="Your first and last name"
        )
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="We'll use this for login and account recovery"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            help="Choose a secure password (at least 8 characters)"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            help="Re-enter your password"
        )
        
        signup_button = st.form_submit_button("✨ Create Account", use_container_width=True)
        
        if signup_button:
            if full_name and email and password and confirm_password:
                if password == confirm_password:
                    if len(password) >= 8:
                        with st.spinner("Creating your account..."):
                            result = auth_service.register_user(full_name, email, password)
                        
                        if result["success"]:
                            st.success(result["message"])
                            st.info("Please use the Login tab to sign in to your new account.")
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Password must be at least 8 characters long")
                else:
                    st.error("Passwords do not match!")
            else:
                st.error("Please fill in all fields")


def show_auth_page():
    
    st.title("Welcome to Rapidread")
    st.markdown("### Your AI-Powered Content Summarizer")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()
    
    st.markdown("---")
    st.markdown(
        """
        **About Rapidread:**
        - Summarize PDF documents
        - Summarize web articles
        - Summarize YouTube videos
        - Summarize GitHub repositories
        """
    )