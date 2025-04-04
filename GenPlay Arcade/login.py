import streamlit as st
import mysql.connector
import hashlib
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

# ---------- CONFIGURE DATABASE CONNECTION ---------- #
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",      
        user="root", 
        password="PASSWORD",# Change to your MySQL password
        database="genplayarcade"    
    )
    return connection

# ---------- PASSWORD HASHING FUNCTION ---------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- SIGNUP FUNCTION ---------- #
def signup():
    st.subheader("Create a New Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        
        hashed_password = hash_password(password)

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                st.warning("Username or Email already exists. Please try a different one.")
                return

            query = "INSERT INTO users (email, username, password) VALUES (%s, %s, %s)"
            values = (email, username, hashed_password)

            cursor.execute(query, values)
            connection.commit()

            st.success("You have successfully created an account! Please login now.")
            st.session_state["signup_login_toggle"] = "login"

        except mysql.connector.Error as err:
            st.error(f"Database Error: {err}")

        finally:
            cursor.close()
            connection.close()

# ---------- LOGIN FUNCTION ---------- #
def login():
    st.image("pages/Images/dash.jpeg", width=600)
    st.title("Unlock the Future of Learning Powered by Gen AI, Fueled by Fun!")
    st.subheader("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hashed_password = hash_password(password)

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()

            if user:
                st.success(f"Welcome back, {username}!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                cursor.execute("SELECT last_login_date, streak FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()

                if result:
                    last_login_date, streak = result
                    today = datetime.now().date()

                    if last_login_date == today - timedelta(days=1):
                        streak += 1  
                    elif last_login_date != today:
                        streak = 1  

                    cursor.execute("UPDATE users SET last_login_date = %s, streak = %s WHERE username = %s", (today, streak, username))
                    connection.commit()

                    st.session_state["streak"] = streak
            else:
                st.error("Incorrect username or password.")

        except mysql.connector.Error as err:
            st.error(f"Database Error: {err}")

        finally:
            cursor.close()
            connection.close()

# ---------- LOGOUT FUNCTION ---------- #
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()

# ---------- MAIN APP FUNCTION ---------- #
def main_app():
    st.title("Welcome to GenPlay Arcade 🏫")

    st.subheader(f"Hello, {st.session_state['username']}! Gamify your learning experience🎮")

    streak = st.session_state.get("streak", 0)
    

    # Display Calendar View of Streak
    today = datetime.now().date()
    dates = pd.date_range(end=today, periods=30).tolist()
    streak_values = [1 if i < streak else 0 for i in range(30)][::-1]
    streak_data = pd.DataFrame({'Date': dates, 'Logged_In':  [int(value) for value in streak_values]})

    # Create a container for the heatmap to customize location
    with st.container():
        st.markdown("### 📅 Your Streak Calendar")

        fig = px.imshow(
        [streak_data['Logged_In'].values], 
        labels=dict(x="Date", color="Streak"), 
        x=[date.strftime('%d %b') for date in streak_data['Date']],
        color_continuous_scale=["#e0e0e0", "#007bff"],
        zmin=0,
        zmax=1,
        aspect="auto"  
        )
        fig.update_yaxes(showticklabels=False, title=None)

        fig.update_layout(
        width=700,  
        height=165,  
        margin=dict(l=20, r=10, t=30, b=10),
        coloraxis_colorbar=dict(
        tickmode="array",
        tickvals=[1],  
        ticktext=["Active"]
        )
        )

        st.plotly_chart(fig, use_container_width=False)
    
    # ---------- BACKGROUND & STYLES ----------
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom, #2e5caf, #add8e6); /* Matching gradient from the image */
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }
        h1 {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 2.5rem;
            color: white;
            text-align: center;
            margin-top: 20px;
        }     
        </style>
    """, unsafe_allow_html=True)

    # Redirect to Login if not authenticated
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You must log in first!")
        st.switch_page("login.py")

    st.markdown("Choose an option below:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📚 Your Courses"):
            st.switch_page("pages/course.py")

    with col2:
        if st.button("💬 Chat with PDF"):
            st.switch_page("pages/chatPDF.py")

    with col3:
        if st.button("🐍Word Serpent "):
            st.switch_page("pages/edugame.py")

    with col4:
        if st.button("📊 Dashbboard"):
            st.switch_page("pages/dashboard.py")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out!")
        st.switch_page("login.py")

# ---------- MAIN CONTROLLER ---------- #
def main():
    st.set_page_config(page_title="GenPlay Arcade", layout="centered")
    
    st.title("GENPLAY ARCADE")

    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #01b3ef, #2e5caf);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }
                .stButton>button {
                width: 100%;
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
                

    # Session state initialization
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "signup_login_toggle" not in st.session_state:
        st.session_state["signup_login_toggle"] = "login"

    # Show the dashboard if logged in
    if st.session_state["logged_in"]:
        main_app()
        return

    # Toggle between Login and Signup
    st.sidebar.title("Navigation")
    action = st.sidebar.radio("Go to", ("Login", "Sign Up"))

    if action == "Sign Up":
        st.session_state["signup_login_toggle"] = "signup"
    else:
        st.session_state["signup_login_toggle"] = "login"

    if st.session_state["signup_login_toggle"] == "signup":
        signup()
    else:
        login()

# ---------- RUN APP ---------- #
if __name__ == "__main__":
    main()
