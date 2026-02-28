import streamlit as st
from Bio import SeqIO
import io

# ── helpers ──────────────────────────────────────────────────────────────────

def _pipeline_banner(active: int) -> None:
    steps = ["1 · Input", "2 · Preprocess", "3 · Predict", "4 · Analyse"]
    classes = ["done" if i < active else ("active" if i == active else "") for i in range(len(steps))]
    html = "<div class='pipeline-steps'>" + "".join(
        f"<div class='step {cls}'>{label}</div>" for label, cls in zip(steps, classes)
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


SAMPLE_SEQUENCE = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"[:150]


def validate_sequence_general(sequence: str) -> str | None:
    """Check if sequence is at least 150 bases and contains only A, T, G, C."""
    sequence = sequence.strip().upper()
    if len(sequence) < 150:
        return "The sequence must be at least 150 bases long."
    if any(base not in "ATGC" for base in sequence):
        return "The sequence must only contain A, T, G, or C."
    return None


def validate_sequence_exact(sequence: str) -> str | None:
    """Check if the sequence is exactly 150 bases and contains only A, T, G, C."""
    sequence = sequence.strip().upper()
    if len(sequence) != 150:
        return f"The sequence must be exactly 150 bases long (currently {len(sequence)} bases)."
    if any(base not in "ATGC" for base in sequence):
        return "The sequence must only contain A, T, G, or C."
    return None


def extract_fasta_sequence(fasta_file, min_length: int = 150, exact_length: bool = True):
    """Extracts sequences from a FASTA file and ensures they meet the criteria."""
    try:
        fasta_content = fasta_file.read().decode("utf-8")
        fasta_io = io.StringIO(fasta_content)
        sequences = [str(record.seq).strip().upper() for record in SeqIO.parse(fasta_io, "fasta")]
        if not sequences:
            return None, "The FASTA file does not contain any valid sequences."
        for seq in sequences:
            error = validate_sequence_exact(seq) if exact_length else validate_sequence_general(seq)
            if error:
                return None, error
        return sequences[0], None
    except Exception as e:
        return None, f"Error processing FASTA file: {e}"


# ── callback functions ────────────────────────────────────────────────────────

def update_specific_sequence() -> None:
    if st.session_state.sequence_input:
        st.session_state.sequence = st.session_state.sequence_input.strip().upper()


def update_general_sequence() -> None:
    if st.session_state.general_sequence_input:
        st.session_state.sequence = st.session_state.general_sequence_input.strip().upper()


def update_specific_file() -> None:
    if st.session_state.fasta_upload is not None:
        seq, err = extract_fasta_sequence(st.session_state.fasta_upload)
        if seq:
            st.session_state.sequence = seq.strip().upper()


def update_general_file() -> None:
    if st.session_state.general_fasta_upload is not None:
        seq, err = extract_fasta_sequence(st.session_state.general_fasta_upload, min_length=150, exact_length=False)
        if seq:
            st.session_state.sequence = seq.strip().upper()


# ── main page ─────────────────────────────────────────────────────────────────

def show_upload() -> None:
    _pipeline_banner(0)

    st.title("📤 Upload & Predict")
    st.markdown(
        "<p style='color:#8ecae6;font-size:0.95rem;margin-top:-12px'>"
        "Submit your nucleotide sequence to run the full ensemble prediction pipeline.</p>",
        unsafe_allow_html=True,
    )

    # ── session-state defaults ────────────────────────────────────────────────
    for key, default in [("sequence", ""), ("organism", ""), ("generalized", False)]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── input section ─────────────────────────────────────────────────────────
    st.markdown(
        "<div class='info-card'>"
        "<h3 style='margin-top:0'>📋 Sequence Input</h3>"
        "<p style='color:#8ecae6;font-size:0.87rem;margin-bottom:0'>"
        "Provide a <strong>150-base</strong> DNA sequence (A, T, G, C only) or upload "
        "a FASTA file containing a single 150-base record.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    input_col, hint_col = st.columns([2, 1], gap="large")

    with input_col:
        input_option = st.radio(
            "Input method",
            ("✍️ Paste sequence", "📁 Upload FASTA file"),
            key="input_method",
            horizontal=True,
        )

        if input_option == "✍️ Paste sequence":
            st.text_area(
                "Nucleotide sequence (exactly 150 bases):",
                height=130,
                key="sequence_input",
                on_change=update_specific_sequence,
                placeholder="e.g. ATGCATGC… (150 bases)",
            )
            # live character counter
            seq_len = len(st.session_state.get("sequence", ""))
            bar_pct = min(seq_len / 150, 1.0)
            color = "#06d6a0" if seq_len == 150 else ("#ffd166" if seq_len > 0 else "#8ecae6")
            st.markdown(
                f"<div style='background:#16283d;border-radius:4px;height:6px;margin-bottom:4px'>"
                f"<div style='background:{color};width:{bar_pct*100:.1f}%;height:6px;border-radius:4px'></div>"
                f"</div>"
                f"<span style='color:{color};font-size:0.78rem'>{seq_len} / 150 bases</span>",
                unsafe_allow_html=True,
            )
        else:
            st.file_uploader(
                "FASTA file (.fasta / .fa / .txt):",
                type=["fasta", "fa", "txt"],
                key="fasta_upload",
                on_change=update_specific_file,
            )
            if st.session_state.sequence:
                st.caption(f"Loaded sequence: {len(st.session_state.sequence)} bases")

    with hint_col:
        st.markdown(
            "<div class='info-card' style='background:#0a2235'>"
            "<h3 style='color:#ffd166;font-size:0.95rem'>⚠️ Requirements</h3>"
            "<ul style='color:#caf0f8;font-size:0.82rem;padding-left:16px;line-height:1.8'>"
            "<li>Exactly <strong>150 bases</strong></li>"
            "<li>Only <code>A</code>, <code>T</code>, <code>G</code>, <code>C</code></li>"
            "<li>No gaps, spaces or special characters</li>"
            "<li>FASTA: one record, 150 bases</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("🔬 Load sample sequence", key="sample_btn", use_container_width=True):
            st.session_state.sequence = SAMPLE_SEQUENCE
            st.session_state.sequence_input = SAMPLE_SEQUENCE
            st.rerun()

    # ── preview ───────────────────────────────────────────────────────────────
    if st.session_state.sequence:
        with st.expander("🔎 Sequence preview", expanded=False):
            seq = st.session_state.sequence
            # colour-code bases
            colours = {"A": "#06d6a0", "T": "#ef233c", "G": "#ffd166", "C": "#48cae4"}
            fallback = "#caf0f8"
            coloured = "".join(
                f"<span style='color:{colours.get(b, fallback)}'>{b}</span>" for b in seq
            )
            st.markdown(
                f"<div style='font-family:monospace;font-size:0.85rem;line-height:1.9;"
                f"word-break:break-all;background:#0a1628;border-radius:8px;padding:12px'>"
                f"{coloured}</div>",
                unsafe_allow_html=True,
            )
            # base composition
            comp_cols = st.columns(4)
            for col, base, clr in zip(comp_cols, ["A", "T", "G", "C"],
                                      ["#06d6a0", "#ef233c", "#ffd166", "#48cae4"]):
                pct = seq.count(base) / len(seq) * 100 if seq else 0
                col.markdown(
                    f"<div style='text-align:center;background:#16283d;border-radius:8px;padding:8px'>"
                    f"<div style='color:{clr};font-size:1.2rem;font-weight:700'>{base}</div>"
                    f"<div style='color:#caf0f8;font-size:0.85rem'>{pct:.1f}%</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── submit ────────────────────────────────────────────────────────────────
    submit_col, _ = st.columns([1, 2])
    with submit_col:
        submitted = st.button("🚀 Run Prediction", key="submit_button", use_container_width=True)

    if submitted:
        errors = []
        if input_option == "✍️ Paste sequence":
            err = validate_sequence_exact(st.session_state.sequence)
            if err:
                errors.append(err)
        else:
            if st.session_state.get("fasta_upload") is None:
                errors.append("Please upload a FASTA file.")

        if errors:
            for err in errors:
                st.warning(f"⚠️ {err}")
        else:
            st.session_state.organism = "allorganism"
            st.session_state.generalized = False
            st.success(
                "✅ Sequence submitted! Navigate to **📊 Results** in the sidebar to view predictions.",
                icon="✅",
            )

