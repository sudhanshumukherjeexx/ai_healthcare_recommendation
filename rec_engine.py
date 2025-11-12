
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# ---- Utility: safe read helpers ----
def _read_csv(path: str) -> Optional[pd.DataFrame]:
    try:
        if not Path(path).exists():
            return None
        df = pd.read_csv(path)
        return df
    except Exception:
        return None

def _read_excel(path: str) -> Optional[pd.DataFrame]:
    try:
        if not Path(path).exists():
            return None
        # Read first sheet by default
        df = pd.read_excel(path, sheet_name=0)
        return df
    except Exception:
        return None

def _find_user_key(df: pd.DataFrame) -> Optional[str]:
    for cand in ["USERID", "user_id", "userID", "UserID", "userId", "id"]:
        if cand in df.columns:
            return cand
    # fallbacks: look for something that looks like an id
    for c in df.columns:
        if "user" in c.lower() and "id" in c.lower():
            return c
    return None

@dataclass
class DataBundle:
    main: Optional[pd.DataFrame] = None
    pilot_user: Optional[pd.DataFrame] = None
    labs: Optional[pd.DataFrame] = None
    wearable: Optional[pd.DataFrame] = None
    microbiome: Optional[pd.DataFrame] = None
    metabolomics: Optional[pd.DataFrame] = None
    genomics: Optional[pd.DataFrame] = None
    meds: Optional[pd.DataFrame] = None
    surveys: Optional[pd.DataFrame] = None

    user_key: Optional[str] = None

    @classmethod
    def load(cls) -> "DataBundle":
        # All CSV files are in the data/ subdirectory, main.xlsx is in root
        data_dir = Path("data")
        
        bundle = cls(
            main=_read_excel("main.xlsx"),
            pilot_user=_read_csv(str(data_dir / "pilot_user_data.csv")),
            labs=_read_csv(str(data_dir / "structured_lab_results.csv")),
            wearable=_read_csv(str(data_dir / "wearable_daily_aggregates.csv")),
            microbiome=_read_csv(str(data_dir / "microbiome_summary.csv")),
            metabolomics=_read_csv(str(data_dir / "metabolomics_summary.csv")),
            genomics=_read_csv(str(data_dir / "genomic_summary.csv")),
            meds=_read_csv(str(data_dir / "medication_history.csv")),
            surveys=_read_csv(str(data_dir / "surveys_adherence_logs.csv")),
        )
        # deduce user key
        for df in [bundle.pilot_user, bundle.labs, bundle.wearable, bundle.microbiome, bundle.metabolomics, bundle.genomics, bundle.meds, bundle.surveys]:
            if df is not None:
                uk = _find_user_key(df)
                if uk:
                    bundle.user_key = uk
                    break
        return bundle

