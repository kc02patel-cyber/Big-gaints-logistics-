import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.figure_factory import create_distplot
from datetime import datetime

st.set_page_config(page_title="Logistics Intelligence Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("logistics_dataset.xlsx")

df = load_data()

st.title("Global Logistics Intelligence Dashboard")
st.markdown("Investor-grade analytics powered by multimodal logistics data.")

# Sidebar filters
st.sidebar.header("Filters")
modes = st.sidebar.multiselect("Transport Mode", df["mode"].unique(), default=df["mode"].unique())
status = st.sidebar.multiselect("Status", df["status"].unique(), default=df["status"].unique())
df_f = df[df["mode"].isin(modes) & df["status"].isin(status)]

# ==========================
# KPIs
# ==========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", len(df_f))
col2.metric("Delivered %", f"{round((df_f['status']=='Delivered').mean()*100,2)}%")
col3.metric("Avg Lead Time (Days)", round(df_f["lead_time_days"].mean(),2))
col4.metric("Total Cargo Value (USD)", f"${round(df_f['cargo_value_usd'].sum(),2):,}")

st.markdown("---")

# ==========================
# 1. Sankey Diagram (Top-1%: Flow Visualization)
# ==========================
st.subheader("Flow: Origin → Mode → Destination (Sankey)")
sankey_df = df_f.groupby(["origin_country","mode","destination_country"]).size().reset_index(name="count")

nodes = list(pd.unique(sankey_df[["origin_country","mode","destination_country"]].values.ravel()))
node_index = {node:i for i,node in enumerate(nodes)}

sources = sankey_df["origin_country"].map(node_index)
intermediate = sankey_df["mode"].map(node_index)
targets = sankey_df["destination_country"].map(node_index)

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(label=nodes),
    link=dict(
        source=sources.tolist() + intermediate.tolist(),
        target=intermediate.tolist() + targets.tolist(),
        value=sankey_df["count"].tolist() + sankey_df["count"].tolist()
))])
st.plotly_chart(fig_sankey, use_container_width=True)

st.markdown("---")

# ==========================
# 2. Treemap (Hierarchical)
# ==========================
st.subheader("Hierarchy: Mode → Carrier → Container Type (Treemap)")
fig_tree = px.treemap(df_f,
    path=["mode","carrier","container_type"],
    values="cargo_value_usd",
    color="mode")
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")

# ==========================
# 3. Chord-style Network (Origin vs Destination Matrix)
# ==========================
st.subheader("Trade Relationships (Origin vs Destination Matrix)")
matrix = df_f.pivot_table(index="origin_country", columns="destination_country", values="shipment_id", aggfunc="count").fillna(0)
fig_heat = px.imshow(matrix, text_auto=True, aspect="auto")
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ==========================
# 4. Ridgeline Density (Lead Time by Mode)
# ==========================
st.subheader("Lead Time Distribution by Mode (Ridgeline Style)")
fig_ridge = px.violin(df_f, x="lead_time_days", y="mode", color="mode", orientation="h", box=False, points=False)
st.plotly_chart(fig_ridge, use_container_width=True)

st.markdown("---")

# ==========================
# 5. Beeswarm (Value Distribution)
# ==========================
st.subheader("Cargo Value Distribution (Beeswarm)")
fig_bee = px.strip(df_f, x="cargo_value_usd", color="mode")
st.plotly_chart(fig_bee, use_container_width=True)

st.markdown("---")

# ==========================
# 6. Sunburst (Category Tree)
# ==========================
st.subheader("Category Breakdown (Sunburst)")
fig_sun = px.sunburst(df_f, path=["origin_country","mode","status"], values="cargo_weight_kg", color="status")
st.plotly_chart(fig_sun, use_container_width=True)

st.markdown("---")

# ==========================
# 7. KPI Trends (Sparkline Table)
# ==========================
st.subheader("Shipment Trend Sparklines (Monthly)")

df_f["month"] = pd.to_datetime(df_f["departure_date"]).dt.to_period("M").astype(str)
trend = df_f.groupby("month").size().reset_index(name="count")

spark = px.line(trend, x="month", y="count")
spark.update_layout(height=200)
st.plotly_chart(spark, use_container_width=True)

st.markdown("---")

# ==========================
# 8. Hexbin Approx. (Distance vs Value)
# ==========================
st.subheader("Density: Distance vs Value (Hexbin Approx)")
fig_hex = px.scatter(df_f, x="distance_km", y="cargo_value_usd", opacity=0.4)
st.plotly_chart(fig_hex, use_container_width=True)

st.markdown("End of report.")
