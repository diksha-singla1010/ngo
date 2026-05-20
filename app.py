# app.py - Professional NGO Impact Analytics Report
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import donor_management       as donor_mod
import program_tracking       as prog_mod
import beneficiary_management as bene_mod
import ml_churn
import cross_analysis         as cross_mod
from ui_helpers import DARK_LAYOUT, chart, download_reports, load_css, metric_row

st.set_page_config(page_title="NGO & Donor Analytics", layout="wide")


load_css(os.path.dirname(__file__))

st.markdown("""
<div class="page-header">
    <h1>NGO & Donor Analytics</h1>
    <div class="subtitle">Data Analytics Dashboard &nbsp;·&nbsp; MCA 2025–26 &nbsp;·&nbsp; Diksha Singla (Roll No. 10)</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 OVERVIEW",
    "👥 DONOR ANALYSIS",
    "🎯 PROGRAM ANALYSIS",
    "❤️ BENEFICIARY ANALYSIS",
    "🔮 CHURN PREDICTION",
    "🔗 CROSS ANALYSIS",
    "📥 DOWNLOAD REPORTS",
])
@st.cache_data
def load_report_data():
    return {
        "donor_kpi":     donor_mod.get_donor_kpis(),
        "prog_kpi":      prog_mod.get_program_kpis(),
        "bene_kpi":      bene_mod.get_beneficiary_kpis(),
        "sector":        donor_mod.get_sector_funding(),
        "state_fund":    donor_mod.get_state_funding(),
        "year_trend":    donor_mod.get_year_wise_trend(),
        "category_sum":  prog_mod.get_category_summary(),
        "state_program": prog_mod.get_state_wise_programs(),
        "gender":        bene_mod.get_gender_distribution(),
        "age":           bene_mod.get_age_group_distribution(),
        "top_donors":    donor_mod.get_top_donors(15),
        "category_demo": bene_mod.get_category_demographics(),
        "payment_mode":  donor_mod.get_payment_mode_analysis(),
        "donor_type":    donor_mod.get_donor_type_analysis(),
        "engagement":    donor_mod.get_engagement_scores(),
        "prog_success":  prog_mod.get_program_success_rates(),
        "cost_per_ben":  prog_mod.get_cost_per_beneficiary(),
        "duration_comp": prog_mod.get_duration_vs_completion(),
        "funding_break": prog_mod.get_funding_breakdown(),
        "programs_tbl":  prog_mod.get_programs_table(),
        "outcome_dist":  bene_mod.get_outcome_distribution(),
        "state_bpl":     bene_mod.get_state_bpl_coverage(),
        "dropout":       bene_mod.get_dropout_analysis(),
        "occupation":    bene_mod.get_occupation_distribution(),
        "enroll_cat":    bene_mod.get_enrollment_status_by_category(),
    }

data = load_report_data()
with tab1:
    st.header("Executive Summary")

    dk = data["donor_kpi"]
    bk = data["bene_kpi"]
    pk = data["prog_kpi"]
    metric_row([
        ("Total Funds", f"{dk.get('total_funds_cr',0)} Cr"),
        ("Active Donors", dk.get("active_donors", 0)),
        ("Total Beneficiaries", f"{bk.get('total',0):,}"),
        ("Success Rate", f"{bk.get('success_rate',0)}%"),
        ("Active Programs", pk.get("active_programs", 0)),
        ("States Covered", dk.get("states_covered", 0)),
    ])

    st.divider()

    st.subheader("📊 Year-wise Funding Trend")
    chart(
        px.line(data["year_trend"], x="financial_year", y="total_cr",
                markers=True, title="Funding Trend (₹ Crores)",
                color_discrete_sequence=["#e8c87a"]).update_layout(**DARK_LAYOUT))

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Sector-wise Funding")
        chart(
            px.pie(data["sector"], names="sector_focus", values="total_cr",
                   title="Distribution of Funds by Sector", hole=0.4,
                   color_discrete_sequence=["#e8c87a","#5ec4b0","#a78bfa","#f87171","#60a5fa"]).update_layout(**DARK_LAYOUT))
    with colB:
        st.subheader("State-wise Beneficiaries")
        chart(
            px.bar(data["state_program"].head(10), x="state", y="beneficiaries",
                   color="success_rate", title="Top 10 States — Beneficiaries",
                   color_continuous_scale="Teal").update_layout(**DARK_LAYOUT))

    colC, colD = st.columns(2)
    with colC:
        st.subheader("Donor Retention vs Churn")
        ret_df = pd.DataFrame({
            "Status": ["Active (Retained)", "Inactive (Churned)"],
            "Count":  [dk.get("active_donors",0), dk.get("inactive_donors",0)]
        })
        chart(
            px.pie(ret_df, names="Status", values="Count",
                   color_discrete_sequence=["#5ec4b0","#ef4444"], hole=0.5).update_layout(**DARK_LAYOUT))
    with colD:
        st.subheader("Program Budget by Category")
        chart(
            px.bar(data["category_sum"], x="category", y="budget_cr",
                   color="success_rate", title="Budget (₹ Cr) & Success Rate by Category",
                   color_continuous_scale="Teal").update_layout(**DARK_LAYOUT))
with tab2:
    st.subheader("👥 Donor Analysis")

    dk = data["donor_kpi"]
    metric_row([
        ("Total Donors", dk.get("total_donors", 0)),
        ("Retention Rate", f"{dk.get('retention_rate',0)}%"),
        ("Avg Donation", f"{dk.get('avg_donation_cr',0)} Cr"),
        ("Churn Rate", f"{dk.get('churn_rate',0)}%"),
    ])

    st.divider()
    st.markdown("#### 🏆 Top 15 Donors")
    st.dataframe(data["top_donors"], use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Funding by Sector")
        chart(
            px.bar(data["sector"], x="sector_focus", y="total_cr",
                   color="total_cr", color_continuous_scale="Purples",
                   title="Total Funding per Sector (₹ Cr)", text_auto=".1f"))
    with col2:
        st.markdown("#### Funding by State")
        chart(
            px.bar(data["state_fund"].head(10), x="state", y="total_cr",
                   color="total_cr", color_continuous_scale="Blues",
                   title="Top 10 States by Funding (₹ Cr)", text_auto=".1f"))

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 💳 Payment Mode — Retention Rate")
        chart(
            px.bar(data["payment_mode"], x="payment_mode", y="retention_rate",
                   color="retention_rate", color_continuous_scale="RdYlGn",
                   title="Retention Rate by Payment Mode (%)", text_auto=".1f"))
    with col4:
        st.markdown("#### 🏢 Donor Type Analysis")
        chart(
            px.bar(data["donor_type"], x="donor_type", y="total_cr",
                   color="retention_rate", color_continuous_scale="Teal",
                   title="Donation Amount & Retention by Donor Type", text_auto=".1f"))

    st.markdown("#### ⭐ Donor Engagement Scores (Top 20)")
    st.dataframe(
        data["engagement"].head(20).style.background_gradient(subset=["score"], cmap="Purples"),
        use_container_width=True, hide_index=True)

    st.markdown("#### 📅 Year-wise Donor Activity")
    yt = data["year_trend"]
    fig_yr = go.Figure()
    fig_yr.add_trace(go.Bar(x=yt["financial_year"], y=yt["total_cr"],
                            name="Funds (₹ Cr)", marker_color="#4f46e5"))
    fig_yr.add_trace(go.Scatter(x=yt["financial_year"], y=yt["donors"],
                                name="No. of Donors", mode="lines+markers",
                                yaxis="y2", marker_color="#f59e0b"))
    fig_yr.update_layout(
        title="Funds Raised vs Donor Count per Year",
        yaxis=dict(title="₹ Crores"),
        yaxis2=dict(title="Donors", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99))
    chart(fig_yr)
with tab3:
    st.subheader("🎯 Program Performance Analysis")

    pk = data["prog_kpi"]
    metric_row([
        ("Total Programs", pk.get("total_programs", 0)),
        ("Active Programs", pk.get("active_programs", 0)),
        ("Total Budget", f"{pk.get('total_budget_cr',0)} Cr"),
        ("States Covered", pk.get("states_covered", 0)),
    ])

    st.divider()
    st.markdown("#### 📋 Programs Overview Table")
    st.dataframe(data["programs_tbl"], use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Beneficiaries & Success Rate by Category")
        chart(
            px.bar(data["category_sum"], x="category", y="enrolled",
                   color="success_rate", title="Enrolled vs Success Rate",
                   color_continuous_scale="RdYlGn", text_auto=True))
    with col2:
        st.markdown("#### State-wise Program Impact")
        chart(
            px.bar(data["state_program"].head(12), x="state", y="beneficiaries",
                   color="success_rate", title="Beneficiaries per State",
                   color_continuous_scale="Teal"))

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 💰 Cost per Beneficiary ")
        cpb = data["cost_per_ben"].sort_values("cost_per_ben").head(15)
        chart(
            px.bar(cpb, x="cost_per_ben", y="program_name", orientation="h",
                   color="cost_per_ben", color_continuous_scale="Blues",
                   title="Lowest Cost-per-Beneficiary Programs"))
    with col4:
        st.markdown("#### 📁 Funding Source Breakdown")
        chart(
            px.pie(data["funding_break"], names="funding_source", values="budget",
                   title="Budget by Funding Source", hole=0.4))

    st.markdown("#### ⏱️ Program Duration vs Completion Rate (Q8)")
    dur = data["duration_comp"].dropna(subset=["duration_months","success_rate"])
    chart(
        px.scatter(dur, x="duration_months", y="success_rate",
                   color="category", size="enrolled",
                   title="Does longer duration improve completion?",
                   labels={"duration_months":"Duration (Months)",
                           "success_rate":"Success Rate (%)"},
                   size_max=30, opacity=0.75))

    st.markdown("#### 🏆 Top 10 Programs by Success Rate")
    top_prog = data["prog_success"].head(10)[
        ["program_name","category","state","success_rate","enrolled","budget_inr"]]
    st.dataframe(
        top_prog.style.background_gradient(subset=["success_rate"], cmap="Greens"),
        use_container_width=True, hide_index=True)
with tab4:
    st.subheader("❤️ Beneficiary Demographics & Outcomes")

    bk = data["bene_kpi"]
    metric_row([
        ("Total Beneficiaries", f"{bk.get('total',0):,}"),
        ("Active", bk.get("active", 0)),
        ("Completed", bk.get("completed", 0)),
        ("Dropped", bk.get("dropped", 0)),
        ("BPL %", f"{bk.get('bpl_pct',0)}%"),
    ])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Gender Distribution")
        chart(
            px.pie(data["gender"], names="gender", values="count",
                   title="Gender Split", hole=0.45,
                   color_discrete_sequence=["#7c3aed","#06b6d4"]))
    with col2:
        st.markdown("#### Age Group Distribution")
        try:
            age_data = bene_mod.get_age_group_distribution()
            if age_data is not None and not age_data.empty:
                chart(
                    px.pie(age_data[["age_group","count"]],
                           names="age_group", values="count",
                           title="Beneficiaries by Age Group",
                           color_discrete_sequence=px.colors.sequential.Blues_r))
            else:
                st.info("Age group data not available.")
        except Exception as e:
            st.error(f"Age group error: {e}")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 📊 Outcome Distribution")
        chart(
            px.bar(data["outcome_dist"], x="outcome", y="count",
                   color="pct", color_continuous_scale="RdYlGn",
                   title="Outcome Achieved Distribution", text_auto=True))
    with col4:
        st.markdown("#### 💼 Occupation Distribution (Top 10)")
        chart(
            px.bar(data["occupation"], x="count", y="occupation",
                   orientation="h", color="pct",
                   color_continuous_scale="Purples",
                   title="Top Occupations among Beneficiaries"))

    st.markdown("#### 🗺️ BPL Coverage by State ")
    chart(
        px.bar(data["state_bpl"].head(12), x="state", y="bpl_pct",
               color="success_rate", color_continuous_scale="RdYlGn",
               title="BPL % by State (colour = success rate)", text_auto=".1f"))

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### 🚨 Dropout Analysis (Top 10)")
        st.dataframe(
            data["dropout"].style.background_gradient(
                subset=["dropout_rate"], cmap="Reds"),
            use_container_width=True, hide_index=True)
    with col6:
        st.markdown("#### Enrollment Status by Category (Stacked)")
        enroll = data["enroll_cat"]
        cols_status = [c for c in enroll.columns if c != "category"]
        fig_enroll = go.Figure()
        colors = ["#10b981","#4f46e5","#ef4444"]
        for i, col in enumerate(cols_status):
            fig_enroll.add_trace(go.Bar(
                name=col, x=enroll["category"], y=enroll[col],
                marker_color=colors[i % len(colors)]))
        fig_enroll.update_layout(barmode="stack",
                                  title="Enrollment Status by Category")
        chart(fig_enroll)

    st.markdown("#### 📋 Category-wise Demographics")
    st.dataframe(
        data["category_demo"].style.background_gradient(
            subset=["success_rate","female_pct","bpl_pct"], cmap="Greens"),
        use_container_width=True, hide_index=True)
with tab5:
    st.subheader("🔮 Donor Churn Prediction & ML Insights")

    try:
        df_summary, fi, best_name = ml_churn.get_model_summary()
        churn_df = ml_churn.predict_all()
        best_row = df_summary[df_summary["Model"] == best_name].iloc[0]

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);
                    padding:20px 28px;border-radius:20px;color:white;margin-bottom:20px;">
            <div style="font-size:13px;opacity:0.8;margin-bottom:4px">🏆 Best Performing Model</div>
            <div style="font-size:26px;font-weight:700">{best_name}</div>
            <div style="display:flex;gap:32px;margin-top:12px;flex-wrap:wrap">
                <div><div style="font-size:11px;opacity:0.7">ACCURACY</div>
                     <div style="font-size:20px;font-weight:600">{best_row['Accuracy']:.1%}</div></div>
                <div><div style="font-size:11px;opacity:0.7">AUC-ROC</div>
                     <div style="font-size:20px;font-weight:600">{best_row['AUC-ROC']:.4f}</div></div>
                <div><div style="font-size:11px;opacity:0.7">F1 SCORE</div>
                     <div style="font-size:20px;font-weight:600">{best_row['F1']:.4f}</div></div>
                <div><div style="font-size:11px;opacity:0.7">PRECISION</div>
                     <div style="font-size:20px;font-weight:600">{best_row['Precision']:.4f}</div></div>
                <div><div style="font-size:11px;opacity:0.7">RECALL</div>
                     <div style="font-size:20px;font-weight:600">{best_row['Recall']:.4f}</div></div>
                <div><div style="font-size:11px;opacity:0.7">CV (5-fold)</div>
                     <div style="font-size:20px;font-weight:600">{best_row['CV(5-fold)']:.4f}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📊 All Models Comparison")
        st.dataframe(
            df_summary.style.highlight_max(
                subset=["Accuracy","Precision","Recall","F1","AUC-ROC","CV(5-fold)"],
                color="#d1fae5"
            ).format({
                "Accuracy":   "{:.2%}", "Precision": "{:.2%}",
                "Recall":     "{:.2%}", "F1":         "{:.4f}",
                "AUC-ROC":   "{:.4f}", "CV(5-fold)": "{:.4f}",
            }),
            use_container_width=True, hide_index=True)

        st.markdown("#### 📈 Model Performance Comparison")
        metrics_melted = df_summary.melt(
            id_vars="Model",
            value_vars=["Accuracy","Precision","Recall","F1","AUC-ROC"],
            var_name="Metric", value_name="Score")
        fig_metrics = px.bar(
            metrics_melted, x="Model", y="Score", color="Metric",
            barmode="group", title="Model Metrics Side-by-Side",
            color_discrete_sequence=px.colors.qualitative.Bold, text_auto=".2f")
        fig_metrics.update_layout(yaxis_range=[0,1.05])
        chart(fig_metrics)

        st.markdown(f"#### 🧠 Feature Importances — {best_name}")
        fi_df = (pd.DataFrame(list(fi.items()), columns=["Feature","Importance"])
                   .sort_values("Importance", ascending=True))
        chart(
            px.bar(fi_df, x="Importance", y="Feature", orientation="h",
                   title="Which features drive churn prediction most?",
                   color="Importance", color_continuous_scale="Purples",
                   text_auto=".3f"))

        st.markdown("#### ⚠️ Churn Risk Distribution")
        col1, col2 = st.columns(2)
        with col1:
            risk_counts = churn_df["churn_risk"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level","Count"]
            color_map = {"Low":"#10b981","Medium":"#f59e0b","High":"#ef4444"}
            chart(
                px.pie(risk_counts, names="Risk Level", values="Count",
                       title="Donors by Churn Risk Level",
                       color="Risk Level", color_discrete_map=color_map, hole=0.45))
        with col2:
            chart(
                px.histogram(churn_df, x="churn_probability", nbins=20,
                             title="Churn Probability Distribution",
                             color_discrete_sequence=["#7c3aed"],
                             labels={"churn_probability":"Churn Probability"}))

        high   = int((churn_df["churn_risk"] == "High").sum())
        medium = int((churn_df["churn_risk"] == "Medium").sum())
        low    = int((churn_df["churn_risk"] == "Low").sum())
        metric_row([
            ("High Risk Donors", high, {"help": "Churn probability > 60%"}),
            ("Medium Risk Donors", medium, {"help": "Churn probability 30-60%"}),
            ("Low Risk Donors", low, {"help": "Churn probability < 30%"}),
        ])

        st.markdown("#### 🚨 Top 15 High-Risk Donors")
        high_risk_df = (churn_df[churn_df["churn_risk"] == "High"]
                        .sort_values("churn_probability", ascending=False)
                        .head(15).reset_index(drop=True))
        st.dataframe(
            high_risk_df.style
                .format({"churn_probability":"{:.1%}","amount_cr":"₹{:.2f} Cr"})
                .background_gradient(subset=["churn_probability"], cmap="Reds"),
            use_container_width=True, hide_index=True)

        st.markdown("#### 🗺️ Churn Risk by Sector & State")
        col3, col4 = st.columns(2)
        with col3:
            sector_churn = (churn_df.groupby("sector_focus")["churn_probability"]
                            .mean().reset_index()
                            .sort_values("churn_probability", ascending=False))
            sector_churn.columns = ["Sector","Avg Churn Probability"]
            chart(
                px.bar(sector_churn, x="Avg Churn Probability", y="Sector",
                       orientation="h", title="Avg Churn Risk by Sector",
                       color="Avg Churn Probability",
                       color_continuous_scale="RdYlGn_r", text_auto=".1%"))
        with col4:
            state_churn = (churn_df.groupby("state")["churn_probability"]
                           .mean().reset_index()
                           .sort_values("churn_probability", ascending=False)
                           .head(10))
            state_churn.columns = ["State","Avg Churn Probability"]
            chart(
                px.bar(state_churn, x="Avg Churn Probability", y="State",
                       orientation="h", title="Top 10 States by Churn Risk",
                       color="Avg Churn Probability",
                       color_continuous_scale="RdYlGn_r", text_auto=".1%"))

        st.markdown("#### 💰 Churn Probability vs Donation Amount")
        chart(
            px.scatter(churn_df, x="amount_cr", y="churn_probability",
                       color="churn_risk", size="amount_cr",
                       color_discrete_map={"Low":"#10b981","Medium":"#f59e0b","High":"#ef4444"},
                       hover_data=["donor_name","donor_type","state"],
                       title="Are high-value donors at churn risk?",
                       labels={"amount_cr":"Donation Amount (₹ Cr)",
                               "churn_probability":"Churn Probability"},
                       size_max=30, opacity=0.7))

        st.markdown("#### 💡 Strategic Recommendations")
        top_sector  = sector_churn.iloc[0]["Sector"]
        top_state   = state_churn.iloc[0]["State"]
        top_feature = fi_df.iloc[-1]["Feature"]
        st.info(f"""
        **Best Model:** {best_name} — AUC = {best_row['AUC-ROC']:.4f}

        **Immediate Actions:**
        - 🚨 **{high} donors** are at high churn risk — prioritise outreach campaigns
        - 📍 **{top_state}** has the highest average churn risk among states
        - 🏭 **{top_sector}** sector donors are most likely to churn — review engagement strategy
        - 💳 Focus on converting one-time donors to recurring before they churn
        - 📊 Top churn driver: **{top_feature}** — use this in retention targeting
        """)

    except Exception as e:
        st.error(f"ML Model Error: {e}")
        st.exception(e)
with tab6:
    st.subheader("Cross-Dataset Analysis — 10 Research Questions")
    st.caption("Insights derived by joining NGO, Donor, Program & Beneficiary datasets")

    st.markdown("### Q1 — Which NGO sector receives the most CSR funding?")
    try:
        q1 = cross_mod.q1_sector_csr_funding()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q1, x="sector", y="total_cr",
                       color="total_cr", color_continuous_scale="YlOrRd",
                       title="Total CSR Funding by Sector (₹ Cr)", text_auto=".1f").update_layout(**DARK_LAYOUT))
        with col2:
            chart(
                px.scatter(q1, x="donors", y="total_cr", size="avg_cr", color="sector",
                           title="Donors vs Funding (bubble = avg donation)",
                           labels={"donors":"No. of Donors","total_cr":"Total (₹ Cr)"}).update_layout(**DARK_LAYOUT))
    except Exception as e:
        st.error(f"Q1 Error: {e}")

    st.divider()

    st.markdown("### Q2 — Which programs have the highest beneficiary success rates?")
    try:
        q2 = cross_mod.q2_program_success_rates().dropna(subset=["success_rate"])
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q2.head(12), x="success_rate", y="program_name",
                       orientation="h", color="success_rate",
                       color_continuous_scale="RdYlGn",
                       title="Top 12 Programs by Success Rate (%)", text_auto=".1f"))
        with col2:
            chart(
                px.scatter(q2, x="enrolled", y="success_rate",
                           color="category", size="enrolled",
                           title="Enrolled vs Success Rate (by category)",
                           labels={"enrolled":"Enrolled","success_rate":"Success Rate (%)"},
                           size_max=30, opacity=0.8))
    except Exception as e:
        st.error(f"Q2 Error: {e}")

    st.divider()

    st.markdown("### Q3 — Is CSR budget allocated fairly across states?")
    try:
        q3 = (cross_mod.q3_budget_vs_funding_by_state()
              .sort_values("program_budget", ascending=False).head(12))
        fig_q3 = go.Figure()
        fig_q3.add_trace(go.Bar(name="Program Budget (₹)", x=q3["state"],
                                y=q3["program_budget"], marker_color="#4f46e5"))
        fig_q3.add_trace(go.Bar(name="Donor Funds (scaled)", x=q3["state"],
                                y=q3["donor_funds_cr"] * 1e7, marker_color="#06b6d4"))
        fig_q3.update_layout(barmode="group",
                              title="Program Budget vs Donor Funds by State",
                              xaxis_title="State")
        chart(fig_q3)
    except Exception as e:
        st.error(f"Q3 Error: {e}")

    st.divider()

    st.markdown("### Q4 — What factors predict donor churn?")
    try:
        _, fi, best = ml_churn.get_model_summary()
        fi_df4 = (pd.DataFrame(list(fi.items()), columns=["Feature","Importance"])
                    .sort_values("Importance", ascending=False))
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(fi_df4, x="Importance", y="Feature", orientation="h",
                       color="Importance", color_continuous_scale="Reds",
                       title=f"Churn Factors — {best}", text_auto=".3f"))
        with col2:
            chart(
                px.pie(fi_df4, names="Feature", values="Importance",
                       title="Feature Importance Share", hole=0.4))
    except Exception as e:
        st.error(f"Q4 Error: {e}")

    st.divider()

    st.markdown("### Q5 — Which demographics benefit most from NGO programs?")
    try:
        q5 = cross_mod.q5_demographic_impact()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q5, x="category", y="count", color="gender",
                       barmode="group", title="Beneficiaries by Category & Gender",
                       color_discrete_sequence=["#7c3aed","#06b6d4"]))
        with col2:
            chart(
                px.bar(q5, x="category", y="success_rate", color="gender",
                       barmode="group", title="Success Rate by Category & Gender",
                       color_discrete_sequence=["#7c3aed","#06b6d4"], text_auto=".1f"))
        chart(
            px.scatter(q5, x="bpl_pct", y="success_rate", color="category",
                       size="count", symbol="gender",
                       title="BPL % vs Success Rate (bubble = beneficiary count)",
                       labels={"bpl_pct":"BPL %","success_rate":"Success Rate (%)"},
                       size_max=40))
    except Exception as e:
        st.error(f"Q5 Error: {e}")

    st.divider()

    st.markdown("### Q6 - Do FCRA-registered NGOs run more impactful programs?")
    try:
        q6 = cross_mod.q6_fcra_impact()
        chart(
            px.bar(q6, x="fcra_status", y="avg_success", color="fcra_status",
                   text_auto=".1f", title="Average Success Rate by FCRA Status",
                   hover_data=["programs", "total_enrolled"],
                   labels={"fcra_status": "FCRA Status", "avg_success": "Avg Success Rate (%)"}))
        st.dataframe(q6, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Q6 Error: {e}")

    st.divider()

    st.markdown("### Q7 — Which states have the highest BPL beneficiary coverage?")
    try:
        q7 = cross_mod.q7_state_bpl_coverage()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q7.head(12), x="state", y="bpl_pct",
                       color="bpl_pct", color_continuous_scale="RdYlGn_r",
                       title="BPL Coverage % by State", text_auto=".1f"))
        with col2:
            chart(
                px.scatter(q7, x="bpl_pct", y="success_rate", size="total",
                           color="state",
                           title="BPL Coverage vs Success Rate (bubble = total beneficiaries)",
                           labels={"bpl_pct":"BPL %","success_rate":"Success Rate (%)"},
                           size_max=35))
    except Exception as e:
        st.error(f"Q7 Error: {e}")

    st.divider()

    st.markdown("### Q8 — Does longer program duration improve completion rates?")
    try:
        q8 = cross_mod.q8_duration_vs_completion().dropna()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q8, x="duration_band", y="avg_success",
                       color="avg_success", color_continuous_scale="RdYlGn",
                       title="Avg Success Rate by Duration Band", text_auto=".1f",
                       labels={"duration_band":"Duration",
                               "avg_success":"Avg Success Rate (%)"}))
        with col2:
            chart(
                px.bar(q8, x="duration_band", y="programs",
                       color="avg_enrolled", color_continuous_scale="Blues",
                       title="No. of Programs & Avg Enrolled per Duration Band",
                       text_auto=True))
    except Exception as e:
        st.error(f"Q8 Error: {e}")

    st.divider()

    st.markdown("### Q9 — What is the cost-per-beneficiary across program categories?")
    try:
        q9 = cross_mod.q9_cost_per_beneficiary()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q9, x="category", y="overall_cpb",
                       color="overall_cpb", color_continuous_scale="RdYlGn_r",
                       title="Cost Per Beneficiary by Category (₹)", text_auto=".0f"))
        with col2:
            chart(
                px.scatter(q9, x="total_enrolled", y="overall_cpb",
                           size="total_budget", color="category",
                           title="Enrolled vs Cost-per-Beneficiary (bubble = budget)",
                           labels={"total_enrolled":"Total Enrolled",
                                   "overall_cpb":"Cost Per Beneficiary (₹)"},
                           size_max=40))
        st.dataframe(
            q9.style.format({"overall_cpb":"₹{:,.0f}","total_budget":"₹{:,.0f}"}),
            use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Q9 Error: {e}")

    st.divider()

    st.markdown("### Q10 — Which donor payment modes correlate with retention?")
    try:
        q10 = cross_mod.q10_payment_mode_retention()
        col1, col2 = st.columns(2)
        with col1:
            chart(
                px.bar(q10, x="payment_mode", y="retention_rate",
                       color="retention_rate", color_continuous_scale="RdYlGn",
                       title="Donor Retention Rate by Payment Mode (%)",
                       text_auto=".1f"))
        with col2:
            chart(
                px.scatter(q10, x="total_cr", y="retention_rate",
                           size="count", color="payment_mode",
                           title="Total Funding vs Retention (bubble = donor count)",
                           labels={"total_cr":"Total Funding (₹ Cr)",
                                   "retention_rate":"Retention Rate (%)"},
                           size_max=40))
        st.dataframe(
            q10.style.format({"total_cr":"₹{:.2f} Cr","retention_rate":"{:.1f}%"}),
            use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Q10 Error: {e}")
with tab7:
    st.markdown("""
    <div style="padding:28px 32px 20px;background:#fff;border:1px solid #e2e6f0;border-radius:20px;margin-bottom:24px;">
        <h2 style="margin:0 0 6px;font-size:26px;font-weight:700;color:#0f172a;">📥 Download Reports</h2>
        <p style="margin:0;color:#64748b;font-size:14px;">Export analytics data and the full PDF report for submission or presentation.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── PDF REPORT ──────────────────────────────────────────────────────────────
    st.markdown("### 📄 Full Analytics Report (PDF)")
    st.markdown(
        "<p style=\"color:#64748b;font-size:13px;margin-bottom:12px;\">"
        "Complete 10-page NGO &amp; Donor Analytics Report with cover page, KPIs, "
        "cross-analysis, and strategic recommendations.</p>",
        unsafe_allow_html=True,
    )

    _pdf_col, _ = st.columns([1, 2])
    with _pdf_col:
        _pdf_path = os.path.join(os.path.dirname(__file__), "ngo_analytics_report.pdf")
        if os.path.exists(_pdf_path):
            with open(_pdf_path, "rb") as _f:
                st.download_button(
                    label="⬇️  Download Full PDF Report",
                    data=_f.read(),
                    file_name="ngo_analytics_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.warning("PDF not found. Run `generate_report_pdf.py` to generate it first.")

    st.divider()

    # ── CSV EXPORTS ──────────────────────────────────────────────────────────────
    st.markdown("### 📊 CSV Data Exports")

    csv_col1, csv_col2 = st.columns(2)

    with csv_col1:
        st.markdown("#### 💰 Financial & Donor Data")
        download_reports(data, [
            ("📈 Funding Trend Report",          "year_trend",   "funding_trend_report.csv"),
            ("🏆 Top Donors Report",              "top_donors",   "top_donors_report.csv"),
            ("💳 Payment Mode Retention Report",  "payment_mode", "payment_mode_retention.csv"),
            ("⭐ Donor Engagement Scores",        "engagement",   "donor_engagement_scores.csv"),
        ])

    with csv_col2:
        st.markdown("#### 🎯 Program & Beneficiary Data")
        download_reports(data, [
            ("📋 Program Performance Report",       "category_sum",   "program_performance_report.csv"),
            ("❤️ Beneficiary Demographics Report",  "category_demo",  "beneficiary_demographics_report.csv"),
            ("⚠️ Dropout Analysis Report",          "dropout",        "dropout_analysis.csv"),
            ("🗺️ State BPL Coverage Report",        "state_bpl",      "state_bpl_coverage.csv"),
            ("💵 Cost Per Beneficiary Report",      "cost_per_ben",   "cost_per_beneficiary.csv"),
        ])

st.markdown("""
<div style="text-align:center;padding:32px 0 16px;color:#7a8097;font-size:12px;letter-spacing:0.06em;">
    © Diksha Singla &nbsp;·&nbsp; Roll No. 10 &nbsp;·&nbsp; MCA 2025–26 &nbsp;·&nbsp; NGO & Donor Analytics Report
</div>
""", unsafe_allow_html=True)