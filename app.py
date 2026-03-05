import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Trust Ecology Diagnostic Dashboard", layout="wide", page_icon="🛡️")

# --- Custom CSS for Dashboard Styling ---
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border-left: 4px solid #ccc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card.critical { border-left-color: #dc3545; background: #fff5f5; }
    .metric-card.moderate { border-left-color: #ffc107; background: #fffbeb; }
    .metric-card.resilient { border-left-color: #28a745; background: #f0fff4; }
    .metric-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
    .metric-label { font-size: 0.9rem; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-status { font-size: 0.85rem; margin-top: 0.3rem; }
    .intervention-card { 
        border: 1px solid #e0e0e0; 
        border-radius: 8px; 
        padding: 1rem; 
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .cascade-warning {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .header-dashboard {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .export-section {
        background: #e8f4fd;
        border: 1px solid #b3d9ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-dashboard"><h1 style="margin:0;">🛡️ TRUST ECOLOGY DIAGNOSTIC DASHBOARD</h1><p style="margin:0.5rem 0 0 0; opacity:0.9;">Hor (2026) • Triadic, Processual Trust Calibration</p></div>', unsafe_allow_html=True)

# --- Disclaimer Banner ---
st.warning("⚠️ Draft / Pre-Validation • For research & diagnostic use only • Not for high-stakes regulatory compliance")

# --- Sidebar: Instructions ---
st.sidebar.header("📘 How to Use")
st.sidebar.markdown("""
1. **Reflect** on a recent AI-assisted decision in your work.
2. **Rate** each statement (1 = Strongly Disagree, 5 = Strongly Agree).
3. **Optional**: Complete the Critical Incident section if you experienced a trust violation.
4. **Click** "Generate Dashboard" to view your Trust Configuration Report.
5. **Export** your results using the download buttons at the bottom.

*Final validated version expected 2026.*
""")

if st.sidebar.button("🔄 Retake Assessment"):
    st.cache_data.clear()
    st.rerun()

# --- Survey Function with Silent Reverse-Item Handling ---
def survey_section(title, items, key_prefix, reverse_indices=None):
    st.subheader(title)
    scores = []
    for i, item in enumerate(items):
        # Display item without "(Reverse)" label
        display_text = item.replace(" (Reverse)", "").replace("(Reverse) ", "")
        raw = st.slider(f"{i+1}. {display_text}", 1, 5, 3, key=f"{key_prefix}_{i}")
        # Silent inversion for reverse-coded items: 1→5, 2→4, 3→3, 4→2, 5→1
        if reverse_indices and i in reverse_indices:
            scores.append(6 - raw)
        else:
            scores.append(raw)
    return np.mean(scores)

# --- Session State for Storing Results ---
if 'results_generated' not in st.session_state:
    st.session_state.results_generated = False
if 'assessment_data' not in st.session_state:
    st.session_state.assessment_data = {}

# --- Survey Items (1–5 Scale, Reverse Items Handled Silently) ---
st.header("Part 1: Assessment")

# Section 1: AI Explicability (Cognitive Trust) - Item 5 is reverse-coded
explicability_items = [
    "The AI performs reliably in uncertain situations.",
    "The AI provides clear explanations for its recommendations.",
    "I can understand the reasoning behind the AI's outputs.",
    "Explicable outputs from the AI reduce my doubts about its competence.",
    "The AI's decisions often feel like a black box to me."
]
explicability_score = survey_section("Section 1: AI Explicability (Cognitive Trust)", explicability_items, "exp", reverse_indices=[4])

# Section 2: Human Stewardship (Relational Trust) - Item 5 is reverse-coded
stewardship_items = [
    "The decision-maker demonstrates integrity when interpreting AI outputs.",
    "The leader prioritizes stakeholder well-being in AI decisions.",
    "The decision-maker communicates AI-related decisions with empathy.",
    "The decision-maker's expertise builds my confidence in the process.",
    "I sometimes question whether the decision-maker truly oversees the AI."
]
stewardship_score = survey_section("Section 2: Human Stewardship (Relational Trust)", stewardship_items, "stew", reverse_indices=[4])

# Section 3: Systemic Legitimacy (Outcome Fairness) - Item 5 is reverse-coded
legitimacy_items = [
    "The outcome equitably distributes benefits and burdens.",
    "The decision process was transparent and procedurally fair.",
    "Affected parties were treated with respect.",
    "I had a meaningful opportunity to raise concerns about the decision.",
    "The final outcome felt unfair to those affected."
]
legitimacy_score = survey_section("Section 3: Systemic Legitimacy (Outcome Fairness)", legitimacy_items, "leg", reverse_indices=[4])

# Section 4: Interconnected Trust (Exploratory) - No reverse items
interconnect_items = [
    "When the AI makes an error, my trust in the human decision-maker also decreases.",
    "Fair outcomes make me more willing to rely on both the AI and the supervisor.",
    "The human steward's integrity compensates when AI explanations are unclear.",
    "Unfair outcomes make me question whether the AI was biased, even if technically accurate.",
    "I trust the AI more when I know there is strong human oversight.",
    "When both the AI and human agree but the outcome is unjust, I lose faith in the entire system."
]
interconnect_score = survey_section("Section 4: Interconnected Trust (Exploratory)", interconnect_items, "int")

# --- Optional: Retrospective Critical Incident Technique ---
with st.expander("🔍 Optional: Critical Incident Reflection", expanded=False):
    st.markdown("*Answer with reference to a specific trust-violating incident.*")
    
    col_a, col_b = st.columns(2)
    with col_a:
        recovery_scale = ["Hours", "Days", "Weeks", "Months", "Never recovered"]
        q1 = st.selectbox("1. AI trust recovery time", recovery_scale, key="rit_q1")
        q3 = st.slider("3. Doubt AI reliability after incident?", 1, 5, 3, key="rit_q3")
        q5 = st.slider("5. Future acceptance of AI recommendations?", 1, 5, 3, key="rit_q5", help="1=Less likely, 5=More likely")
    with col_b:
        q2 = st.selectbox("2. Human trust recovery time", recovery_scale, key="rit_q2")
        q4 = st.slider("4. Doubt decision-maker integrity after incident?", 1, 5, 3, key="rit_q4")
        q6 = st.multiselect("6. What helped restore trust?", ["Correction", "Apology", "Policy change", "Recourse", "Leadership advocacy", "Time", "Other"], key="rit_q6")
    q7 = st.text_area("7. Additional details (optional)", key="rit_q7")
    q8 = st.radio("8. Did fairness of later outcomes restore confidence?", ["Yes", "No", "Unsure"], key="rit_q8")

# --- Generate Dashboard Button ---
st.markdown("---")
if st.button("📊 Generate Trust Configuration Report", type="primary", use_container_width=True):
    
    # Store results in session state for export
    st.session_state.results_generated = True
    
    # --- Scoring & Status Logic (1–5 Scale) ---
    def get_status(score):
        if score < 2.5:
            return "✕ Critical", "critical", "#dc3545"
        elif score < 3.5:
            return "◐ Moderate", "moderate", "#ffc107"
        else:
            return "✓ Resilient", "resilient", "#28a745"
    
    def get_status_label(score):
        label, css_class, color = get_status(score)
        return label
    
    # Calculate Overall Trust Index (mean of core triad)
    overall_score = np.mean([explicability_score, stewardship_score, legitimacy_score])
    
    # Store assessment data for export
    st.session_state.assessment_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scores": {
            "AI Explicability": round(explicability_score, 2),
            "Human Stewardship": round(stewardship_score, 2),
            "Systemic Legitimacy": round(legitimacy_score, 2),
            "Interconnected Trust": round(interconnect_score, 2),
            "Overall Trust Index": round(overall_score, 2)
        },
        "status": {
            "AI Explicability": get_status_label(explicability_score)[0],
            "Human Stewardship": get_status_label(stewardship_score)[0],
            "Systemic Legitimacy": get_status_label(legitimacy_score)[0],
            "Overall Trust Index": get_status_label(overall_score)[0]
        },
        "critical_incident": {
            "completed": True,
            "ai_recovery": q1,
            "human_recovery": q2,
            "doubt_ai": q3,
            "doubt_human": q4,
            "future_acceptance": q5,
            "restoration_mechanisms": q6,
            "qualitative_note": q7,
            "systemic_recovery": q8
        } if 'q1' in locals() else {"completed": False}
    }
    
    # --- DASHBOARD HEADER: Trust Configuration Report ---
    st.subheader("📋 Trust Configuration Report")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        label, css_class, color = get_status(explicability_score)
        st.markdown(f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">AI Explicability</div>
            <div class="metric-value" style="color:{color}">{explicability_score:.1f}</div>
            <div class="metric-status">{label}</div>
            <div style="font-size:0.8rem; color:#777;">{explicability_score:.1f}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        label, css_class, color = get_status(stewardship_score)
        st.markdown(f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">Human Stewardship</div>
            <div class="metric-value" style="color:{color}">{stewardship_score:.1f}</div>
            <div class="metric-status">{label}</div>
            <div style="font-size:0.8rem; color:#777;">{stewardship_score:.1f}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        label, css_class, color = get_status(legitimacy_score)
        st.markdown(f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">Systemic Legitimacy</div>
            <div class="metric-value" style="color:{color}">{legitimacy_score:.1f}</div>
            <div class="metric-status">{label}</div>
            <div style="font-size:0.8rem; color:#777;">{legitimacy_score:.1f}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        label, css_class, color = get_status(overall_score)
        st.markdown(f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">Overall Trust Index</div>
            <div class="metric-value" style="color:{color}">{overall_score:.1f}</div>
            <div class="metric-status">{label}</div>
            <div style="font-size:0.8rem; color:#777;">{overall_score:.1f}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    # --- Score Breakdown Table ---
    st.markdown("### 📈 Dimension Scores")
    score_df = pd.DataFrame({
        'Dimension': ['AI Explicability', 'Human Stewardship', 'Systemic Legitimacy'],
        'Score': [explicability_score, stewardship_score, legitimacy_score],
        'Status': [get_status_label(explicability_score), get_status_label(stewardship_score), get_status_label(legitimacy_score)]
    })
    st.dataframe(score_df, use_container_width=True, hide_index=True)
    
    # --- Cascade Risk Detection ---
    scores_list = [explicability_score, stewardship_score, legitimacy_score]
    score_range = max(scores_list) - min(scores_list)
    
    if score_range >= 2.0:
        st.markdown(f"""
        <div class="cascade-warning">
            <strong>⚠️ Cascade Risk Detected</strong><br>
            The spread of {score_range:.1f} points across your three dimensions indicates <strong>high cascade risk</strong>. 
            Per the Trust Ecology Framework's attributional reappraisal mechanism, a critical fracture in your lowest-scoring dimension 
            is likely to retroactively erode confidence in your higher-scoring dimensions. 
            <strong>Fix the lowest dimension first</strong> — improvements in higher dimensions will have limited impact until the critical fracture is addressed.
        </div>
        """, unsafe_allow_html=True)
    
    # --- Evidence-Based Intervention Guidance ---
    st.subheader("🎯 Evidence-Based Intervention Guidance")
    st.markdown("*Priority order: Address critical fractures first to prevent cascade effects.*")
    
    interventions = [
        ("AI Explicability", explicability_score, 
         "Enhance product explanation quality and RM communication training. Introduce visual aids, plain-language summaries, and digital transparency tools. Benchmark against disclosure standards before launch."),
        ("Human Stewardship", stewardship_score,
         "Redesign incentive structures to reward advisory quality, not sales volume. Implement stewardship training focused on integrity signaling and benevolence. Run monthly stewardship perception checks during the recovery period."),
        ("Systemic Legitimacy", legitimacy_score,
         "Establish robust recourse and appeal mechanisms. Ensure outcomes are communicated with transparency on process and equity. Provide SBV-ready audit trail of fairness metrics. Prioritise appeal resolution speed as a legitimacy signal.")
    ]
    
    # Sort by score ascending (lowest = highest priority)
    interventions_sorted = sorted(interventions, key=lambda x: x[1])
    
    for dim_name, score, action in interventions_sorted:
        status_label, css_class, color = get_status(score)
        priority_icon = "🔴" if score < 2.5 else "🟡" if score < 3.5 else "🟢"
        
        st.markdown(f"""
        <div class="intervention-card">
            <h4 style="margin:0 0 0.5rem 0; color:{color}">{priority_icon} {dim_name} {status_label}</h4>
            <p style="margin:0 0 0.5rem 0;"><strong>Score:</strong> {score:.1f}/5</p>
            <p style="margin:0;"><strong>Recommended Action:</strong> {action}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- Radar Chart for Core Triad ---
    st.subheader("📊 Trust Ecology Radar (Core Triad)")
    st.markdown("*Visualizing structural balance. Interconnected Trust displayed separately as processual variable.*")
    
    categories = ['AI Explicability', 'Human Stewardship', 'Systemic Legitimacy']
    values = [explicability_score, stewardship_score, legitimacy_score]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        name='Trust Score',
        line_color='#2a5298',
        fillcolor='rgba(42, 82, 152, 0.3)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickvals=list(range(6))),
            angularaxis=dict(direction="clockwise", period=3)
        ),
        showlegend=False,
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Processual Variable: Interconnected Trust ---
    st.subheader("🔄 Processual Variable: Interconnected Trust")
    int_label, int_css, int_color = get_status(interconnect_score)
    st.markdown(f"""
    **Score:** {interconnect_score:.2f}/5 | **Status:** {int_label}
    
    *This variable represents the dynamic flow and dependency between the three core dimensions. 
    High scores indicate strong coupling (events in one dimension strongly affect others).*
    """)
    st.progress(interconnect_score / 5.0)
    
    # --- Critical Incident Summary (if completed) ---
    if 'q1' in locals():
        st.subheader("🔍 Critical Incident Insights")
        st.markdown(f"""
        - **AI Trust Recovery:** {q1} | **Human Trust Recovery:** {q2}
        - **Retroactive Doubt (AI):** {q3}/5 | **Retroactive Doubt (Human):** {q4}/5
        - **Future Acceptance Intention:** {q5}/5
        - **Restoration Mechanisms:** {', '.join(q6) if q6 else 'None selected'}
        - **Systemic Legitimacy Recovery:** {q8}
        """)
        if q7:
            st.markdown(f"*Qualitative note:* {q7}")
    
    # --- EXPORT FUNCTIONALITY ---
    st.markdown("---")
    st.subheader("💾 Export Results")
    st.markdown("<div class='export-section'><strong>Download your Trust Configuration Report</strong><br>Choose your preferred format for sharing or record-keeping.</div>", unsafe_allow_html=True)
    
    col_export1, col_export2 = st.columns(2)
    
    # CSV Export
    with col_export1:
        csv_data = pd.DataFrame({
            'Dimension': ['AI Explicability', 'Human Stewardship', 'Systemic Legitimacy', 'Interconnected Trust', 'Overall Trust Index'],
            'Score': [round(explicability_score, 2), round(stewardship_score, 2), round(legitimacy_score, 2), round(interconnect_score, 2), round(overall_score, 2)],
            'Status': [get_status_label(explicability_score), get_status_label(stewardship_score), get_status_label(legitimacy_score), get_status_label(interconnect_score), get_status_label(overall_score)]
        })
        csv_buffer = csv_data.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer,
            file_name=f"trust_ecology_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # JSON/Text Report Export
    with col_export2:
        report_text = f"""
TRUST ECOLOGY DIAGNOSTIC REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================

DIMENSION SCORES (1-5 Scale)
----------------------------
AI Explicability:      {explicability_score:.2f}/5 [{get_status_label(explicability_score)}]
Human Stewardship:     {stewardship_score:.2f}/5 [{get_status_label(stewardship_score)}]
Systemic Legitimacy:   {legitimacy_score:.2f}/5 [{get_status_label(legitimacy_score)}]
Interconnected Trust:  {interconnect_score:.2f}/5 [{get_status_label(interconnect_score)}]
Overall Trust Index:   {overall_score:.2f}/5 [{get_status_label(overall_score)}]

CASCADE RISK
------------
Score Range: {score_range:.2f} points
Status: {"⚠️ HIGH - Address lowest dimension first" if score_range >= 2.0 else "✓ LOW - Balanced trust profile"}

INTERVENTION PRIORITIES
-----------------------
"""
        for i, (dim_name, score, action) in enumerate(interventions_sorted, 1):
            report_text += f"{i}. {dim_name} ({score:.1f}/5): {action}\n"
        
        if 'q1' in locals():
            report_text += f"""
CRITICAL INCIDENT REFLECTION
----------------------------
AI Trust Recovery: {q1}
Human Trust Recovery: {q2}
Retroactive Doubt (AI): {q3}/5
Retroactive Doubt (Human): {q4}/5
Future Acceptance: {q5}/5
Restoration Mechanisms: {', '.join(q6) if q6 else 'None'}
Systemic Recovery: {q8}
Qualitative Note: {q7 if q7 else 'Not provided'}
"""
        
        report_text += """
================================
Based on: Hor (2026) Trust Ecology: Calibrating Triadic, Processual Trust
Status: Draft / Pre-Validation - For research use only
"""
        
        st.download_button(
            label="📄 Download Text Report",
            data=report_text,
            file_name=f"trust_ecology_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # JSON Export (for researchers)
    st.markdown("**For Researchers:**")
    json_buffer = json.dumps(st.session_state.assessment_data, indent=2).encode('utf-8')
    st.download_button(
        label="🔬 Download JSON (Research Data)",
        data=json_buffer,
        file_name=f"trust_ecology_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=False
    )

# --- Footer ---
st.markdown("---")
st.caption("Trust Ecology Diagnostic Dashboard • Hor (2026) • Draft for research use only")