import streamlit as st
import time

# Redirect to Login if not authenticated
if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You must log in first!")
        time.sleep(3)
        st.switch_page("login123.py")
        
st.set_page_config(page_title="Your Courses", page_icon="📚", layout="wide")

st.title("📚 Your Courses")

# ---------- BACKGROUND & STYLES ----------
st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to left, #ffffff, #2e5caf);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }
        .course-box {
            background-color: #ffffff;
            width: 50%;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
            margin-bottom: 15px;
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
        a {
            text-decoration: none;
            text-color:#ffffff;
            font-size: 15px;
            color:#ffffff;
            background-color: #ffffff;
            padding: 8px 12px;
            border-radius: 5px;
            
            margin-top: 10px;
        }
        a:hover {
            background-color: #000000;
            color: white;
        }
        input[type=checkbox] {
            appearance: none;
            width: 20px;
            height: 20px;
            border: 2px solid #ccc;
            border-radius: 3px;
            display: inline-block;
            cursor: pointer;
            margin-right: 10px;
            vertical-align: middle;
        }
        input[type=checkbox]:checked {
            background-color: #4CAF50;
            border-color: #4CAF50;
            position: relative;
        }
        input[type=checkbox]:checked::after {
            content: '✔';
            color: white;
            position: absolute;
            left: 3px;
            top: -2px;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

st.write("Here you'll find all your enrolled courses!")

# Courses list with links
courses = [
    {"name": "Python Basics", "link": "https://share.minicoursegenerator.com/from-zero-to-python-hero-your-journey-into-th-638793539152398025", "image": "pages/Images/Python programming.jpeg"},
    {"name": "Machine Learning with Python", "link": "https://share.minicoursegenerator.com/unlocking-the-power-of-data-mastering-machine-638793545291989177", "image": "pages/Images/ML with Python.jpeg"},
    {"name": "Data Science Essentials", "link": "https://share.minicoursegenerator.com/from-data-to-decisions-mastering-the-essentia-638793559767327294", "image": "pages/Images/data science.jpeg"},
    {"name": "Python for Data Science", "link": "https://share.minicoursegenerator.com/data-science-essentials-with-python-from-basi-638793627007592808", "image": "pages/Images/python for DS.jpeg"}
]

if "completed_courses" not in st.session_state:
    st.session_state.completed_courses = {course["name"]: False for course in courses}

for course in courses:
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(course["image"], use_container_width=True)
    
    with col2:
        st.subheader(course["name"])
        
        st.markdown(
            f"""
            <div class="course-box">
                <a href="{course["link"]}" target="_blank" onclick="sessionStorage.setItem('{course["name"]}_completed', 'true')">📖 Open {course["name"]}</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        checkbox_key = f"{course['name']}_checkbox"
        completed = st.session_state.completed_courses[course["name"]]

        # Render the checkbox
        if st.checkbox("Mark as Completed", key=checkbox_key):
            st.session_state.completed_courses[course["name"]] = True
            completed = True
        else:
            st.session_state.completed_courses[course["name"]] = False
            completed = False

        if completed:
            st.write("✅ Completed")

if st.button("⬅️Back"):
    st.switch_page("login.py")
