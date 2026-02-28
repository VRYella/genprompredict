import streamlit as st


# ── pipeline step helper ──────────────────────────────────────────────────────
def _pipeline_banner(active: int) -> None:
    """Render a 4-step pipeline breadcrumb (0-indexed active step)."""
    steps = ["1 · Input", "2 · Preprocess", "3 · Predict", "4 · Analyse"]
    classes = []
    for i in range(len(steps)):
        if i < active:
            classes.append("done")
        elif i == active:
            classes.append("active")
        else:
            classes.append("")
    html = "<div class='pipeline-steps'>" + "".join(
        f"<div class='step {cls}'>{label}</div>"
        for label, cls in zip(steps, classes)
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── organism data ─────────────────────────────────────────────────────────────
ORGANISMS = {
    "Haloferax volcanii DS2": ("https://en.wikipedia.org/wiki/Haloferax_volcanii", "🌊", "Archaea", "Halophilic archaeon"),
    "Helicobacter pylori 26695": ("https://en.wikipedia.org/wiki/Helicobacter_pylori", "🦠", "Bacteria", "Gastric pathogen"),
    "Klebsiella pneumoniae MGH 78578": ("https://en.wikipedia.org/wiki/Klebsiella_pneumoniae", "🧫", "Bacteria", "Clinical isolate"),
    "Mycobacterium tuberculosis H37Rv": ("https://en.wikipedia.org/wiki/Mycobacterium_tuberculosis", "⚕️", "Bacteria", "TB causative agent"),
    "Nostoc sp. PCC 7120": ("https://en.wikipedia.org/wiki/Nostoc", "🌿", "Cyanobacteria", "Nitrogen fixer"),
    "Pseudomonas aeruginosa UCBPP-PA14": ("https://en.wikipedia.org/wiki/Pseudomonas_aeruginosa", "🔬", "Bacteria", "Opportunistic pathogen"),
    "Saccharolobus solfataricus P2": ("https://en.wikipedia.org/wiki/Sulfolobus_solfataricus", "🌋", "Archaea", "Thermoacidophile"),
    "Salmonella enterica SL1344": ("https://en.wikipedia.org/wiki/Salmonella", "⚠️", "Bacteria", "Enteric pathogen"),
    "Streptomyces coelicolor A3(2)": ("https://en.wikipedia.org/wiki/Streptomyces_coelicolor", "🧬", "Bacteria", "Antibiotic producer"),
    "Synechocystis sp. PCC 6803": ("https://en.wikipedia.org/wiki/Synechocystis", "☀️", "Cyanobacteria", "Model phototroph"),
    "Thermococcus kodakarensis KOD1": ("https://en.wikipedia.org/wiki/Thermococcus_kodakarensis", "🔥", "Archaea", "Hyperthermophile"),
    "Bacillus amyloliquefaciens XH7": ("https://en.wikipedia.org/wiki/Bacillus_amyloliquefaciens", "🌾", "Bacteria", "Plant growth promoter"),
    "Chlamydia pneumoniae CWL029": ("https://en.wikipedia.org/wiki/Chlamydia_pneumoniae", "🫁", "Bacteria", "Respiratory pathogen"),
    "Corynebacterium glutamicum ATCC 13032": ("https://en.wikipedia.org/wiki/Corynebacterium_glutamicum", "🏭", "Bacteria", "Industrial workhorse"),
    "Escherichia coli MG1655": ("https://en.wikipedia.org/wiki/Escherichia_coli", "⚗️", "Bacteria", "Model organism"),
}

ML_MODELS = [
    ("SVM", "Support Vector Machine"),
    ("RF", "Random Forest"),
    ("LR", "Logistic Regression"),
    ("NB", "Naïve Bayes"),
    ("KNN", "K-Nearest Neighbors"),
    ("GB", "Gradient Boosting"),
    ("ADA", "AdaBoost"),
    ("DT", "Decision Tree"),
    ("PER", "Perceptron"),
    ("SGD", "Stochastic Gradient Descent"),
    ("BAG", "Bagging Classifier"),
    ("ET", "Extra Trees"),
    ("CAT", "CatBoost"),
    ("LGBM", "LightGBM"),
    ("XGB", "XGBoost"),
]


def show_home() -> None:
    _pipeline_banner(0)

    # ── Hero section ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#023e58 0%,#0a4f6e 100%);
                    border-radius:14px;padding:32px 36px;margin-bottom:28px;
                    border:1px solid #1e3a52;">
          <h1 style="color:#00b4d8;margin:0 0 10px;font-size:2.2rem">
            🧬 GenPromPredict
          </h1>
          <p style="color:#caf0f8;font-size:1.05rem;margin:0 0 14px">
            An advanced, ensemble machine-learning pipeline for bacterial and archaeal
            <strong style="color:#48cae4">promoter sequence prediction</strong>.
            Trained on 15 organisms using <em>kappa-encoding</em> of 150-base upstream
            sequences.
          </p>
          <div style="display:flex;gap:20px;flex-wrap:wrap">
            <span style="background:#034e68;border-radius:20px;padding:5px 14px;
                         color:#90e0ef;font-size:0.82rem">🦠 15 Organisms</span>
            <span style="background:#034e68;border-radius:20px;padding:5px 14px;
                         color:#90e0ef;font-size:0.82rem">🤖 15 ML Models</span>
            <span style="background:#034e68;border-radius:20px;padding:5px 14px;
                         color:#90e0ef;font-size:0.82rem">⚡ Ensemble Voting</span>
            <span style="background:#034e68;border-radius:20px;padding:5px 14px;
                         color:#90e0ef;font-size:0.82rem">📊 150-bp window</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stats row ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Organisms", "15", delta="archaea + bacteria")
    with col2:
        st.metric("ML Models", "15", delta="ensemble voting")
    with col3:
        st.metric("Sequence window", "150 bp", delta="kappa-encoded")
    with col4:
        st.metric("Encoding features", "149", delta="2-mer sliding window")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────────────────────────────
    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown("### 🌍 Supported Organisms")
        st.markdown(
            "<p style='color:#8ecae6;font-size:0.85rem;margin-top:-8px'>"
            "Click any organism name to visit its Wikipedia article.</p>",
            unsafe_allow_html=True,
        )
        for name, (url, icon, domain, desc) in ORGANISMS.items():
            st.markdown(
                f"<div class='info-card' style='padding:12px 16px;margin-bottom:8px;"
                f"display:flex;align-items:center;gap:12px'>"
                f"<span style='font-size:1.4rem'>{icon}</span>"
                f"<div><a href='{url}' target='_blank' style='color:#48cae4;"
                f"text-decoration:none;font-weight:600'>{name}</a>"
                f"<br><span style='color:#8ecae6;font-size:0.78rem'>"
                f"{domain} · {desc}</span></div></div>",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("### 🤖 Machine-Learning Models")
        st.markdown(
            "<p style='color:#8ecae6;font-size:0.85rem;margin-top:-8px'>"
            "15 classifiers contribute to the final ensemble vote.</p>",
            unsafe_allow_html=True,
        )
        # display as 3-column grid
        rows = [ML_MODELS[i:i+3] for i in range(0, len(ML_MODELS), 3)]
        for row in rows:
            cols = st.columns(3)
            for col, (abbr, full) in zip(cols, row):
                col.markdown(
                    f"<div class='info-card' style='padding:10px 12px;text-align:center'>"
                    f"<div style='color:#00b4d8;font-weight:700;font-size:1rem'>{abbr}</div>"
                    f"<div style='color:#caf0f8;font-size:0.72rem'>{full}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("### 🔬 How It Works")
        st.markdown(
            """
            <div class='info-card'>
            <ol style="color:#caf0f8;padding-left:18px;line-height:1.9">
              <li>Upload a <strong>150-base</strong> nucleotide sequence or FASTA file.</li>
              <li>The best <em>kappa-property</em> for the target organism is selected.</li>
              <li>Sequence is encoded into a <strong>149-feature</strong> numerical vector.</li>
              <li>All 15 classifiers independently predict promoter vs. non-promoter.</li>
              <li>A <strong>majority-vote ensemble</strong> yields the final call.</li>
              <li>Full prediction breakdown and downloadable report are provided.</li>
            </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

