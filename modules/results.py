import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os

# ── API timeouts (seconds) ────────────────────────────────────────────────────
# The /predict endpoint runs a single 150-bp window through all 15 models.
PREDICT_TIMEOUT = 120
# The /predict_regions endpoint slides a 150-bp window across a longer sequence,
# calling /predict internally for every window – substantially more work.
PREDICT_REGIONS_TIMEOUT = 300

# ── pipeline step banner ──────────────────────────────────────────────────────

def _pipeline_banner(active: int) -> None:
    steps = ["1 · Input", "2 · Preprocess", "3 · Predict", "4 · Analyse"]
    classes = ["done" if i < active else ("active" if i == active else "") for i in range(len(steps))]
    html = "<div class='pipeline-steps'>" + "".join(
        f"<div class='step {cls}'>{label}</div>" for label, cls in zip(steps, classes)
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── property name loader ──────────────────────────────────────────────────────

def _load_property_names() -> dict:
    """Load property ID → name mapping from the bundled output file."""
    candidates = [
        Path("output (2).txt"),
        Path(__file__).parent.parent / "output (2).txt",
    ]
    for fp in candidates:
        if fp.exists():
            try:
                df = pd.read_csv(str(fp), sep=r"\t| {2,}", engine="python")
                return dict(zip(df["ID"].astype(str), df["PropertyName"]))
            except Exception:
                pass
    return {}


_PROPERTY_NAMES: dict = _load_property_names()


def _prop_label(prop_id) -> str:
    return _PROPERTY_NAMES.get(str(prop_id), f"Property {prop_id}")


# ── chart helpers ─────────────────────────────────────────────────────────────

def _model_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar showing Promoter (1) / Non-Promoter (0) per model."""
    colours = ["#06d6a0" if "Promoter ✅" in v else "#ef233c" for v in df["Prediction"]]
    fig = go.Figure(
        go.Bar(
            x=[1] * len(df),
            y=df["Model"],
            orientation="h",
            marker_color=colours,
            text=df["Prediction"],
            textposition="inside",
            insidetextanchor="middle",
        )
    )
    fig.update_layout(
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font_color="#caf0f8",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=11)),
        height=max(320, len(df) * 28),
        title=dict(text="Model Prediction Breakdown", font=dict(color="#48cae4", size=14)),
        showlegend=False,
    )
    return fig


def _vote_pie_chart(promoter_votes: int, total: int) -> go.Figure:
    non_votes = total - promoter_votes
    fig = go.Figure(
        go.Pie(
            labels=["Promoter", "Non-Promoter"],
            values=[promoter_votes, non_votes],
            hole=0.55,
            marker_colors=["#06d6a0", "#ef233c"],
            textfont=dict(color="#caf0f8"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0d1b2a",
        font_color="#caf0f8",
        margin=dict(l=10, r=10, t=30, b=10),
        height=260,
        showlegend=True,
        legend=dict(font=dict(color="#caf0f8")),
        title=dict(text="Ensemble Vote Distribution", font=dict(color="#48cae4", size=14)),
        annotations=[dict(
            text=f"{promoter_votes}/{total}",
            font=dict(size=18, color="#00b4d8"),
            showarrow=False,
        )],
    )
    return fig


def _confidence_gauge(agreement: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(agreement * 100, 1),
            number={"suffix": "%", "font": {"color": "#00b4d8", "size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#8ecae6"},
                "bar": {"color": "#0096c7"},
                "steps": [
                    {"range": [0, 40], "color": "#1e3a52"},
                    {"range": [40, 70], "color": "#023e5e"},
                    {"range": [70, 100], "color": "#034e68"},
                ],
                "threshold": {
                    "line": {"color": "#06d6a0", "width": 3},
                    "thickness": 0.75,
                    "value": 50,
                },
                "bgcolor": "#0d1b2a",
                "bordercolor": "#1e3a52",
            },
            title={"text": "Model Agreement", "font": {"color": "#48cae4", "size": 13}},
        )
    )
    fig.update_layout(
        paper_bgcolor="#0d1b2a",
        font_color="#caf0f8",
        margin=dict(l=10, r=10, t=20, b=10),
        height=220,
    )
    return fig


# ── main result pages ─────────────────────────────────────────────────────────

def show_results() -> None:
    _pipeline_banner(3)

    st.title("📊 Prediction Results")

    if "sequence" not in st.session_state or not st.session_state.get("sequence"):
        st.warning("⚠️ No sequence submitted. Please go to **📤 Upload & Predict** first.")
        st.stop()

    sequence = st.session_state["sequence"]
    organism = st.session_state.get("organism", "allorganism")

    # ── sequence info card ────────────────────────────────────────────────────
    with st.expander("🔎 Submitted sequence", expanded=False):
        colours = {"A": "#06d6a0", "T": "#ef233c", "G": "#ffd166", "C": "#48cae4"}
        fallback = "#caf0f8"
        coloured = "".join(
            f"<span style='color:{colours.get(b, fallback)}'>{b}</span>"
            for b in sequence
        )
        st.markdown(
            f"<div style='font-family:monospace;font-size:0.83rem;line-height:1.9;"
            f"word-break:break-all;background:#0a1628;border-radius:8px;padding:12px'>"
            f"{coloured}</div>",
            unsafe_allow_html=True,
        )

    # ── call API ──────────────────────────────────────────────────────────────
    FASTAPI_URL = "https://fastapiserver-2.onrender.com/predict"
    with st.spinner("🔬 Running ensemble prediction – please wait…"):
        try:
            response = requests.post(
                FASTAPI_URL,
                json={"sequence": sequence, "organism": organism},
                timeout=PREDICT_TIMEOUT,
            )
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            st.stop()

    # ── best property ─────────────────────────────────────────────────────────
    best_prop_id = results.get("best_property", "Unknown")
    best_prop_label = _prop_label(best_prop_id)

    # ── final prediction card ─────────────────────────────────────────────────
    final_pred = results.get("ensemble_prediction", 0)
    pred_text = "Promoter Sequence" if final_pred == 1 else "Non-Promoter Sequence"
    pred_icon = "✅" if final_pred == 1 else "❌"
    pred_color = "#06d6a0" if final_pred == 1 else "#ef233c"
    pred_bg = "#062b1e" if final_pred == 1 else "#2b0606"

    st.markdown(
        f"<div style='background:{pred_bg};border:2px solid {pred_color};"
        f"border-radius:14px;padding:24px 28px;text-align:center;margin:16px 0'>"
        f"<div style='font-size:2.8rem'>{pred_icon}</div>"
        f"<h2 style='color:{pred_color};margin:8px 0 4px'>{pred_text}</h2>"
        f"<p style='color:#caf0f8;margin:0'>Best kappa property used: "
        f"<strong style='color:#ffd166'>{best_prop_label}</strong></p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── model predictions ─────────────────────────────────────────────────────
    if isinstance(results.get("predictions"), dict):
        df = pd.DataFrame(
            [
                (k, "Promoter ✅" if v == 1 else "Non-Promoter ❌")
                for k, v in results["predictions"].items()
            ],
            columns=["Model", "Prediction"],
        )
        st.session_state["results_df"] = df

        total_models = len(df)
        promoter_votes = int((df["Prediction"] == "Promoter ✅").sum())
        agreement = promoter_votes / total_models

        # ── metrics row ───────────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total models", total_models)
        m2.metric("Promoter votes", promoter_votes)
        m3.metric("Non-promoter votes", total_models - promoter_votes)
        m4.metric("Agreement rate", f"{agreement:.0%}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── charts ────────────────────────────────────────────────────────────
        chart_left, chart_right = st.columns([2, 1], gap="large")
        with chart_left:
            st.plotly_chart(_model_bar_chart(df), use_container_width=True)
        with chart_right:
            st.plotly_chart(_vote_pie_chart(promoter_votes, total_models), use_container_width=True)
            st.plotly_chart(_confidence_gauge(agreement), use_container_width=True)

        # ── raw table ─────────────────────────────────────────────────────────
        with st.expander("📋 Full model predictions table", expanded=False):
            st.dataframe(
                df.style.applymap(
                    lambda x: "color: #06d6a0" if "Promoter ✅" in x else "color: #ef233c",
                    subset=["Prediction"],
                ),
                use_container_width=True,
                height=400,
            )
    else:
        st.error("Invalid predictions format received from the server.")

    # ── report download ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Download Report")
    if "report_path" in results:
        try:
            with open(results["report_path"], "r") as f:
                report_content = f.read()
            st.download_button(
                label="⬇️ Download Prediction Report (.txt)",
                data=report_content,
                file_name=f"{organism}_promoter_report.txt",
                mime="text/plain",
            )
        except FileNotFoundError:
            st.warning("Could not locate the report file on the server.")
        except Exception as e:
            st.error(f"Error generating report: {e}")
    else:
        st.warning("No downloadable report available for this prediction.")


def show_general_results() -> None:
    _pipeline_banner(3)

    st.title("📊 Generalized Prediction Results")

    if "sequence" not in st.session_state or not st.session_state.get("sequence"):
        st.warning("⚠️ No sequence submitted. Please go to **📤 Upload & Predict** first.")
        st.stop()

    sequence = st.session_state["sequence"]
    organism = st.session_state.get("organism", "allorganism")

    FASTAPI_GENERAL_URL = "http://127.0.0.1:8000/predict_regions"
    with st.spinner("🔬 Scanning sequence for promoter regions…"):
        try:
            response = requests.post(
                FASTAPI_GENERAL_URL,
                json={"sequence": sequence, "organism": organism},
                timeout=PREDICT_REGIONS_TIMEOUT,
            )
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            st.stop()

    # ── summary metrics ───────────────────────────────────────────────────────
    seq_len = results.get("input_sequence_length", len(sequence))
    regions = results.get("promoter_regions", [])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sequence length", f"{seq_len} bp")
    m2.metric("Promoter regions found", len(regions))
    m3.metric("Best precision", f"{results.get('best_precision', 0):.3f}")
    m4.metric("Best recall", f"{results.get('best_recall', 0):.3f}")

    # ── score profile chart ───────────────────────────────────────────────────
    score_profile = results.get("score_profile", [])
    if score_profile:
        fig_sp = go.Figure()
        fig_sp.add_trace(
            go.Scatter(
                y=score_profile,
                mode="lines",
                line=dict(color="#00b4d8", width=1.5),
                fill="tozeroy",
                fillcolor="rgba(0,180,216,0.15)",
                name="Score",
            )
        )
        # shade promoter regions
        for region in regions:
            fig_sp.add_vrect(
                x0=region["start"], x1=region["end"],
                fillcolor="rgba(6,214,160,0.2)",
                line_width=0,
                annotation_text="promoter",
                annotation_font_color="#06d6a0",
                annotation_font_size=9,
            )
        fig_sp.update_layout(
            paper_bgcolor="#0d1b2a",
            plot_bgcolor="#0d1b2a",
            font_color="#caf0f8",
            xaxis=dict(title="Position (bp)", color="#8ecae6"),
            yaxis=dict(title="Composite Score", color="#8ecae6"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=280,
            title=dict(text="Score Profile along Sequence", font=dict(color="#48cae4", size=14)),
        )
        st.plotly_chart(fig_sp, use_container_width=True)

    # ── highlighted sequence ──────────────────────────────────────────────────
    if regions:
        st.markdown("### 🔬 Highlighted Sequence (Promoter regions in <span style='color:#06d6a0'>green</span>)", unsafe_allow_html=True)
        highlight = [False] * len(sequence)
        for region in regions:
            for i in range(region.get("start", 0), region.get("end", 0) + 1):
                if i < len(sequence):
                    highlight[i] = True

        base_colours = {"A": "#06d6a0", "T": "#ef233c", "G": "#ffd166", "C": "#48cae4"}
        fallback2 = "#caf0f8"
        html_seq = ""
        for i, ch in enumerate(sequence):
            if highlight[i]:
                html_seq += (
                    f"<span style='background:#06d6a044;border-radius:2px;"
                    f"color:{base_colours.get(ch, fallback2)};font-weight:700'>{ch}</span>"
                )
            else:
                html_seq += f"<span style='color:{base_colours.get(ch, fallback2)}'>{ch}</span>"

        st.markdown(
            f"<div style='font-family:monospace;font-size:0.83rem;line-height:1.9;"
            f"word-break:break-all;background:#0a1628;border-radius:8px;padding:14px'>"
            f"{html_seq}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### 📋 Predicted Promoter Regions")
        for idx, region in enumerate(regions, 1):
            with st.expander(f"Region {idx}: positions {region.get('start')}–{region.get('end')}", expanded=False):
                st.code(region.get("region_sequence", ""), language=None)
                st.caption(f"Length: {region.get('end', 0) - region.get('start', 0) + 1} bp")
    else:
        st.info("ℹ️ No potential promoter regions were identified in the submitted sequence.")


if __name__ == "__main__":
    show_general_results()

