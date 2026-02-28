import streamlit as st
from typing import Optional


def _pipeline_banner(active: Optional[int]) -> None:
    steps = ["1 · Input", "2 · Preprocess", "3 · Predict", "4 · Analyse"]
    classes = [
        "done" if (active is not None and i < active)
        else ("active" if active == i else "")
        for i in range(len(steps))
    ]
    html = "<div class='pipeline-steps'>" + "".join(
        f"<div class='step {cls}'>{label}</div>" for label, cls in zip(steps, classes)
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def show_about() -> None:
    _pipeline_banner(None)  # no active step – informational page

    st.title("ℹ️ About GenPromPredict")

    # ── Architecture overview ─────────────────────────────────────────────────
    st.markdown(
        """
        <div class='info-card'>
        <h3>🏗️ System Architecture</h3>
        <p style='color:#caf0f8;line-height:1.8'>
        GenPromPredict follows a <strong>client–server pipeline</strong> architecture
        inspired by NonBFinder and similar bioinformatics web tools:
        </p>
        <ul style='color:#caf0f8;line-height:1.9;padding-left:18px'>
          <li><strong style='color:#48cae4'>Streamlit frontend</strong> – multi-page navigation
              with a persistent sidebar, pipeline step breadcrumbs, and interactive widgets.</li>
          <li><strong style='color:#48cae4'>FastAPI backend</strong> – stateless REST API hosted
              on Render (<code>fastapiserver-2.onrender.com</code>) that handles sequence
              encoding, model loading from Hugging Face Hub, prediction, and report generation.</li>
          <li><strong style='color:#48cae4'>Hugging Face Hub</strong> – trained model files
              (pickle / XGBoost JSON / CatBoost CBM) are fetched on-demand and cached locally.</li>
          <li><strong style='color:#48cae4'>Ensemble voting</strong> – 15 classifiers vote
              independently; the majority decision is returned as the final prediction.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Pipeline steps ────────────────────────────────────────────────────────
    st.markdown("### 🔄 Prediction Pipeline")
    cols = st.columns(4)
    pipeline_steps = [
        ("1️⃣", "Input", "User submits a 150-base DNA sequence or FASTA file via the Upload page."),
        ("2️⃣", "Preprocess", "Sequence is validated, cleaned, and kappa-encoded into a 149-feature numerical vector."),
        ("3️⃣", "Predict", "All 15 classifiers run inference; individual predictions are collected."),
        ("4️⃣", "Analyse", "Ensemble vote is computed, results visualised with charts and a downloadable report."),
    ]
    for col, (icon, title, desc) in zip(cols, pipeline_steps):
        col.markdown(
            f"<div class='info-card' style='text-align:center'>"
            f"<div style='font-size:2rem'>{icon}</div>"
            f"<h3 style='color:#00b4d8;font-size:1rem;margin:6px 0'>{title}</h3>"
            f"<p style='color:#caf0f8;font-size:0.82rem'>{desc}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Encoding method ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div class='info-card'>
        <h3>🔬 Kappa-Property Encoding</h3>
        <p style='color:#caf0f8;line-height:1.8'>
        Each DNA sequence is encoded using a <em>2-mer sliding window</em> approach.
        For every consecutive di-nucleotide (e.g. AT, GC…) the corresponding
        <strong>kappa physicochemical property value</strong> is looked up from a
        curated 125-property database.  The window slides one base at a time over
        the full 150-base sequence, producing <strong>149 numerical features</strong>
        that capture local structural and thermodynamic characteristics of the DNA.
        </p>
        <p style='color:#8ecae6;font-size:0.85rem'>
        The best-performing kappa property for each organism was pre-selected by
        ranking all 125 properties on a held-out validation set and choosing the
        one that maximised ensemble F1-score.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ML models ─────────────────────────────────────────────────────────────
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """
            <div class='info-card'>
            <h3>🤖 Classifier Ensemble</h3>
            <ul style='color:#caf0f8;line-height:1.9;padding-left:18px;font-size:0.9rem'>
              <li>Support Vector Machine (SVM)</li>
              <li>Random Forest</li>
              <li>Logistic Regression</li>
              <li>Naïve Bayes</li>
              <li>K-Nearest Neighbors</li>
              <li>Gradient Boosting</li>
              <li>AdaBoost</li>
              <li>Decision Tree</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class='info-card'>
            <h3>&nbsp;</h3>
            <ul style='color:#caf0f8;line-height:1.9;padding-left:18px;font-size:0.9rem'>
              <li>Perceptron</li>
              <li>Stochastic Gradient Descent (SGD)</li>
              <li>Bagging Classifier</li>
              <li>Extra Trees Classifier</li>
              <li>CatBoost</li>
              <li>LightGBM</li>
              <li>XGBoost</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Dataset & training ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class='info-card'>
        <h3>📚 Dataset &amp; Training</h3>
        <ul style='color:#caf0f8;line-height:1.8;padding-left:18px'>
          <li>Promoter sequences (150 bp upstream of TSS) were collected from
              <strong>15 bacterial/archaeal genomes</strong>.</li>
          <li>Negative examples were generated by randomly sampling
              non-promoter intergenic regions of the same length.</li>
          <li>Each model was trained independently on each organism's dataset
              and saved as a serialised model file on Hugging Face Hub.</li>
          <li>Model files are fetched at prediction time and cached locally to
              minimise latency on repeated queries.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<p style='color:#8ecae6;font-size:0.8rem;text-align:center'>"
        "GenPromPredict · Built with Streamlit &amp; FastAPI · "
        "Models hosted on Hugging Face Hub</p>",
        unsafe_allow_html=True,
    )
