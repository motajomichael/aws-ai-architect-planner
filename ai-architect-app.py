import streamlit as st
import json
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

DATA_FILE = "data.json"
today = datetime.today().date()

# -------------------------
# DATE FORMATTER
# -------------------------

def format_date(dt):
    return dt.strftime("%A, %d %B %Y")

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
    data.setdefault("delay_days", 0)
    data.setdefault("base_start_date", "2026-04-16")

    # NEW
    data.setdefault("weekly_time", 0)
    data.setdefault("history", {})
    data.setdefault("streak", 0)
    data.setdefault("last_completed_date", None)
    data.setdefault("last_study_date", None)
    data.setdefault("light_mode", False)

    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -------------------------
# BASE DATE
# -------------------------

base_start = datetime.strptime(data["base_start_date"], "%Y-%m-%d")

# -------------------------
# CERT BUILDER
# -------------------------

timeline = []
cursor = base_start

def add_cert(name, weeks, modules, courses):
    global cursor

    start = cursor
    end = start + timedelta(days=weeks * 7)
    exam = end

    timeline.append({
        "name": name,
        "start": start,
        "end": end,
        "exam": exam,
        "modules": modules,
        "courses": courses
    })

    cursor = end + timedelta(days=1)

# -------------------------
# CERTIFICATIONS (UNCHANGED)
# -------------------------

add_cert("Cloud Practitioner",3,
["Intro to Cloud","Compute","Networking","Storage","Databases","Security","Pricing"],
[("Cloud Practitioner Essentials","https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials")])

add_cert("AI Practitioner",2,
["Intro to AI","LLMs","Prompt Engineering","Bedrock","Use Cases"],
[("Generative AI Foundations","https://explore.skillbuilder.aws/learn/course/external/view/elearning/17996/generative-ai-foundations"),
 ("Amazon Bedrock Intro","https://explore.skillbuilder.aws/learn/course/external/view/elearning/17990/introduction-to-amazon-bedrock")])

add_cert("Solutions Architect Associate",8,
["Compute","Storage","Serverless","Networking","Databases","HA","Security","Cost"],
[("Architecting on AWS","https://explore.skillbuilder.aws/learn/course/external/view/elearning/185/architecting-on-aws")])

add_cert("Developer Associate",4,
["Lambda","API Gateway","SDK","Events","Auth"],
[("Developing on AWS","https://explore.skillbuilder.aws/learn/course/external/view/elearning/186/developing-on-aws")])

add_cert("Data Engineer Associate",8,
["Data Lakes","ETL","Glue","Athena","Streaming"],
[("Data Analytics Fundamentals","https://explore.skillbuilder.aws/learn/course/external/view/elearning/123/data-analytics-fundamentals")])

add_cert("SysOps Associate",4,
["Monitoring","Logging","Scaling","Security"],
[("Systems Operations on AWS","https://explore.skillbuilder.aws/learn/course/external/view/elearning/189/systems-operations-on-aws")])

add_cert("DevOps Professional",8,
["CI/CD","Automation","Deployments","IaC"],
[("DevOps Engineering on AWS","https://explore.skillbuilder.aws/learn/course/external/view/elearning/190/devops-engineering-on-aws")])

add_cert("Solutions Architect Professional",6,
["Multi-region","Hybrid","Enterprise"],
[("Advanced Architecting on AWS","https://explore.skillbuilder.aws/learn/course/external/view/elearning/194/advanced-architecting-on-aws")])

add_cert("Generative AI Professional",6,
["LLMs","Embeddings","RAG"],
[("Generative AI Learning Plan","https://explore.skillbuilder.aws/learn/public/learning_plan/view/2193/generative-ai-learning-plan")])

all_modules = [m for cert in timeline for m in cert["modules"]]

# -------------------------
# HELPERS
# -------------------------

def get_current_cert():
    idx = data["current_module"]
    count = 0

    for cert in timeline:
        if idx < count + len(cert["modules"]):
            return cert, idx - count
        count += len(cert["modules"])

    return timeline[-1], 0

def get_today_task():
    today_str = str(today)

    if data["last_completed_date"] == today_str:
        idx = max(data["current_module"] - 1, 0)
    else:
        idx = data["current_module"]

    return all_modules[idx] if idx < len(all_modules) else "Review"

def get_tomorrow_task():
    return all_modules[data["current_module"]] if data["current_module"] < len(all_modules) else "Review"

def get_weekly_tasks():
    return all_modules[data["current_module"]:data["current_module"]+5]

def get_duration(task):
    if data["light_mode"]:
        return 30

    t = task.lower()
    if "intro" in t: return 45
    if "compute" in t or "storage" in t: return 75
    if "ai" in t: return 60
    return 60

# -------------------------
# PROGRESS FUNCTIONS
# -------------------------

def update_streak():
    today_str = str(today)

    if data["last_study_date"] == today_str:
        return

    if data["last_study_date"]:
        last = datetime.strptime(data["last_study_date"], "%Y-%m-%d").date()
        if last == today - timedelta(days=1):
            data["streak"] += 1
        else:
            data["streak"] = 1
    else:
        data["streak"] = 1

    data["last_study_date"] = today_str

