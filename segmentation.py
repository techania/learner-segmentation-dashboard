import pandas as pd
from datetime import datetime
import streamlit as st
import plotly.express as px

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Learner Risk Segmentation & Intervention Dashboard", layout="wide")

# ------------------------------------------------------------
# HEADER / EXECUTIVE SUMMARY
# ------------------------------------------------------------
st.markdown("""
# Learner Risk & Intervention Dashboard

Using a **Critical / Moderate / On Track** segmentation model, this dashboard monitors learner engagement, progress, and barriers across a **12-week program**.

It highlights who requires immediate intervention, who is at rising risk, and who is progressing well, enabling data-driven coaching, resource allocation, and operational decision-making.
""")

# ------------------------------------------------------------
# LOAD & CLEAN DATA
# ------------------------------------------------------------
# Load CSV and ignore the first column if it's a blank index
# don't use any column as index
df = pd.read_csv("cohort.csv", index_col=False)

# Reset index to start from 1 for display purposes
df.reset_index(drop=True, inplace=True)
df.index += 1  # optional: for numbering purposes


# Combine first + last name
df["Name"] = df["First Name"].fillna("") + " " + df["Last Name"].fillna("")

# Convert dates and calculate days since last seen
df["Last Seen"] = pd.to_datetime(df["Last Seen"], errors='coerce')
today = datetime(2025, 8, 5)
df["Days_Since_Last_Seen"] = (today - df["Last Seen"]).dt.days

# Clean percentage columns


def clean_percentage_column(col):
    return pd.to_numeric(col.astype(str).str.replace("%", ""), errors='coerce')


df["Progress"] = clean_percentage_column(df["Progress"])
df["Average Grade"] = clean_percentage_column(df["Average Grade"])

# ------------------------------------------------------------
# SEGMENTATION LOGIC
# ------------------------------------------------------------


def engagement_segment(days):
    if days > 14:
        return "Critical"
    elif days > 7:
        return "Moderate"
    return "On Track"


def progress_segment(p):
    if p < 50:
        return "Critical"
    elif p < 70:
        return "Moderate"
    return "On Track"


df["Engagement_Segment"] = df["Days_Since_Last_Seen"].apply(engagement_segment)
df["Progress_Segment"] = df["Progress"].apply(progress_segment)
df["Barriers_Flag"] = df["Barriers"].apply(
    lambda x: "Has Barriers" if pd.notna(x) and str(x).strip().lower() not in [
        "none", "no", ""] else "No Barriers"
)


def composite_segment(row):
    if row["Engagement_Segment"] == "Critical" or row["Progress_Segment"] == "Critical" or row["Barriers_Flag"] == "Has Barriers":
        return "Critical / Urgent"
    if row["Engagement_Segment"] == "Moderate" or row["Progress_Segment"] == "Moderate":
        return "Moderate / At-Risk"
    return "On Track / Low Risk"


df["Composite_Segment"] = df.apply(composite_segment, axis=1)