# ---- Profile extraction ----
def extract_user_profile(bundle: DataBundle, user_id: Any) -> Dict[str, Any]:
    profile = {"USERID": user_id, "sources": {}}

    def slice_user(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        if df is None: return None
        key = bundle.user_key or _find_user_key(df)
        if key and key in df.columns:
            return df[df[key] == user_id]
        return None

    profile["pilot_user"] = slice_user(bundle.pilot_user)
    profile["labs"] = slice_user(bundle.labs)
    profile["wearable"] = slice_user(bundle.wearable)
    profile["microbiome"] = slice_user(bundle.microbiome)
    profile["metabolomics"] = slice_user(bundle.metabolomics)
    profile["genomics"] = slice_user(bundle.genomics)
    profile["meds"] = slice_user(bundle.meds)
    profile["surveys"] = slice_user(bundle.surveys)

    # Aggregate concise signals
    signals = {}

    # Labs: basic markers (assume columns like 'marker', 'value', 'unit', 'flag')
    labs = profile["labs"]
    if labs is not None and not labs.empty:
        # find recent
        date_col = None
        for c in labs.columns:
            if "date" in c.lower():
                date_col = c; break
        if date_col:
            labs_sorted = labs.sort_values(date_col, ascending=False).head(50)
        else:
            labs_sorted = labs.head(50)
        signals["lab_flags_high"] = list(labs_sorted.columns)
        # Try to pick common markers if present
        for marker in ["Vitamin D", "Omega-3 Index", "LDL", "HDL", "CRP", "HbA1c", "Ferritin"]:
            col = None
            for c in labs.columns:
                if marker.lower().replace("-", "").replace(" ", "") in c.lower().replace("-", "").replace(" ", ""):
                    col = c; break
            if col:
                try:
                    # take the latest numeric value
                    val = pd.to_numeric(labs[col], errors="coerce").dropna()
                    if len(val) > 0:
                        signals[marker] = float(val.iloc[-1])
                except Exception:
                    pass

    # Wearables: try sleep/HRV/resting HR if present
    wearable = profile["wearable"]
    if wearable is not None and not wearable.empty:
        for metric in ["sleep_hours", "total_sleep", "hrv", "rhr", "resting_hr", "steps", "vo2max"]:
            cand = None
            for c in wearable.columns:
                if metric.replace("_","") in c.lower().replace("_",""):
                    cand = c; break
            if cand:
                try:
                    vals = pd.to_numeric(wearable[cand], errors="coerce").dropna()
                    if len(vals) > 0:
                        signals[f"wearable_{metric}_avg"] = float(vals.tail(14).mean())
                except Exception:
                    pass

    # Microbiome/metabolomics textual captures (diversity score, SCFA, etc. if present)
    microbiome = profile["microbiome"]
    if microbiome is not None and not microbiome.empty:
        for metric in ["diversity", "shannon", "butyrate", "scfa", "inflammation"]:
            cand = None
            for c in microbiome.columns:
                if metric in c.lower():
                    cand = c; break
            if cand:
                try:
                    vals = pd.to_numeric(microbiome[cand], errors="coerce").dropna()
                    if len(vals) > 0:
                        signals[f"microbiome_{metric}_avg"] = float(vals.mean())
                except Exception:
                    pass

    metabol = profile["metabolomics"]
    if metabol is not None and not metabol.empty:
        for metric in ["vitamin", "omega", "glucose", "carnitine", "amino"]:
            cand = None
            for c in metabol.columns:
                if metric in c.lower():
                    cand = c; break
            if cand:
                try:
                    vals = pd.to_numeric(metabol[cand], errors="coerce").dropna()
                    if len(vals) > 0:
                        signals[f"metabol_{metric}_avg"] = float(vals.mean())
                except Exception:
                    pass

    # Genomics: capture notable variants flags if present
    genom = profile["genomics"]
    if genom is not None and not genom.empty:
        variant_cols = [c for c in genom.columns if any(k in c.lower() for k in ["variant", "risk", "allele", "mutation", "snp"])]
        signals["genomic_flags"] = {}
        for c in variant_cols[:20]:
            # just record non-null unique values as flags
            vals = genom[c].dropna().unique().tolist()
            if len(vals) > 0:
                signals["genomic_flags"][c] = vals[:5]

    # Medications: list current meds if present
    meds = profile["meds"]
    if meds is not None and not meds.empty:
        name_col = None
        for c in meds.columns:
            if "med" in c.lower() or "drug" in c.lower() or "peptide" in c.lower():
                name_col = c; break
        if name_col:
            current = meds[name_col].dropna().astype(str).unique().tolist()
            signals["current_meds"] = current[:20]

    # Surveys: preferences, allergies, goals
    surveys = profile["surveys"]
    if surveys is not None and not surveys.empty:
        # try to pick common fields
        for tag in ["allergy", "goal", "avoid", "preference", "nootropic", "caffeine", "sleep", "diet"]:
            cols = [c for c in surveys.columns if tag in c.lower()]
            for col in cols:
                vals = surveys[col].dropna().astype(str).unique().tolist()
                if vals:
                    signals[f"survey_{col}"] = vals[:10]

    profile["signals"] = signals
    return profile


def assemble_user_dataframe(bundle: DataBundle, user_id: Any) -> Optional[pd.DataFrame]:
    """Check all CSV DataFrames for the user_id and return a merged DataFrame of all rows found.

    The merged DataFrame includes a small column `__source` that indicates which original
    table the row came from. Returns None if the user is not found in any data source.
    """
    parts = []
    src_map = {
        'pilot_user': bundle.pilot_user,
        'labs': bundle.labs,
        'wearable': bundle.wearable,
        'microbiome': bundle.microbiome,
        'metabolomics': bundle.metabolomics,
        'genomics': bundle.genomics,
        'meds': bundle.meds,
        'surveys': bundle.surveys,
    }

    for name, df in src_map.items():
        if df is None or df.empty:
            continue
        # determine key for this dataframe
        key = bundle.user_key or _find_user_key(df)
        if not key or key not in df.columns:
            continue
        try:
            user_rows = df[df[key] == user_id]
            if user_rows is None or user_rows.empty:
                continue
            # add source column to keep provenance
            temp = user_rows.copy()
            temp['__source'] = name
            parts.append(temp)
        except Exception:
            continue

    if not parts:
        return None
    try:
        merged = pd.concat(parts, ignore_index=True, sort=False)
        return merged
    except Exception:
        return None

# ---- Rule-based fallback recommender ----
def rule_based_recommendations(profile: Dict[str, Any], peptide_catalog: Optional[pd.DataFrame]) -> Dict[str, Any]:
    sig = profile.get("signals", {})
    recs = {"supplement_stack": [], "peptides": [], "nootropics": [], "notes": []}

    # Simple heuristics (non-medical guidance; informational only):
    vit_d = sig.get("Vitamin D")
    if isinstance(vit_d, float) and vit_d < 25:
        recs["supplement_stack"].append("Vitamin D3 + K2 (informational; confirm dosage with clinician)")
    omega = sig.get("Omega-3 Index")
    if isinstance(omega, float) and omega < 6:
        recs["supplement_stack"].append("Omega-3 (EPA/DHA) fish oil (informational)")
    crp = sig.get("CRP")
    if isinstance(crp, float) and crp > 3:
        recs["supplement_stack"].append("Anti-inflammatory focus: curcumin, magnesium glycinate (informational)")
    hrv = sig.get("wearable_hrv_avg")
    if isinstance(hrv, float) and hrv < 30:
        recs["supplement_stack"].append("Sleep + stress support: magnesium glycinate, L-theanine, ashwagandha (informational)")

    # Nootropics based on surveys (avoid if caffeine sensitive)
    caffeine_flags = []
    for k, v in sig.items():
        if "caffeine" in k.lower():
            caffeine_flags.extend([str(x).lower() for x in (v if isinstance(v, list) else [v])])
    caffeine_sensitive = any("sensitive" in x or "avoid" in x for x in caffeine_flags)
    if not caffeine_sensitive:
        recs["nootropics"].append("L-tyrosine (focus/alertness)")
        recs["nootropics"].append("Rhodiola rosea (fatigue)")
    recs["nootropics"].append("Citicoline (memory/attention)")

    # Peptide suggestions (informational only) from main.xlsx if has keywords
    if peptide_catalog is not None and not peptide_catalog.empty:
        # try to pick peptides by 'indication' like sleep, recovery, cognition
        lower_cols = {c.lower(): c for c in peptide_catalog.columns}
        text_cols = [lower_cols[c] for c in lower_cols if any(k in c for k in ["indication", "function", "description", "mechanism"])]
        name_col = lower_cols.get("name") or lower_cols.get("peptide") or list(peptide_catalog.columns)[0]
        def any_match(row, keywords):
            blob = " ".join(str(row[c]) for c in text_cols) if text_cols else " ".join(str(x) for x in row)
            blob_l = blob.lower()
            return any(k in blob_l for k in keywords)
        # if poor sleep/low HRV -> sleep/recovery
        if isinstance(hrv, float) and hrv < 30:
            for _, r in peptide_catalog.iterrows():
                if any_match(r, ["sleep", "recovery", "stress"]) and len(recs["peptides"]) < 5:
                    recs["peptides"].append(str(r.get(name_col, "Unknown")))
        # if cognition goals found in survey
        goals = []
        for k, v in sig.items():
            if "goal" in k.lower():
                goals.extend([str(x).lower() for x in (v if isinstance(v, list) else [v])])
        if any(g for g in goals if "focus" in g or "cognition" in g or "memory" in g):
            for _, r in peptide_catalog.iterrows():
                if any_match(r, ["cognition", "memory", "neuro", "brain"]) and len(recs["peptides"]) < 8:
                    recs["peptides"].append(str(r.get(name_col, "Unknown")))

    recs["notes"].append("These are informational ideas, not medical advice. Please consult a qualified clinician before starting peptides or supplements.")
    return recs

# ---- LLM wrapper (OpenAI) ----
def llm_recommendations(profile: Dict[str, Any], peptide_catalog_sample: List[Dict[str, Any]]) -> Optional[str]:
    
    # Load .env file if it exists
    dotenv_path = Path(".") / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

    # Now fetch key from BOTH .env and system env
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        sys_prompt = (
            "You are an expert health optimization assistant specializing in cutting-edge wellness and performance. "
            "You generate NON-medical, informational wellness suggestions only. "
            "YOU MUST add a clear disclaimer that this is informational only, not medical advice, and to consult a qualified clinician before acting.\n"
            "Provide recommendations in FOUR sections:\n"
            "1. POWER-PACKED SUPPLEMENT STACK - Include vitamins, minerals, amino acids, and specific dosage ranges (e.g., 200-400 mg daily) tailored to user's biomarkers and health signals\n"
            "2. THERAPEUTIC PEPTIDES - Recommend specific peptides (BPC-157, TB-500, Semax, Cerebrolysin, NAD+, etc.) with specific dosage ranges, personalized for user's recovery and cognitive needs\n"
            "3. NOOTROPICS - Cognitive enhancement compounds (L-theanine, rhodiola, bacopa, etc.) with specific dosage ranges for focus and mental performance\n"
            "4. GENERAL WELLNESS TIPS - Sleep optimization, exercise, stress management, nutrition, and lifestyle recommendations\n"
            "Be SPECIFIC with dosage ranges (e.g., 500-1000 mg daily, 200-400 mcg daily). "
            "Personalize ALL recommendations based on user's lab biomarkers, wearable metrics (sleep, HRV, steps), medications, and survey preferences. "
            "Avoid contraindications if possible using the provided medication list. "
            "Focus on power-packed, synergistic compound stacks that work well together."
        )
        # Build a compact merged-sample from profile['merged_df'] if available.
        merged_sample = None
        try:
            mdf = profile.get("merged_df")
            if mdf is not None and not mdf.empty:
                # select up to 8 informative columns (avoid internal __source) and up to 20 rows
                cols = [c for c in list(mdf.columns) if c != "__source"]
                cols = cols[:8]
                rows = min(20, len(mdf))
                merged_sample = [
                    {c: (None if pd.isna(r[c]) else r[c]) for c in cols}
                    for _, r in mdf.head(rows).iterrows()
                ]
        except Exception:
            merged_sample = None

        user_blob = json.dumps({
            "user_signals": profile.get("signals", {}),
            "current_meds": profile.get("signals", {}).get("current_meds", []),
            "survey_prefs": {k:v for k,v in profile.get("signals", {}).items() if "survey_" in k},
            "merged_user_rows": merged_sample,
            "peptide_catalog_sample": peptide_catalog_sample[:50],
        }, indent=2)
        msg = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Create recommendations for USERID={profile.get('USERID')} using this context:\n{user_blob}"}
        ]
        # Use responses API if available; fall back to chat.completions
        try:
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0.2)
            return resp.choices[0].message.content
        except Exception:
            resp = client.responses.create(model="gpt-4o-mini", input=msg, temperature=0.2)
            return resp.output_text
    except Exception:
        return None

