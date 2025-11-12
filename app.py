
import os
import streamlit as st
import pandas as pd
from rec_engine import build_recommendations, DataBundle, assemble_user_dataframe

st.set_page_config(page_title="AI Wellness Recommendation Agent", page_icon="🧬", layout="wide")

st.title("🧬 AI Recommendation Agent (Supplements • Peptides • Nootropics)")
st.caption("Prototype — uses your uploaded datasets. For information only; not medical advice.")

with st.expander("ℹ️ How it works"):
    st.markdown("""
    1. Enter a `USERID` below.
    2. The app collects your data across the uploaded CSV/XLSX files (labs, wearables, surveys, etc.).
    3. If an `OPENAI_API_KEY` is set, it will draft an LLM-based plan; otherwise it uses a rule-based fallback.
    4. Output is **informational only**. Consult a qualified clinician before starting peptides or supplements.
    """)

user_id = st.text_input("Enter USERID", value="")

# buttons and merged-preview flow
colA, colB = st.columns([1,2])

with colA:
    if st.button("Find User", type="primary", disabled=(user_id.strip()=="" )):
        bundle = DataBundle.load()
        merged = assemble_user_dataframe(bundle, user_id.strip())
        st.session_state["merged_preview"] = merged

    merged = st.session_state.get("merged_preview")
    if merged is None and user_id.strip() != "":
        st.info("Click 'Find User' to search all data files for the provided USERID.")
    elif merged is not None:
        st.success(f"User found: {merged.shape[0]} rows across sources")
        # show a small preview and ask for confirmation before running the LLM
        with st.expander("Preview merged user data (first 10 rows)"):
            st.dataframe(merged.head(10))
        if st.button("Generate Recommendations for this user"):
            with st.spinner("Generating recommendations (LLM or fallback)..."):
                result = build_recommendations(user_id.strip())
            st.session_state["result"] = result

with colB:
    st.markdown("#### Data health check")
    bundle = DataBundle.load()
    files_ok = {
        "main.xlsx (peptide catalog)": bundle.main is not None and not bundle.main.empty,
        "pilot_user_data.csv": bundle.pilot_user is not None,
        "structured_lab_results.csv": bundle.labs is not None,
        "wearable_daily_aggregates.csv": bundle.wearable is not None,
        "microbiome_summary.csv": bundle.microbiome is not None,
        "metabolomics_summary.csv": bundle.metabolomics is not None,
        "genomic_summary.csv": bundle.genomics is not None,
        "medication_history.csv": bundle.meds is not None,
        "surveys_adherence_logs.csv": bundle.surveys is not None,
    }
    st.dataframe(pd.DataFrame({"file": list(files_ok.keys()), "loaded": list(files_ok.values())}))

st.markdown("---")

res = st.session_state.get("result")
if res:
    st.subheader("Your Recommendations")
    st.markdown(f"**Engine used:** `{res.get('engine')}`")

    with st.expander("Show extracted profile signals"):
        st.json(res.get("profile_signals", {}))

    if res.get("engine") == "llm":
        st.markdown(res.get("recommendations_text", ""))
    else:
        recs = res.get("recommendations", {})
        if recs:
            cols = st.columns(3)
            with cols[0]:
                st.markdown("### Supplement Stack (info)")
                st.write("\n".join(f"- {x}" for x in recs.get("supplement_stack", [])) or "_No items_")
            with cols[1]:
                st.markdown("### Peptides (info)")
                st.write("\n".join(f"- {x}" for x in recs.get("peptides", [])) or "_No items_")
            with cols[2]:
                st.markdown("### Nootropics (info)")
                st.write("\n".join(f"- {x}" for x in recs.get("nootropics", [])) or "_No items_")
            st.markdown("#### Notes")
            st.write("\n".join(f"- {x}" for x in recs.get("notes", [])))
    st.info("Disclaimer: This output is for **information only** and is **not medical advice**. Always consult a qualified clinician before making changes.")
