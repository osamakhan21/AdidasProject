import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Adidas Dashboard", layout="wide")

# --- CUSTOM STYLING: Modern Dark Blue Theme + Glassmorphism + Styled Sidebar ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #001f3f;
            color: #f1f1f1;
        }

        header {
            background-color: #002c5f;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        }

        header h1 {
            color: #ffffff;
            font-size: 2.2rem;
            margin: 0;
            letter-spacing: 1px;
        }

        .stRadio > div {
            flex-direction: row !important;
            gap: 1rem;
        }

        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        div[data-testid="metric-container"]:hover {
            box-shadow: 0px 0px 8px rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }

        section[data-testid="stSidebar"] {
            background-color: #002d4d !important;
            padding: 2rem 1rem 2rem 1rem;
            color: #f1f1f1 !important;
            border-right: 2px solid #003d66;
            font-family: 'Inter', sans-serif;
            box-shadow: 2px 0 12px rgba(0,0,0,0.3);
        }

        section[data-testid="stSidebar"] .stMarkdown {
            font-size: 1.2rem;
            font-weight: bold;
            color: #ffcc00;
            margin-bottom: 1.5rem;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #004aad;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)


# --- HEADER ---
st.markdown('<header><h1>📊 Adidas US Sales Dashboard</h1></header>', unsafe_allow_html=True)


# --- LOAD DATA ---
file_path = "data/Adidas US Sales Datasets.xlsx"
df = pd.read_excel(file_path)
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("### 📁 <span style='color:#ffcc00'>Filters</span>", unsafe_allow_html=True)
min_date = df['Invoice Date'].min()
max_date = df['Invoice Date'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

regions = ["All"] + sorted(df['Region'].dropna().unique())
products = ["All"] + sorted(df['Product'].dropna().unique())

selected_region = st.sidebar.selectbox("Select Region", regions)
selected_product = st.sidebar.selectbox("Select Product", products)

# --- FILTER LOGIC ---
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df['Invoice Date'] >= pd.to_datetime(start_date)) & (filtered_df['Invoice Date'] <= pd.to_datetime(end_date))]

if selected_region != "All":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df['Product'] == selected_product]

if filtered_df.empty:
    st.warning("⚠️ No data found for selected filters.")
    st.stop()

# --- VIEW TOGGLE ---
view = st.radio("Choose View:", ["📋 Table View", "📈 Graph View"], horizontal=True)

# ===================== TABLE VIEW =====================
if view == "📋 Table View":
    st.subheader("📋 Detailed Sales Table")
    st.dataframe(filtered_df, use_container_width=True)

# ===================== GRAPH VIEW =====================
else:
    st.subheader("📈 Visual Insights")

    # --- KPIs ---
    k1, k2, k3 = st.columns(3)
    k4, k5 = st.columns(2)
    k1.metric("💰 Total Sales", f"${filtered_df['Total Sales'].sum():,.2f}")
    k2.metric("📦 Units Sold", f"{filtered_df['Units Sold'].sum():,}")
    k3.metric("📉 Operating Margin", f"{filtered_df['Operating Margin'].mean():.2f}")
    k4.metric("🏦 Operating Profit", f"${filtered_df['Operating Profit'].sum():,.2f}")
    k5.metric("🧮 Price per Unit", f"${filtered_df['Price per Unit'].mean():.2f}")

    st.markdown("---")

    # --- CHART: Monthly Sales ---
    if 'Month' in filtered_df.columns:
        month_data = filtered_df.groupby('Month')['Total Sales'].sum().reset_index()
        fig_month = px.bar(
            month_data,
            x='Month',
            y='Total Sales',
            title="🗓️ Monthly Sales",
            template='plotly_dark',
            color_discrete_sequence=['#007bff']
        )
        fig_month.update_layout(height=450)
        st.plotly_chart(fig_month, use_container_width=True)

    # --- CHART: Sales by Product ---
    if 'Product' in filtered_df.columns:
        product_data = filtered_df.groupby('Product')['Total Sales'].sum().reset_index().sort_values(by='Total Sales')
        fig_product = px.bar(
            product_data,
            x='Total Sales',
            y='Product',
            orientation='h',
            title="📦 Sales by Product",
            color='Total Sales',
            color_continuous_scale='Blues',
            template='plotly_dark'
        )
        fig_product.update_layout(height=450)
        st.plotly_chart(fig_product, use_container_width=True)

    # --- CHART: Sales by Region ---
    if 'Region' in filtered_df.columns:
        region_data = filtered_df.groupby('Region')['Total Sales'].sum().reset_index()
        fig_region = px.bar(
            region_data,
            x='Region',
            y='Total Sales',
            title="🗺️ Sales by Region",
            text_auto='.2s',
            color='Region',
            color_discrete_sequence=px.colors.sequential.Blues,
            template='plotly_dark'
        )
        fig_region.update_traces(marker_line_width=1.5)
        fig_region.update_layout(height=450)
        st.plotly_chart(fig_region, use_container_width=True)

    # --- CHART: Sales by State ---
    if 'State' in filtered_df.columns:
        state_data = filtered_df.groupby('State')['Total Sales'].sum().reset_index().sort_values(by='Total Sales', ascending=False)
        fig_state = go.Figure(data=[
            go.Bar(
                x=state_data['State'],
                y=state_data['Total Sales'],
                marker=dict(color='rgba(0,91,187,0.7)'),
            )
        ])
        fig_state.update_layout(
            title="🏙️ Sales by State",
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            height=450
        )
        st.plotly_chart(fig_state, use_container_width=True)
        st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="adidas_filtered_data.csv",
        mime='text/csv'
        )
