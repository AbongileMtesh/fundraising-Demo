import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== SESSION STATE INITIALIZATION  (streamlit run app.py)==========
if "users" not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=["id", "name", "email", "password", "role"])
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["id", "applicant_id", "faculty_options","department", "title", "description", "amount", "status", "date_submitted","time_period","proposal_needed"])
if "logs" not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=["id", "application_id", "changed_by", "old_status", "new_status", "date_changed"])
if "user" not in st.session_state:
    st.session_state.user = None

# ==== EMAIL CONFIGURATION ====
SENDER_EMAIL = "abpearl4@gmail.com"
SENDER_PASSWORD = "quzhdovrjkkyknpb"  # Use Gmail App Password (not your login password!)

# Faculty → Fundraiser email mapping
FACULTY_EMAIL_MAP = {
    "CBE": "amteshane@uj.ac.za",
    "FEBE": "sthobile@uj.ac.za",
    "FADA": "sthobile@uj.ac.za",
    "LAW": "sthobile@uj.ac.za",
    "SCI": "sthobile@uj.ac.za",
    "HSC": "mpontsho@uj.ac.za",
    "HUM": "sthobile@uj.ac.za",
    "EDU": "sthobile@uj.ac.za",
    "JBS": "sthobile@uj.ac.za"
}

# ========== UTILITY FUNCTIONS ==========
def register_user(name, email, password, role):
    if email in st.session_state.users["email"].values:
        st.warning("Email already registered!")
        return False
    new_user = pd.DataFrame([{
        "id": len(st.session_state.users) + 1,
        "name": name,
        "email": email,
        "password": password,
        "role": role
        
    }])
    st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
    st.success("Account created successfully!")
    return True

def login_user(email, password):
    users = st.session_state.users
    match = users[(users["email"] == email) & (users["password"] == password)]
    if not match.empty:
        st.session_state.user = match.iloc[0].to_dict()
        st.success(f"Welcome {st.session_state.user['name']} ({st.session_state.user['role']})")
        return True
    st.error("Invalid email or password.")
    return False

def submit_application(applicant_id, faculty_options,department, title, description, amount,time_period,proposal_needed):
    new_app = pd.DataFrame([{
        "id": len(st.session_state.applications) + 1,
        "applicant_id": applicant_id,
        "faculty_options": faculty_options,
        "department": department,
        "title": title,
        "description": description,
        "amount": amount,
        "status": "Submitted",
        "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "time_period" : time_period,
        "proposal_needed": proposal_needed
    }])
    st.session_state.applications = pd.concat([st.session_state.applications, new_app], ignore_index=True)
    st.success("Funding application submitted successfully!")