def build_recommendations(user_id: Any) -> Dict[str, Any]:
    bundle = DataBundle.load()

    # First, verify the user exists in at least one data source and build a merged dataframe
    merged = assemble_user_dataframe(bundle, user_id)
    if merged is None:
        # user not found anywhere - short-circuit to avoid unnecessary LLM calls
        return {
            "engine": "no_data",
            "profile_signals": {},
            "message": f"User {user_id} not found in any data source."
        }

    # proceed to build the detailed profile (keeps per-source slices as well)
    profile = extract_user_profile(bundle, user_id)
    # attach merged dataframe for downstream use / debugging
    profile["merged_df"] = merged

    # Load peptide catalog (main.xlsx) and convert a tiny sample for the LLM
    peptide_catalog = bundle.main
    sample = []
    if peptide_catalog is not None and not peptide_catalog.empty:
        # Sample key columns to reduce prompt size
        cols = peptide_catalog.columns[:8].tolist()
        for _, r in peptide_catalog.head(80).iterrows():
            sample.append({c: (None if pd.isna(r[c]) else r[c]) for c in cols})

    # Try LLM first (if key present)
    llm_txt = llm_recommendations(profile, sample)
    if llm_txt is None:
        # Rule-based fallback
        recs = rule_based_recommendations(profile, peptide_catalog)
        return {"engine": "rule_based", "profile_signals": profile.get("signals", {}), "recommendations": recs}
    else:
        return {"engine": "llm", "profile_signals": profile.get("signals", {}), "recommendations_text": llm_txt}
