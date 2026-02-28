import streamlit as st
from modules.home import show_home
from modules.upload import show_upload
from modules.results import show_results, show_general_results
from modules.about import show_about

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenPromPredict – Promoter Prediction System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS (teal/dark-navy theme, inspired by NonBFinder) ────────────────
st.markdown(
    """
    <style>
    /* ── base palette ── */
    :root {
        --bg-primary:    #0d1b2a;
        --bg-secondary:  #112233;
        --accent-teal:   #00b4d8;
        --accent-cyan:   #48cae4;
        --accent-green:  #06d6a0;
        --accent-red:    #ef233c;
        --accent-yellow: #ffd166;
        --text-primary:  #e0f4ff;
        --text-muted:    #8ecae6;
        --card-bg:       #16283d;
        --border:        #1e3a52;
    }

    /* ── app shell ── */
    .stApp { background-color: var(--bg-primary); color: var(--text-primary); }

    /* ── sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0d2137 100%);
        border-right: 2px solid var(--border);
    }
    section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; padding: 6px 0; }

    /* ── pipeline step banner ── */
    .pipeline-steps {
        display: flex;
        gap: 0;
        margin-bottom: 1.4rem;
        border-radius: 8px;
        overflow: hidden;
    }
    .step {
        flex: 1;
        text-align: center;
        padding: 10px 4px;
        font-size: 0.78rem;
        font-weight: 600;
        background: var(--card-bg);
        color: var(--text-muted);
        border-right: 1px solid var(--border);
        letter-spacing: 0.04em;
    }
    .step:last-child { border-right: none; }
    .step.active {
        background: linear-gradient(90deg, #005f73, #0a9396);
        color: #ffffff;
    }
    .step.done {
        background: #023e5e;
        color: var(--accent-cyan);
    }

    /* ── cards ── */
    .info-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }
    .info-card h3 { color: var(--accent-teal); margin-top: 0; }

    /* ── metric badges ── */
    div[data-testid="metric-container"] {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px;
    }
    div[data-testid="metric-container"] label { color: var(--text-muted) !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--accent-teal) !important;
        font-size: 1.6rem !important;
    }

    /* ── buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0077b6, #0096c7);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.6rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0, 180, 216, 0.4);
    }

    /* ── dataframe ── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ── headings ── */
    h1 { color: var(--accent-teal) !important; letter-spacing: 0.02em; }
    h2 { color: var(--accent-cyan) !important; }
    h3 { color: var(--text-primary) !important; }

    /* ── dividers ── */
    hr { border-color: var(--border); }

    /* ── success / warning / error ── */
    div[data-testid="stAlert"] { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:8px 0 18px'>"
        "<span style='font-size:2.4rem'>🧬</span>"
        "<h2 style='color:#00b4d8;margin:4px 0 2px;font-size:1.15rem'>GenPromPredict</h2>"
        "<p style='color:#8ecae6;font-size:0.78rem;margin:0'>Advanced Promoter Prediction</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📤 Upload & Predict", "📊 Results", "ℹ️ About"],
        key="navigation_app",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<p style='color:#8ecae6;font-size:0.72rem;text-align:center'>"
        "Powered by 15 ML models · kappa-encoding · FastAPI backend</p>",
        unsafe_allow_html=True,
    )

# ── Page routing ─────────────────────────────────────────────────────────────
if page == "🏠 Home":
    show_home()
elif page == "📤 Upload & Predict":
    show_upload()
elif page == "📊 Results":
    if not st.session_state.get("generalized", False):
        show_results()
    else:
        show_general_results()
elif page == "ℹ️ About":
    show_about()