def update_status(application_id, new_status, changed_by):
    apps = st.session_state.applications
    old_status = apps.loc[apps["id"] == application_id, "status"].values[0]
    st.session_state.applications.loc[apps["id"] == application_id, "status"] = new_status
    
    new_log = pd.DataFrame([{
        "id": len(st.session_state.logs) + 1,
        "application_id": application_id,
        "changed_by": changed_by,
        "old_status": old_status,
        "new_status": new_status,
        "date_changed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    st.session_state.logs = pd.concat([st.session_state.logs, new_log], ignore_index=True)
    st.success(f"Status updated from '{old_status}' → '{new_status}'")

def send_email_to_fundraiser(faculty,Department, applicant_name, title, description, amount, time_period,proposal):
    """Send notification email to the fundraiser for the selected faculty."""
    if faculty not in FACULTY_EMAIL_MAP:
        st.warning("No fundraiser email found for this faculty.")
        return

    fundraiser_email = FACULTY_EMAIL_MAP[faculty]

    subject = f"New Funding Application from {applicant_name} ({faculty})"
    body = f"""
    Dear Fundraiser,

    A new funding application has been submitted for your faculty ({faculty}).

    📘 Department: {Department}
    📘 Project Title: {title}
    📝 Description: {description}
    💰 Requested Amount: R{amount:,.2f}
    ⏱️ Time Period: {time_period}
    👤 Applicant: {applicant_name}
    📝 Proposal needed: {proposal}

    Please log into the Fundraising System to review and update the application status.

    Kind regards,
    Fundraising Management System
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = fundraiser_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        #st.success(f"📨 Email sent successfully to {fundraiser_email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# ========== UI ==========
st.title("🎓 Fundraising Management System Demo")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ========== REGISTER ==========
if choice == "Register":
    st.subheader("Create an Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Applicant", "Fundraiser", "Admin"])
    
    if st.button("Register"):
        register_user(name, email, password, role)

# ========== LOGIN ==========
elif choice == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_user(email, password)

# ========== MAIN APP ==========
if st.session_state.user:
    user = st.session_state.user
    st.write("---")
    st.write(f"👤 Logged in as **{user['name']}** ({user['role']})")

    # APPLICANT VIEW
    if user["role"] == "Applicant":
        st.header("Apply for Funding")
        title = st.text_input("Project Title")
        description = st.text_area("Project Description")
        amount = st.number_input("Funding Amount Requested", min_value=0.0)
        # Faculty dropdown
        faculty_options = ["CBE", "FEBE", "FADA", "LAW", "SCI", "HSC", "HUM", "EDU", "JBS"]
        selected_faculty = st.selectbox("Select Faculty", faculty_options)
        
        department = st.text_area("Department")
        # Time Period dropdown
        time_period_options = ["4 months", "5 months", "6 months", "7 months", "8 months", "9 months", "10 months", "11 months", "1 year"]
        selected_period = st.selectbox("Select Time Period", time_period_options)

        proposal_needed = ["Yes","No"]
        selected_proposal = st.selectbox("Will you need a proposal?", proposal_needed)
        if st.button("Submit Funding Application"):
           submit_application(user["id"], selected_faculty,department, title, description, amount, selected_period,selected_proposal)
           send_email_to_fundraiser(selected_faculty,department ,user["name"], title, description, amount, selected_period,selected_proposal)


        st.write("### Your Funding Applications")
        my_apps = st.session_state.applications[st.session_state.applications["applicant_id"] == user["id"]]
        st.dataframe(my_apps[["id", "faculty_options","department","title", "description", "amount", "status", "date_submitted","time_period","proposal_needed"]])

        # FUNDRAISER VIEW
    elif user["role"] == "Fundraiser":
        st.header("Fundraiser Dashboard")

        # Find the faculty associated with this fundraiser's email
        user_email = user["email"]
        associated_faculty = None
        for faculty, fundraiser_email in FACULTY_EMAIL_MAP.items():
            if fundraiser_email.lower() == user_email.lower():
                associated_faculty = faculty
                break

        if not associated_faculty:
            st.warning("No faculty assigned to your email. Please contact the admin.")
        else:
            st.info(f"📘 You are assigned to **{associated_faculty}** faculty.")
            
            # Filter applications for this faculty
            apps = st.session_state.applications[
                st.session_state.applications["faculty_options"] == associated_faculty
            ]

            if apps.empty:
                st.write("No applications found for your faculty yet.")
            else:
                for _, app in apps.iterrows():
                    with st.expander(f"📁 {app['title']} (Status: {app['status']})"):
                        st.write(f"**Faculty:** {app['faculty_options']}")
                        st.write(f"**Department:** {app['department']}")
                        st.write(f"**Description:** {app['description']}")
                        st.write(f"**Amount Requested:** R{app['amount']:,}")
                        st.write(f"**Time Period:** {app['time_period']}")
                        st.write(f"**Proposal Needed:** {app['proposal_needed']}")
                        st.write(f"**Date Submitted:** {app['date_submitted']}")

                        new_status = st.selectbox(
                            "Update Status",
                            ["Submitted", "Proposal Stage", "Contract Stage", "Completed"],
                            key=f"status_{app['id']}"
                        )
                        if st.button(f"Update {app['title']}", key=f"btn_{app['id']}"):
                            update_status(app["id"], new_status, user["name"])
                            st.success(f"✅ Status updated for {app['title']}")


    # ADMIN VIEW
    elif user["role"] == "Admin":
        st.header("All Applications Overview")
        st.dataframe(st.session_state.applications)

        st.subheader("Activity Logs (Status Changes)")
        st.dataframe(st.session_state.logs)

        if st.button("Reset Demo Data"):
            st.session_state.applications = pd.DataFrame(columns=st.session_state.applications.columns)
            st.session_state.logs = pd.DataFrame(columns=st.session_state.logs.columns)
            st.success("All demo data reset!")

