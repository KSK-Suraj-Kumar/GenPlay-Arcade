import streamlit as st
import PyPDF2
import google.generativeai as genai
import time

# ------------------- CONFIGURE GEMINI API ------------------- #
genai.configure(api_key='YOUR_GEMINI_API_KEY')  # Replace 'YOUR_GEMINI_API_KEY' with your actual API key.

model = genai.GenerativeModel('gemini-2.0-flash')

# Redirect to Login if not authenticated
if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You must log in first!")
        time.sleep(3)
        st.switch_page("login123.py")
        

# ------------------- PDF TEXT EXTRACTOR ------------------- #
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# ------------------- GEMINI RESPONSE FUNCTION ------------------- #
def generate_gemini_response(user_query, pdf_context):
    prompt = f"""
You are an AI PDF assistant. Answer the user's question based on this PDF content.

PDF Content:
{pdf_context}

User Question:
{user_query}

Your Answer:
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# ------------------- STREAMLIT FRONTEND ------------------- #
st.set_page_config(page_title="PDF Chatbot", layout="wide")
st.title("📄 Turn Static PDFs into Interactive Chats 🤖")
left_col, right_col = st.columns(2)

# ---------- BACKGROUND & STYLES ----------
st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #add8e6, #000080);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }
        .stButton>button {
            width: 20%;
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 15px;
        }
        .stButton>button:hover {
            background-color: #ffffff;
            color: green;
            transform: scale(1.05);
            } </style>
    """, unsafe_allow_html=True)

# ------------------- LEFT COLUMN: PDF UPLOAD ------------------- #
with left_col:
    st.header("Upload PDF")
    uploaded_pdf = st.file_uploader("Upload your PDF here", type=["pdf"])
    
    # PDF Status
    if uploaded_pdf:
        with st.spinner("Reading your PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_pdf)
        
        st.success("✅ PDF uploaded and processed!")
    else:
        pdf_text = ""
        st.info("Please upload a PDF to start.")

# ------------------- RIGHT COLUMN: CHATBOT ------------------- #
with right_col:
    st.header("Chatbot")

    if pdf_text:
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Initialize the user input state if not already there
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        # Function to handle send button click
        def send_click():
            user_message = st.session_state.user_input.strip()

            if user_message != "":
                with st.spinner("Generating response..."):
                    response = generate_gemini_response(user_message, pdf_text)
                
                # Append messages to chat history
                st.session_state.chat_history.append(("You", user_message))
                st.session_state.chat_history.append(("Bot", response))

                # Clear input
                st.session_state.user_input = "" 

        # Show chat history
        chat_container = st.container()
        with chat_container:
            for sender, message in st.session_state.chat_history:
                if sender == "You":
                    st.markdown(f"**🧑‍💻 You:** {message}")
                else:
                    st.markdown(f"**🤖 Bot:** {message}")

        # Text input for user's question
        st.text_input("Ask a question about the PDF", key="user_input", on_change=send_click)

    else:
        st.info("Upload a PDF to activate the chatbot.")

if st.button("⬅️Back"):
    st.switch_page("login.py")