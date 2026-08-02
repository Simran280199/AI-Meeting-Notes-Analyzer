import streamlit as st
from state import MeetingState
from graph import graph

# ---------- Page config ----------
st.set_page_config(
    page_title="AI Meeting Notes Analyzer",
    page_icon="🗒️",
    layout="centered"
)

# ---------- Custom dark/techy styling ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;700&display=swap');

    .main .block-container {
        max-width: 780px;
        padding-top: 2.5rem;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0b0e14 !important;
    }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0b0e14 !important;
    }
    .app-subtitle, p, label, .stMarkdown {
        color: #c7cad1 !important;
    }

    .app-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7c5cff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        color: #7d8394;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
        font-family: 'Inter', sans-serif;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #7c5cff;
        margin-top: 1.8rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid #7c5cff;
        padding-left: 8px;
    }

    .topic-tag {
        display: inline-block;
        background-color: rgba(124, 92, 255, 0.12);
        border: 1px solid rgba(124, 92, 255, 0.4);
        color: #b3a3ff;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-family: 'JetBrains Mono', monospace;
        margin: 0 6px 6px 0;
    }

    .priority-badge {
        display: inline-block;
        padding: 7px 18px;
        border-radius: 6px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        letter-spacing: 0.04em;
    }
    .priority-high {
        background-color: rgba(255, 69, 96, 0.12);
        color: #ff4560;
        border: 1px solid rgba(255, 69, 96, 0.4);
        box-shadow: 0 0 12px rgba(255, 69, 96, 0.25);
    }
    .priority-medium {
        background-color: rgba(255, 176, 32, 0.12);
        color: #ffb020;
        border: 1px solid rgba(255, 176, 32, 0.4);
        box-shadow: 0 0 12px rgba(255, 176, 32, 0.25);
    }
    .priority-low {
        background-color: rgba(0, 230, 150, 0.12);
        color: #00e696;
        border: 1px solid rgba(0, 230, 150, 0.4);
        box-shadow: 0 0 12px rgba(0, 230, 150, 0.25);
    }
    .priority-na {
        background-color: rgba(125, 131, 148, 0.12);
        color: #7d8394;
        border: 1px solid rgba(125, 131, 148, 0.4);
    }

    .action-item {
        padding: 12px 16px;
        background-color: #141821;
        border: 1px solid #262b38;
        border-left: 3px solid #7c5cff;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #e6e8ee;
    }
    .action-owner {
        color: #7d8394;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        margin-top: 4px;
        display: block;
    }

    .stButton > button {
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid #262b38;
    }
    .stTextArea textarea {
        background-color: #141821 !important;
        color: #e6e8ee !important;
        caret-color: #e6e8ee !important;
        border: 1px solid #262b38;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
    .stTextArea textarea::placeholder {
        color: #4a5063 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Sample transcript ----------
SAMPLE_TRANSCRIPT = """John: We need to improve the website performance.
Sarah: Yes, page load time is too slow.
David: I will optimize the database queries this week.
Sarah: I will redesign the homepage layout.
John: Let's try to finish these tasks before Friday."""

# ---------- Header ----------
st.markdown('<div class="app-title">&gt; AI_Meeting_Notes_Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Paste or upload a transcript to extract topics, a summary, '
    'action items, and priority — powered by a LangGraph agent pipeline.</div>',
    unsafe_allow_html=True
)

# ---------- Input area ----------
if "transcript_input" not in st.session_state:
    st.session_state.transcript_input = ""

uploaded_file = st.file_uploader("Upload a transcript (.txt)", type=["txt"])
if uploaded_file is not None:
    st.session_state.transcript_input = uploaded_file.read().decode("utf-8")

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("Use sample transcript", use_container_width=True):
        st.session_state.transcript_input = SAMPLE_TRANSCRIPT
with col_b:
    if st.button("Clear", use_container_width=True):
        st.session_state.transcript_input = ""

transcript = st.text_area(
    "Meeting transcript",
    value=st.session_state.transcript_input,
    height=260,
    placeholder="Paste your meeting transcript here...",
    label_visibility="collapsed"
)

analyze_clicked = st.button("Analyze Meeting", type="primary", use_container_width=True)

# ---------- Run the pipeline ----------
if analyze_clicked:
    if not transcript.strip():
        st.warning("Please paste or upload a transcript first.")
    else:
        with st.spinner("Analyzing transcript... running the agent pipeline"):
            initial_state: MeetingState = {
                "transcript": transcript,
                "topics": [],
                "summary": "",
                "action_items": [],
                "priority": "",
                "final_report": ""
            }
            result = graph.invoke(initial_state)

        st.success("Analysis complete")

        # --- Topics ---
        st.markdown('<div class="section-label">Topics Discussed</div>', unsafe_allow_html=True)
        tags_html = "".join(f'<span class="topic-tag">{t}</span>' for t in result["topics"])
        st.markdown(tags_html, unsafe_allow_html=True)

        # --- Summary ---
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        st.write(result["summary"])

        # --- Action Items ---
        st.markdown('<div class="section-label">Action Items</div>', unsafe_allow_html=True)
        if result["action_items"]:
            for item in result["action_items"]:
                st.markdown(
                    f'<div class="action-item">{item["task"]}'
                    f'<span class="action-owner">Owner: {item["owner"]}</span></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No action items identified in this meeting.")

        # --- Priority ---
        st.markdown('<div class="section-label">Priority</div>', unsafe_allow_html=True)
        priority_value = result["priority"] or "Not applicable"
        priority_class = {
            "High": "priority-high",
            "Medium": "priority-medium",
            "Low": "priority-low"
        }.get(priority_value, "priority-na")
        st.markdown(
            f'<span class="priority-badge {priority_class}">{priority_value}</span>',
            unsafe_allow_html=True
        )

        # --- Raw report (for copying / download) ---
        with st.expander("View plain-text report"):
            st.text(result["final_report"])
        st.download_button(
            "Download report as .txt",
            data=result["final_report"],
            file_name="meeting_report.txt",
            mime="text/plain"
        )