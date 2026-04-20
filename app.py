import streamlit as st
import json
from datetime import date

st.set_page_config(layout="wide")

DATA_FILE = "data.json"

# -------------------------
# LOAD / SAVE
# -------------------------

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data.setdefault("current_module", 0)
    data.setdefault("notes", "")

    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -------------------------
# CERTIFICATIONS + MODULES
# -------------------------

certifications = [
    {
        "name": "Cloud Practitioner + AI Practitioner",
        "start": "2026-04-20",
        "end": "2026-05-17",
        "modules": [
            "Intro to Cloud",
            "Compute (EC2, Lambda)",
            "Global Infrastructure",
            "Networking",
            "Storage",
            "Databases",
            "AI/ML Basics",
            "Security",
            "Monitoring",
            "Pricing",
            "Migration",
            "Well-Architected Framework"
        ]
    },
    {
        "name": "Solutions Architect Associate",
        "start": "2026-05-18",
        "end": "2026-07-12",
        "modules": [
            "Compute Deep Dive",
            "Storage Deep Dive",
            "Serverless Architecture",
            "Networking (VPC)",
            "Databases + Caching",
            "High Availability",
            "Security Deep Dive",
            "Cost Optimization"
        ]
    }
]

# Flatten modules
all_modules = []
for cert in certifications:
    all_modules.extend(cert["modules"])

# -------------------------
# HELPERS
# -------------------------

def get_current_cert():
    idx = data["current_module"]
    count = 0

    for cert in certifications:
        if idx < count + len(cert["modules"]):
            return cert, idx - count
        count += len(cert["modules"])

    return certifications[-1], 0

def get_today_task():
    idx = data["current_module"]
    if idx < len(all_modules):
        return all_modules[idx]
    return "Review / Practice"

def get_weekly_tasks():
    idx = data["current_module"]
    return all_modules[idx: idx + 5]

def complete_task():
    if data["current_module"] < len(all_modules):
        data["current_module"] += 1
        save_data(data)

# -------------------------
# SIDEBAR
# -------------------------

page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Courses",
    "Notes"
])

# -------------------------
# DASHBOARD
# -------------------------

if page == "Dashboard":
    st.title("🚀 AWS Learning Dashboard")

    cert, cert_idx = get_current_cert()

    st.subheader("🎯 Current Certification")
    st.info(f"{cert['name']}")

    col1, col2 = st.columns(2)
    col1.metric("Start Date", cert["start"])
    col2.metric("Target End", cert["end"])

    # -------------------------
    # MODULE PROGRESS
    # -------------------------

    st.subheader("📚 Modules Progress")

    for i, module in enumerate(cert["modules"]):
        status = "✅" if i < cert_idx else "⬜"
        st.write(f"{status} {module}")

    # -------------------------
    # TODAY
    # -------------------------

    st.subheader("📍 Today")
    st.write(f"👉 {get_today_task()}")

    if st.button("✅ Mark Complete"):
        complete_task()
        st.rerun()

    # -------------------------
    # WEEKLY PLAN
    # -------------------------

    st.subheader("📅 This Week")

    for task in get_weekly_tasks():
        st.write(f"• {task}")

    # -------------------------
    # PROGRESS
    # -------------------------

    progress = data["current_module"] / len(all_modules)

    st.subheader("📊 Overall Progress")
    st.progress(progress)

# -------------------------
# COURSES
# -------------------------

elif page == "Courses":
    st.title("📚 Certification Plan")

    certifications = [
        {
            "name": "Cloud Practitioner + AI Practitioner",
            "start": "2026-04-20",
            "end": "2026-05-17",
            "exam": ["Cloud: 2026-05-15", "AI: 2026-05-17"],
            "courses": [
                ("Cloud Practitioner Essentials", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials"),
                ("AWS Technical Essentials", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/185/aws-technical-essentials"),
                ("Generative AI Foundations", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/17996/generative-ai-foundations"),
                ("Amazon Bedrock Intro", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/17990/introduction-to-amazon-bedrock"),
                ("Coursera AWS Fundamentals", "https://www.coursera.org/specializations/aws-fundamentals")
            ],
            "modules": [
                "Intro to Cloud",
                "Compute (EC2, Lambda)",
                "Global Infrastructure",
                "Networking",
                "Storage",
                "Databases",
                "AI/ML Basics",
                "Security",
                "Monitoring",
                "Pricing",
                "Migration",
                "Well-Architected Framework"
            ]
        },
        {
            "name": "Solutions Architect Associate",
            "start": "2026-05-18",
            "end": "2026-07-12",
            "exam": ["SAA: 2026-07-12"],
            "courses": [
                ("Architecting on AWS", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/185/architecting-on-aws"),
                ("AWS Technical Essentials", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/185/aws-technical-essentials")
            ],
            "modules": [
                "Compute Deep Dive",
                "Storage Deep Dive",
                "Serverless Architecture",
                "Networking (VPC)",
                "Databases + Caching",
                "High Availability",
                "Security Deep Dive",
                "Cost Optimization"
            ]
        }
    ]

    for cert in certifications:
        with st.expander(f"🎯 {cert['name']}"):
            
            col1, col2 = st.columns(2)
            col1.write(f"📅 Start: {cert['start']}")
            col2.write(f"📅 End: {cert['end']}")

            st.write("🧪 Exam Dates:")
            for e in cert["exam"]:
                st.write(f"- {e}")

            st.subheader("📚 Courses")
            for name, link in cert["courses"]:
                st.markdown(f"[{name}]({link})")

            st.subheader("🧠 Modules")
            for m in cert["modules"]:
                st.write(f"• {m}")
# -------------------------
# NOTES
# -------------------------

elif page == "Notes":
    st.title("📝 Notes")

    data["notes"] = st.text_area("What did you learn today?", data["notes"], height=300)
    save_data(data)