# ------------------------------------------------------------
# EXECUTIVE KPIs
# ------------------------------------------------------------
st.markdown("---")
st.markdown("## 📌 Segmentation Overview")
with st.container(border=True):
    total = len(df)
    critical = len(df[df["Composite_Segment"] == "Critical / Urgent"])
    moderate = len(df[df["Composite_Segment"] == "Moderate / At-Risk"])
    ontrack = len(df[df["Composite_Segment"] == "On Track / Low Risk"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Learners", total)
    c2.metric("Critical / Urgent", f"{critical} ({critical/total*100:.1f}%)")
    c3.metric("Moderate / At-Risk", f"{moderate} ({moderate/total*100:.1f}%)")
    c4.metric("On Track / Low Risk", f"{ontrack} ({ontrack/total*100:.1f}%)")


# ------------------------------------------------------------
# SIMPLE DISTRIBUTION CHART
# ------------------------------------------------------------
counts = df["Composite_Segment"].value_counts().reset_index()
counts.columns = ["Segment", "Count"]

fig = px.bar(
    counts,
    x="Segment",
    y="Count",
    color="Segment",
    color_discrete_map={
        "Critical / Urgent": "red",
        "Moderate / At-Risk": "orange",
        "On Track / Low Risk": "green"
    }
)
st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# PRIORITY WORKLIST
# ------------------------------------------------------------
st.markdown("---")
st.subheader("🚨 High-Risk Learner Priority Worklist")
st.markdown("<p style='font-size: 16px; color: #949ba8;'>Learners requiring immediate action</p>",
            unsafe_allow_html=True)

priority_df = df[
    (df["Composite_Segment"] == "Critical / Urgent") |
    (df["Barriers_Flag"] == "Has Barriers") |
    (df["Days_Since_Last_Seen"] > 10)
].sort_values(by=["Days_Since_Last_Seen", "Progress"], ascending=[False, True]).copy()

# Add No. column
priority_df.insert(0, "No.", range(1, len(priority_df)+1))

# Logical column order
logical_cols = ["No.", "Name", "Days_Since_Last_Seen", "Progress", "Average Grade",
                "Barriers_Flag", "Engagement_Segment", "Progress_Segment", "Composite_Segment"] + \
    [col for col in df.columns if col not in ["First Name", "Last Name", "Name",
                                              "Days_Since_Last_Seen", "Progress", "Average Grade",
                                              "Barriers_Flag", "Engagement_Segment",
                                              "Progress_Segment", "Composite_Segment"]]

display_cols = {
    "Days_Since_Last_Seen": "Days Since Last Seen (days)",
    "Progress": "Progress (%)",
    "Average Grade": "Average Grade (%)"
}

st.dataframe(priority_df[logical_cols].rename(
    columns=display_cols), use_container_width=True)

with st.expander("ℹ️ Methodology for Priority Worklist"):
    st.markdown("""
The Priority Worklist highlights learners who require immediate outreach based on:

1. **Composite Segment:** Learners in the 'Critical / Urgent' segment.
2. **Engagement:** Days since last login/activity — learners inactive for >10 days are flagged.
3. **Progress:** Learners with low completion percentages.
4. **Barriers:** Learners with known barriers (e.g., access issues, personal challenges).

The top 15 learners are displayed by **highest urgency**, sorted first by inactivity, then by lowest progress.

*The Priority Worklist is a dynamically generated subset of Critical / Urgent (and learners with barriers/inactivity) for immediate outreach. All learners in this list follow the Critical / Urgent intervention plan.*
""")


# ------------------------------------------------------------
# SEGMENTED LEARNER DETAILS + INTERVENTIONS + COLLAPSIBLE EXPLANATION
# ------------------------------------------------------------
st.markdown("## 📂 Learner Segments + Targeted Interventions")
st.markdown("""
<p style='font-size: 16px; color: #949ba8; margin-bottom: -30px;'>
Detailed breakdown of each risk segment with recommended actions.
</p>
""", unsafe_allow_html=True)

intervention_text = {
    "Critical / Urgent": """
**Who:** Learners with low engagement, behind progress, or significant barriers  

**Actions:**  
- **Immediate multi-channel outreach:** Call, SMS, and email within 24 hours  
- **Personalized coaching plan:** Assign a dedicated coach to create a tailored action plan  
- **Barrier resolution escalation:** Involve program operations or support teams to remove technical, financial, or accessibility obstacles  
- **Progress accountability checkpoints:** Daily check-ins for the next 3 days, with completion targets  
- **Performance tracking dashboard:** Monitor engagement and progress in real-time, trigger alerts for no activity  
- **Peer buddy system:** Pair learners with high-performing peers for mentorship  
- **Incentivized milestones:** Short-term achievements with recognition or small rewards
""",
    "Moderate / At-Risk": """
**Who:** Learners showing moderate engagement issues or slightly behind in progress  

**Actions:**  
- **Weekly check-ins:** Coach or automated system nudges to ensure learners stay on track  
- **Targeted micro-interventions:** Assign specific learning modules or exercises to address gaps  
- **Data-driven monitoring:** Identify trends in engagement and progress, flag any declining performance  
- **Motivational nudges:** Emails highlighting achievements and next steps  
- **Optional peer mentoring:** Connect with more engaged learners for guidance  
- **Small milestone rewards:** Recognize incremental improvements
""",
    "On Track / Low Risk": """
**Who:** High engagement, progressing well  

**Actions:**  
- **Recognition and feedback:** Highlight achievements in dashboards or team meetings  
- **Enrichment modules:** Provide optional advanced content or challenges  
- **Next stage preparation:** Suggest preparation activities for future program stages  
- **Mentorship opportunities:** Encourage high-performing learners to mentor peers  
- **Engagement celebration:** Badges or certificates for sustained progress  
- **Continuous monitoring:** Track for any signs of risk before they escalate
"""
}

explanation_text = {
    "Critical / Urgent": """
Learners in the **Critical / Urgent** segment are flagged for **immediate intervention**.

**Segmentation criteria:**
1. **Engagement:** Not active for **more than 14 days**.
2. **Progress:** Below **50%** completion.
3. **Barriers:** Any known personal, technical, or access-related challenges.

**Composite logic:**  
- If **any** criteria is met → learner is in Critical / Urgent.

**Priority Worklist inclusion:**  
- All Critical / Urgent learners.  
- Learners with barriers or inactive >10 days.
""",
    "Moderate / At-Risk": """
Learners in the **Moderate / At-Risk** segment show **early signs of risk**.

**Segmentation criteria:**
1. **Engagement:** 8–14 days since last login.
2. **Progress:** 50–69% completion.
3. **Barriers:** Minor or intermittent challenges.

**Composite logic:**  
- If **no Critical criteria** but **any Moderate criteria** is met → Moderate / At-Risk.

**Priority Worklist inclusion:**  
- Typically not included unless inactive >10 days or has barriers.
""",
    "On Track / Low Risk": """
Learners in the **On Track / Low Risk** segment are **progressing as expected**.

**Segmentation criteria:**
1. **Engagement:** Logged in within last 7 days.
2. **Progress:** ≥70% completion.
3. **Barriers:** None reported.

**Composite logic:**  
- No Critical or Moderate criteria → On Track / Low Risk.

**Priority Worklist inclusion:**  
- Only included if unexpected barriers or inactive >10 days.
"""
}

segment_icons = {
    "Critical / Urgent": "🔴",
    "Moderate / At-Risk": "🟠",
    "On Track / Low Risk": "🟢"
}

for seg in ["Critical / Urgent", "Moderate / At-Risk", "On Track / Low Risk"]:
    seg_df = df[df["Composite_Segment"] == seg].copy()
    seg_df.insert(0, "No.", range(1, len(seg_df)+1))

    # Segment title with icon
    st.markdown(f"---\n### {segment_icons[seg]} {seg}")

    # Collapsible intervention actions
    with st.expander("📋 Intervention Plan"):
        st.markdown(intervention_text[seg].replace("\n", "  \n"))

    # Display table
    st.dataframe(
        seg_df[logical_cols].rename(columns=display_cols),
        use_container_width=True
    )

    # Collapsible explanation
    with st.expander(f"ℹ️ How learners were categorized for '{seg}'"):
        st.markdown(explanation_text[seg])


# ------------------------------------------------------------
# DIMENSION DRILLDOWNS IN TABS
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Engagement", "Progress", "Average Grade", "Barriers", "Training Stage"]
)

with tab1:
    st.subheader("Engagement Breakdown")
    fig_eng = px.histogram(
        df,
        x="Days_Since_Last_Seen",
        color="Composite_Segment",
        color_discrete_map={"Critical / Urgent": "red",
                            "Moderate / At-Risk": "orange", "On Track / Low Risk": "green"},
        labels={"Days_Since_Last_Seen": "Days Since Last Seen (days)"}
    )
    st.plotly_chart(fig_eng, use_container_width=True)

with tab2:
    st.subheader("Progress Breakdown")
    fig_prog = px.histogram(
        df,
        x="Progress",
        color="Composite_Segment",
        nbins=int(df["Progress"].max()-df["Progress"].min())+1,
        color_discrete_map={"Critical / Urgent": "red",
                            "Moderate / At-Risk": "orange", "On Track / Low Risk": "green"},
        labels={"Progress": "Progress (%)"}
    )
    st.plotly_chart(fig_prog, use_container_width=True)

with tab3:
    st.subheader("Average Grade Breakdown")
    fig_grade = px.histogram(
        df,
        x="Average Grade",
        color="Composite_Segment",
        nbins=int(df["Average Grade"].max()-df["Average Grade"].min())+1,
        color_discrete_map={"Critical / Urgent": "red",
                            "Moderate / At-Risk": "orange", "On Track / Low Risk": "green"},
        labels={"Average Grade": "Average Grade (%)"}
    )
    st.plotly_chart(fig_grade, use_container_width=True)

# Create a column that shows actual barriers or 'No Barrier'
df["Barriers_Display"] = df["Barriers"].apply(
    lambda x: str(x).strip() if pd.notna(x) and str(
        x).strip() != "" else "No Barrier"
)

# In the Barriers tab
with tab4:
    st.subheader("Barriers Breakdown")
    fig_bar = px.histogram(
        df,
        x="Barriers_Display",  # use the new column
        color="Composite_Segment",
        color_discrete_map={
            "Critical / Urgent": "red",
            "Moderate / At-Risk": "orange",
            "On Track / Low Risk": "green"
        },
        labels={"Barriers_Display": "Barriers"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)


with tab5:
    st.subheader("Training Stage Breakdown")
    fig_stage = px.histogram(
        df,
        x="Training Stage",
        color="Composite_Segment",
        color_discrete_map={"Critical / Urgent": "red",
                            "Moderate / At-Risk": "orange", "On Track / Low Risk": "green"}
    )
    st.plotly_chart(fig_stage, use_container_width=True)

# ------------------------------------------------------------
# DOWNLOAD
# ------------------------------------------------------------
st.markdown("## 📥 Download Segmented Dataset")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "cohort_segmented.csv", "text/csv")


st.markdown("""
---
**Assignment Notes:** This Streamlit dashboard demonstrates:  
- Segmentation plan based on Engagement, Progress, and Barriers  
- High-level intervention actions per segment  
- Priority worklist for immediate action  
- Drilldowns for engagement, progress, grades, barriers, and training stage
""")

# cd ~/Desktop/Segmentation
# source venv/bin/activate
# streamlit run segmentation.py
# pip install -r requirements.txt
