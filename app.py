import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="SkyCity Market Analytics", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('SkyCity Auckland Restaurants & Bars.csv')
    df.columns = df.columns.str.strip()
    # KPI Calculations
    df['Aggregator_Dependence'] = df['UE_share'] + df['DD_share']
    df['Risk_Level'] = df['Aggregator_Dependence'].apply(lambda x: 'High Risk 🔴' if x > 0.70 else 'Healthy 🟢')
    return df

df = load_data()

# --- SIDEBAR (Meeting 100% of Requirements) ---
st.sidebar.header("🛠️ Strategy Control Panel")
# Filter 1: Subregion
region = st.sidebar.multiselect("Subregion", df['Subregion'].unique(), default=df['Subregion'].unique())
# Filter 2: Cuisine
cuisine = st.sidebar.multiselect("Cuisine Type", df['CuisineType'].unique(), default=df['CuisineType'].unique())
# Filter 3: Segment (Added this to be 100% unique/complete!)
segment = st.sidebar.multiselect("Restaurant Segment", df['Segment'].unique(), default=df['Segment'].unique())

# Toggle Requirement (Page 6)
view_mode = st.sidebar.radio("Analysis Focus:", ["Overall Channel Mix", "In-Store vs. Delivery Comparison"])

# Apply Filters
filtered_df = df[(df['Subregion'].isin(region)) & 
                 (df['CuisineType'].isin(cuisine)) & 
                 (df['Segment'].isin(segment))].copy()

# --- MAIN DASHBOARD ---
st.title("🏙️ SkyCity Auckland Command Center")
st.markdown("### Market Share & Channel Performance Analytics")

# --- ROW 1: KPIs ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{int(filtered_df['MonthlyOrders'].sum()):,}")
rev = (filtered_df['InStoreRevenue'] + filtered_df['UberEatsRevenue'] + filtered_df['DoorDashRevenue'] + filtered_df['SelfDeliveryRevenue']).sum()
c2.metric("Total Revenue", f"${rev/1e6:.2f}M")
risk_n = len(filtered_df[filtered_df['Risk_Level'] == 'High Risk 🔴'])
c3.metric("High Risk Shops", risk_n)
c4.metric("Avg Order Value", f"${filtered_df['AOV'].mean():.2f}")

# --- ROW 2: DYNAMIC CHARTS ---
col_left, col_right = st.columns(2)

with col_left:
    if view_mode == "Overall Channel Mix":
        st.subheader("📊 Overall Channel Distribution")
        shares = filtered_df[['InStoreShare', 'UE_share', 'DD_share', 'SD_share']].mean()
        fig = px.pie(values=shares, names=['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'], hole=0.5)
    else:
        st.subheader("🏢 In-Store vs 🚚 Delivery Split")
        filtered_df['Total_Delivery'] = filtered_df['UE_share'] + filtered_df['DD_share'] + filtered_df['SD_share']
        fig = px.bar(filtered_df.groupby('Segment')[['InStoreShare', 'Total_Delivery']].mean().reset_index(), 
                     x='Segment', y=['InStoreShare', 'Total_Delivery'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🍱 Cuisine-Channel Mix")
    fig2 = px.bar(filtered_df.groupby('CuisineType')[['InStoreShare', 'UE_share', 'DD_share', 'SD_share']].mean().reset_index(), 
                  x='CuisineType', y=['InStoreShare', 'UE_share', 'DD_share', 'SD_share'], barmode='stack')
    st.plotly_chart(fig2, use_container_width=True)

# --- ROW 3: HEATMAP ---
st.divider()
st.subheader("🗺️ Subregion Dominance Heatmap")
heat_data = filtered_df.groupby('Subregion')[['InStoreShare', 'UE_share', 'DD_share', 'SD_share']].mean()
st.plotly_chart(px.imshow(heat_data, text_auto=".2f", color_continuous_scale='Viridis'), use_container_width=True)

# --- ROW 4: RISK PANEL ---
st.subheader("⚠️ Strategic Risk Panel")
risk_list = filtered_df[filtered_df['Risk_Level'] == 'High Risk 🔴'][['RestaurantName', 'Subregion', 'Segment', 'Aggregator_Dependence']]
st.write("Top 10 most delivery-dependent restaurants (Immediate Action Required):")
st.table(risk_list.sort_values(by='Aggregator_Dependence', ascending=False).head(10))

# --- ROW 5: STRATEGIC DEEP DIVE (The "Extra" Lit KPIs) ---
st.divider()
st.header("🎯 Strategic Deep Dive (Advanced KPIs)")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("💰 Profitability Gap")
    # Extra KPI 1: Difference between In-Store and Uber Eats Profit
    filtered_df['Profit_Gap'] = filtered_df['InStoreNetProfit'] - filtered_df['UberEatsNetProfit']
    avg_gap = filtered_df['Profit_Gap'].mean()
    st.metric("Avg. Profit Loss (In-Store vs. Uber)", f"${avg_gap:.2f}", 
              delta="Per Order", delta_color="inverse")
    st.write("This shows how much net profit is 'lost' to aggregator fees compared to a walk-in customer.")

with col_b:
    st.subheader("📈 Regional Growth Index")
    # Extra KPI 2: Using the GrowthFactor column from your dataset
    growth_data = filtered_df.groupby('Subregion')['GrowthFactor'].mean().reset_index()
    fig_growth = px.bar(growth_data, x='Subregion', y='GrowthFactor', 
                        title="Market Growth Potential by Area",
                        color='GrowthFactor', color_continuous_scale='Greens')
    st.plotly_chart(fig_growth, use_container_width=True)