def log_time(minutes):
    today_str = str(today)
    data["weekly_time"] += minutes
    data["history"][today_str] = data["history"].get(today_str, 0) + minutes
    update_streak()
    save_data(data)

def complete_task():
    today_str = str(today)

    if data["last_completed_date"] == today_str:
        return

    duration = get_duration(get_today_task())

    data["current_module"] += 1
    data["last_completed_date"] = today_str

    log_time(duration)

def undo_today():
    today_str = str(today)

    if data["last_completed_date"] != today_str:
        return

    data["current_module"] -= 1
    data["last_completed_date"] = None

    if today_str in data["history"]:
        data["weekly_time"] -= data["history"][today_str]
        del data["history"][today_str]

    save_data(data)

# -------------------------
# AI COACH
# -------------------------

def ai_coach():
    tips = []

    if data["streak"] >= 5:
        tips.append("🔥 Strong consistency. Protect your streak.")
    elif data["streak"] == 0:
        tips.append("Start small today. Momentum matters more than intensity.")

    if data["weekly_time"] < 120:
        tips.append("Increase weekly study time slightly (30–60 mins/day).")

    if data["delay_days"] > 0:
        tips.append(f"You are {data['delay_days']} days behind. Add 10–15 mins daily.")

    if data["light_mode"]:
        tips.append("Light mode is fine — just don’t stay there too long.")

    return tips

# -------------------------
# HEATMAP (GitHub style)
# -------------------------

def render_heatmap(history):
    if not history:
        st.info("No study data yet")
        return

    df = pd.DataFrame(list(history.items()), columns=["date","minutes"])
    df["date"] = pd.to_datetime(df["date"])

    end = datetime.today()
    start = end - timedelta(days=90)

    all_days = pd.date_range(start=start, end=end)
    full = pd.DataFrame({"date": all_days})
    full = full.merge(df, on="date", how="left").fillna(0)

    full["week"] = full["date"].dt.isocalendar().week
    full["day"] = full["date"].dt.weekday

    pivot = full.pivot(index="day", columns="week", values="minutes")

    fig, ax = plt.subplots(figsize=(12,3))
    ax.imshow(pivot, aspect="auto")
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    ax.set_xticks([])

    st.pyplot(fig)

# -------------------------
# SIDEBAR
# -------------------------

page = st.sidebar.radio("Navigation", ["Dashboard","Courses","Notes"])

data["light_mode"] = st.sidebar.checkbox("⚖️ Light Day Mode", value=data["light_mode"])

delay = st.sidebar.number_input("Days Behind", 0, 30, 0)
if st.sidebar.button("Adjust Timeline"):
    data["delay_days"] += delay
    save_data(data)

# -------------------------
# DASHBOARD
# -------------------------

if page == "Dashboard":
    st.title("🚀 AWS Learning Dashboard")

    cert, progress = get_current_cert()

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("🔥 Streak", data["streak"])
    col2.metric("📊 Weekly Time", f"{data['weekly_time']} mins")
    col3.metric("⏳ Days to Exam", (cert["exam"] - datetime.today()).days)
    col4.metric("Progress", f"{progress}/{len(cert['modules'])}")

    st.progress(progress / len(cert["modules"]))

    st.subheader("📍 Today")
    today_task = get_today_task()
    st.write(f"👉 {today_task}")
    st.write(f"⏱ {get_duration(today_task)} mins")

    already_done = data["last_completed_date"] == str(today)

    colA,colB = st.columns(2)

    with colA:
        if already_done:
            st.success("Completed today")
        else:
            if st.button("Complete Task"):
                complete_task()
                st.rerun()

    with colB:
        if already_done:
            if st.button("Undo"):
                undo_today()
                st.rerun()

    st.subheader("➕ Extra / Partial Study")

    extra = st.number_input("Minutes", 0, 180, 30)
    if st.button("Log Study"):
        log_time(extra)

    st.subheader("🔜 Tomorrow")
    st.write(get_tomorrow_task())

    st.subheader("🤖 AI Coach")
    for tip in ai_coach():
        st.write("•", tip)

    st.subheader("📅 Study Heatmap")
    render_heatmap(data["history"])

# -------------------------
# COURSES (UNCHANGED)
# -------------------------

elif page == "Courses":
    st.title("📚 Certification Plan")

    for cert in timeline:
        with st.expander(cert["name"]):

            st.write(
                "📅",
                format_date(cert["start"]),
                "→",
                format_date(cert["end"] + timedelta(days=data["delay_days"]))
            )

            st.write(
                "🧪 Exam:",
                format_date(cert["exam"] + timedelta(days=data["delay_days"]))
            )

            st.subheader("📚 Courses")
            for name, link in cert["courses"]:
                st.markdown(f"[{name}]({link})")

            # ✅ THIS IS WHAT WAS MISSING
            st.subheader("🧠 Modules")
            for m in cert["modules"]:
                st.write(f"• {m}")

# -------------------------
# NOTES (UNCHANGED)
# -------------------------

elif page == "Notes":
    st.title("📝 Notes")
    data["notes"] = st.text_area("Notes", data["notes"])
    save_data(data)