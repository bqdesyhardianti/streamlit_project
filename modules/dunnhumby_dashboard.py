import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# Show Project Dashboard
# =====================================================
def show():

    # -----------------------------
    # KPI Card Styling
    # -----------------------------
    st.markdown(
        """
        <style>
        [data-testid="metric-container"] {
            background-color: #f5f7fa;
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Title
    # -----------------------------
    st.title("🛒 DUNNHUMBY Customer Insight Dashboard")
    st.caption("Retail performance, segmentation & strategic cluster insights")

    # -----------------------------
    # Load Data
    # -----------------------------
    df = pd.read_csv(
        "projects/dunnhumby_customer_insight/data/processed/cluster_final.csv"
    )

    # -----------------------------
    # Filter Panel
    # -----------------------------
    st.markdown("### 🎯 Filters")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        cluster = st.selectbox(
            "Cluster",
            ["All"] + sorted(df["Cluster_Name"].dropna().unique()),
        )
    with f2:
        rfm = st.selectbox(
            "RFM Segment",
            ["All"] + sorted(df["RFM_segment"].dropna().unique()),
        )
    with f3:
        strategy = st.selectbox(
            "Strategy",
            ["All"] + sorted(df["Strategy"].dropna().unique()),
        )
    with f4:
        income = st.selectbox(
            "Income Group",
            ["All"] + sorted(df["income_desc"].dropna().unique()),
        )

    # -----------------------------
    # Apply Filters
    # -----------------------------
    df_f = df.copy()
    if cluster != "All":
        df_f = df_f[df_f["Cluster_Name"] == cluster]
    if rfm != "All":
        df_f = df_f[df_f["RFM_segment"] == rfm]
    if strategy != "All":
        df_f = df_f[df_f["Strategy"] == strategy]
    if income != "All":
        df_f = df_f[df_f["income_desc"] == income]

    # =====================================================
    # KPI ROW
    # =====================================================
    st.subheader("📊 Executive KPIs")
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric("💰 Total Sales", f"${df_f['Monetary'].sum():,.0f}")
    k2.metric("🧾 Transactions", f"{df_f['num_transactions'].sum():,}")
    k3.metric("👨‍👩‍👧 Households", f"{df_f['household_key'].nunique():,}")
    k4.metric("🛒 Avg Basket", f"${df_f['avg_basket_value'].mean():,.2f}")
    k5.metric("🎯 Price Index", f"{df_f['avg_price_index'].mean():.2f}")
    k6.metric("💸 Discount Ratio", f"{df_f['discount_ratio'].mean():.2%}")

    st.markdown("---")

    # =====================================================
    # TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs(
        ["📊 Executive Overview", "🧍 Customer Segmentation", "🎯 Cluster Strategy"]
    )

    # =====================================================
    # TAB 1 — EXECUTIVE OVERVIEW
    # =====================================================
    with tab1:
        st.subheader("Executive Overview")

        c1, c2 = st.columns(2)

        with c1:
            sales_cluster = (
                df_f.groupby("Cluster_Name")
                .agg(total_sales=("Monetary", "sum"))
                .reset_index()
            )
            fig = px.bar(
                sales_cluster,
                x="Cluster_Name",
                y="total_sales",
                title="Sales by Cluster",
                text="total_sales",
                labels={"Cluster_Name":"Cluster", "total_sales":"Total Sales"}
            )
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            rfm_dist = (
                df_f.groupby("RFM_segment")
                .agg(households=("household_key", "nunique"))
                .reset_index()
            )
            fig = px.pie(
                rfm_dist,
                names="RFM_segment",
                values="households",
                title="RFM Segment Share",
                hole=0.45
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Price Sensitivity vs Discount Ratio")
        fig = px.scatter(
            df_f,
            x="avg_price_index",
            y="discount_ratio",
            color="Cluster_Name",
            size="Monetary",
            hover_data=["household_key"],
            title="Price Sensitivity vs Discount Ratio"
        )
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TAB 2 — CUSTOMER SEGMENTATION
    # =====================================================
    with tab2:
        st.subheader("Cluster Behavioral Profile")
        profile = df.groupby("Cluster_Name")[
            ["Avg_Recency","Avg_Frequency","Avg_Monetary","Avg_discount_ratio","Avg_sku_mix"]
        ].mean().reset_index()

        selected = st.selectbox("Select Cluster Profile", profile["Cluster_Name"])
        row = profile[profile["Cluster_Name"] == selected]
        metrics = ["Avg_Recency","Avg_Frequency","Avg_Monetary","Avg_discount_ratio","Avg_sku_mix"]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=row[metrics].values.flatten(),
                theta=metrics,
                fill="toself",
                name=selected
            )
        )
        fig.update_layout(title="Cluster Radar Profile", polar=dict(radialaxis=dict(visible=True)))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Average Spend by Income Group")
        income_spend = df_f.groupby("income_desc").agg(avg_spend=("Monetary","mean")).reset_index()
        fig = px.bar(
            income_spend,
            x="income_desc",
            y="avg_spend",
            title="Average Spend by Income Group",
            text="avg_spend"
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TAB 3 — CLUSTER STRATEGY
    # =====================================================
    with tab3:
        st.subheader("Cluster Strategy Matrix")
        strat_tbl = df.groupby(["Cluster_Name","Strategy","Guardrail"]).agg(
            avg_sales=("Monetary","mean"),
            avg_discount=("discount_ratio","mean"),
            households=("household_key","nunique")
        ).reset_index()

        st.dataframe(strat_tbl.sort_values("avg_sales", ascending=False), use_container_width=True)

        st.markdown("### Top 10 Brands by Revenue")
        top_brand = df_f.groupby("brand").agg(revenue=("Monetary","sum")).sort_values("revenue",ascending=False).head(10).reset_index()
        fig = px.bar(
            top_brand,
            x="revenue",
            y="brand",
            orientation="h",
            text="revenue",
            title="Top 10 Brands by Revenue"
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
