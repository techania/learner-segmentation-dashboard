# Learner Risk Segmentation & Intervention Dashboard

## Overview
The **Learner Risk Segmentation & Intervention Dashboard** monitors learner engagement, progress, and potential barriers across a program. It segments learners into **Critical / Moderate / On Track** categories to identify who requires immediate intervention, who is at rising risk, and who is progressing well.  

This tool supports **coaches, program managers, and operational teams** in making **data-driven decisions** for interventions and resource allocation.

---

## Key Components

### 1. Executive Summary & KPIs
The dashboard shows:
- **Total Learners**
- Learner counts and percentages per segment:
  - **Critical / Urgent**
  - **Moderate / At-Risk**
  - **On Track / Low Risk**

### 2. Segmentation Logic
Learners are segmented based on three dimensions:

#### Engagement
| Segment   | Days Since Last Seen |
|-----------|--------------------|
| Critical  | >14 days           |
| Moderate  | 8–14 days          |
| On Track  | ≤7 days            |

#### Progress
| Segment   | Completion % |
|-----------|--------------|
| Critical  | <50%         |
| Moderate  | 50–69%       |
| On Track  | ≥70%         |

#### Barriers
| Segment   | Description                                    |
|-----------|------------------------------------------------|
| Critical  | Known barriers affecting learning             |
| Moderate  | Minor or intermittent challenges              |
| On Track  | No reported barriers                          |

#### Composite Segment
- **Critical / Urgent:** Any Critical criterion met **or** has known barriers  
- **Moderate / At-Risk:** Any Moderate criterion met (and no Critical)  
- **On Track / Low Risk:** None of the above  

---

### 3. Priority Worklist
The **High-Risk Learner Priority Worklist** identifies learners requiring **immediate outreach**.  

**Inclusion Criteria:**
- Learners in the **Critical / Urgent** segment  
- Learners with **known barriers**  
- Learners inactive for **more than 10 days**

**Sorting Logic:**
1. Days since last activity (descending — most inactive first)  
2. Progress (ascending — lowest progress first)

This ensures that **the most urgent cases appear at the top** for intervention.

---

### 4. Segmented Learner Tables & Recommended Interventions
Each segment has an **interactive table** showing relevant learners, along with recommended actions.

| Segment                 | Who                                               | Actions                                                                 |
|-------------------------|--------------------------------------------------|-------------------------------------------------------------------------|
| Critical / Urgent       | Low engagement, behind progress, or known barriers | Immediate outreach (call/SMS), intensive coaching, barrier escalation, 3-day login expectation |
| Moderate / At-Risk      | Moderate engagement or slightly behind progress | Weekly check-ins, nudges + encouragement, monitoring trends            |
| On Track / Low Risk     | High engagement, progressing well                | Recognition, enrichment modules, prep for next program stage            |

---

### 5. Drilldowns & Visualizations
Interactive tabs provide **dimension-specific insights**:

1. **Engagement:** Distribution of Days Since Last Seen by segment  
2. **Progress:** Distribution of Progress (%) by segment  
3. **Average Grade:** Distribution of Average Grade (%) by segment  
4. **Barriers:** Distribution of reported barriers by segment  
5. **Training Stage:** Learner count per training stage by segment  

Visualizations use **color coding** to clearly distinguish segments:
- **Critical / Urgent:** Red  
- **Moderate / At-Risk:** Orange  
- **On Track / Low Risk:** Green

---

### 6. Data Table Details
- **No.:** Row numbering for readability  
- **Name:** Learner full name  
- **Days Since Last Seen:** Calculated from last login/activity date  
- **Progress:** Program completion percentage  
- **Average Grade:** Grade percentage  
- **Barriers Flag:** Indicates whether learner has reported barriers  
- **Engagement Segment:** Derived from Days Since Last Seen  
- **Progress Segment:** Derived from Progress  
- **Composite Segment:** Overall risk segment  

Tables are **interactive and sortable**, allowing coaches to filter and prioritize interventions.

---

### 7. Detailed Explanation of Segmentation

#### Critical / Urgent
Learners in this segment meet **any** of the following:
- **Engagement:** Not active in the last 7+ days  
- **Progress:** Below 50%  
- **Barriers:** Known personal or access challenges  

#### Moderate / At-Risk
Learners in this segment show **some signs of risk**:
- **Engagement:** 3–7 days since last activity  
- **Progress:** 50–69%  
- **Barriers:** Minor or intermittent challenges  

#### On Track / Low Risk
Learners in this segment are **progressing well**:
- **Engagement:** Active recently  
- **Progress:** 70% or higher  
- **Barriers:** None reported  

---

### 8. Notes & Considerations
- **Thresholds** for engagement and progress can be adjusted in the code.  
- **Barriers** are treated as **binary** for segmentation — any reported barrier triggers Critical classification.  
- Dashboard is designed for a **12-week program** but adaptable to different durations.  
- Data is **cleaned and validated**, with percentages converted to numeric and missing values handled gracefully.  

---

### 9. Downloadable Segmented Dataset
- Users can **download the entire segmented dataset** as a CSV for offline analysis.
- CSV contains all original data plus computed columns:
  - `Days_Since_Last_Seen`  
  - `Engagement_Segment`  
  - `Progress_Segment`  
  - `Barriers_Flag`  
  - `Composite_Segment`  
