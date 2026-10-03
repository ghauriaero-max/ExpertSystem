
import streamlit as st
from silvus_triad_expert_system import (
    PROPOSITIONS,
    QUESTIONS,
    RULES,
    forward_chain,
    explain_fact,
)

st.set_page_config(
    page_title="Assignment No.01 Expert System (AI-502)",
    page_icon="📡",
    layout="wide",
)

st.markdown("""
<style>
.main-title {
    font-size: 2.1rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.subtitle {
    color: #666;
    margin-bottom: 1.2rem;
}
.result-box {
    padding: 1rem;
    border-radius: 0.7rem;
    border: 1px solid #ddd;
    margin-bottom: 0.7rem;
}
.fault {
    border-left: 5px solid #d9534f;
}
.ok {
    border-left: 5px solid #28a745;
}
.info {
    border-left: 5px solid #0d6efd;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">📡 Data Link Expert System</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Rule-based troubleshooting system using forward chaining</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("System Information")
    st.write("**Inference method:** Forward chaining")
    st.write(f"**Propositions:** {len(PROPOSITIONS)}")
    st.write(f"**Rules:** {len(RULES)}")
    st.write(f"**Diagnostic questions:** {len(QUESTIONS)}")

    st.divider()
    st.warning(
        "Use the applicable Silvus radio manual and Triad BDA datasheet "
        "for exact voltage, RF-power, temperature and alarm limits."
    )

    if st.button("🔄 Reset Diagnostic", use_container_width=True):
        st.session_state.clear()
        st.rerun()

tab1, tab2, tab3 = st.tabs([
    "🛠️ Troubleshooting",
    "🧠 Knowledge Base",
    "ℹ️ About",
])

with tab1:
    st.subheader("Diagnostic Questionnaire")
    st.caption("Select the statements that are confirmed to be true. "
               "Only selected statements are inserted into the knowledge base as facts.")

    answers = {}

    radio_questions = [q for q in QUESTIONS if q[1].startswith("radio_")]
    bda_questions = [q for q in QUESTIONS if q[1].startswith("bda_")]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Silvus Radio")
        for qid, symbol, question in radio_questions:
            answers[symbol] = st.checkbox(
                f"{qid}. {question}",
                key=f"check_{symbol}",
            )

    with col2:
        st.markdown("### Triad BDA")
        for qid, symbol, question in bda_questions:
            answers[symbol] = st.checkbox(
                f"{qid}. {question}",
                key=f"check_{symbol}",
            )

    st.divider()

    if st.button("🔍 Run Expert Diagnosis", type="primary", use_container_width=True):
        initial_facts = {symbol for symbol, selected in answers.items() if selected}

        all_facts, fired_rules, trace = forward_chain(initial_facts)
        derived = sorted(all_facts - initial_facts)

        st.session_state["initial_facts"] = initial_facts
        st.session_state["all_facts"] = all_facts
        st.session_state["fired_rules"] = fired_rules
        st.session_state["trace"] = trace
        st.session_state["derived"] = derived
        st.session_state["diagnosed"] = True

    if st.session_state.get("diagnosed"):
        initial_facts = st.session_state["initial_facts"]
        all_facts = st.session_state["all_facts"]
        fired_rules = st.session_state["fired_rules"]
        trace = st.session_state["trace"]
        derived = st.session_state["derived"]

        st.divider()
        st.subheader("📋 Diagnostic Results")

        conclusions = [
            f for f in derived
            if f.endswith("_fault")
            or f.endswith("_condition")
            or f.endswith("_ok")
            or f in {
                "integrated_rf_path_fault",
                "radio_configuration_or_peer_fault",
            }
        ]

        if conclusions:
            for fact in conclusions:
                explanation = explain_fact(fact)

                if "fault" in fact:
                    css_class = "fault"
                    icon = "⚠️"
                elif "condition" in fact:
                    css_class = "info"
                    icon = "🔎"
                else:
                    css_class = "ok"
                    icon = "✅"

                st.markdown(
                    f'<div class="result-box {css_class}">'
                    f'<strong>{icon} {fact}</strong><br>'
                    f'{explanation}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                "The knowledge base did not reach a specific diagnostic conclusion. "
                "Collect additional evidence and consult detailed maintenance procedures."
            )

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Initial Facts", len(initial_facts))
        metric2.metric("Rules Fired", len(fired_rules))
        metric3.metric("Derived Facts", len(derived))

        with st.expander("Initial Facts"):
            if initial_facts:
                for fact in sorted(initial_facts):
                    st.write(f"• `{fact}`")
            else:
                st.write("No positive facts were selected.")

        with st.expander("Derived Facts"):
            if derived:
                for fact in derived:
                    st.write(f"→ `{fact}`")
            else:
                st.write("No rules fired.")

        with st.expander("Inference Trace"):
            if trace:
                for i, item in enumerate(trace, 1):
                    st.code(f"{i}. {item}")
            else:
                st.write("No inference was possible.")

with tab2:
    st.subheader("Knowledge Base")

    st.markdown("### Propositions")
    proposition_rows = [
        {"Symbol": symbol, "Meaning": meaning}
        for symbol, meaning in PROPOSITIONS.items()
    ]
    st.dataframe(proposition_rows, use_container_width=True, hide_index=True)

    st.markdown("### Rules")
    rule_rows = [
        {
            "Rule": rule.rule_id,
            "Conditions": " AND ".join(sorted(rule.conditions)),
            "Conclusion": rule.conclusion,
        }
        for rule in RULES
    ]
    st.dataframe(rule_rows, use_container_width=True, hide_index=True)

    st.markdown("### User Queries")
    query_rows = [
        {"ID": qid, "Proposition": symbol, "Question": question}
        for qid, symbol, question in QUESTIONS
    ]
    st.dataframe(query_rows, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("About the Expert System")

    st.markdown("""
### Purpose
This application provides a rule-based decision-support interface for
preliminary troubleshooting of a Silvus radio and a Triad RF BDA.

### Architecture

**User observations → Facts → Forward chaining → Derived facts → Diagnostic conclusions**

The Streamlit layer is only the graphical interface. The actual reasoning
is performed by the existing Python knowledge base and forward-chaining
inference engine.

### Important limitation
This is an educational/prototype expert system. It must not replace the
applicable equipment manuals, datasheets, approved maintenance procedures,
electrical/RF safety procedures, or qualified maintenance personnel.

Model-specific thresholds should be populated only after verification against
the exact deployed equipment documentation.
""")

st.caption("Silvus + Triad BDA Expert System — Forward Chaining Prototype")
