import streamlit as st
import numpy as np
import pathlib
from src.data_loader import load_and_clean_hdb_data
from src.visual_components import (
    create_town_depreciation_boxplot,
    create_mrt_proximity_scatter,
    create_parallel_coordinates,
    create_hdb_map,
    create_macro_benchmark_chart
)

st.set_page_config(page_title="SC4024: HDB Visual Analytics", page_icon="🏢", layout="wide")

@st.cache_data
def get_dashboard_data():
    return load_and_clean_hdb_data("data/resale_flat_prices.csv")

df = get_dashboard_data()

# --- Sidebar Controls ---
st.sidebar.title("🔍 Visual Filters")
all_towns = sorted(df['town'].unique().tolist())
selected_towns = st.sidebar.multiselect("Select Towns:", options=all_towns, default=['ANG MO KIO', 'BEDOK', 'CENTRAL AREA', 'PUNGGOL'])

all_types = sorted(df['flat_type'].unique().tolist())
selected_types = st.sidebar.multiselect("Select Flat Types:", options=all_types, default=all_types)

filtered_df = df[
    (df['town'].isin(selected_towns if selected_towns else all_towns)) &
    (df['flat_type'].isin(selected_types if selected_types else all_types))
]

# --- Sidebar Valuation Simulator ---
st.sidebar.divider()
st.sidebar.subheader("🧮 Flat Valuation Simulator")

sim_town = st.sidebar.selectbox("Target Town", sorted(df['town'].unique()))
sim_type = st.sidebar.selectbox("Flat Type", sorted(df['flat_type'].unique()))
sim_area = st.sidebar.slider("Floor Area (Sqm)", 30, 180, 90)
sim_years = st.sidebar.slider("Holding Period (Years)", 1, 20, 5)

matched = df[(df['town'] == sim_town) & (df['flat_type'] == sim_type)]

if not matched.empty:
    avg_depr = matched['depreciation_per_year'].median()
    current_val = matched['price_per_sqm'].median() * sim_area
    est_loss = avg_depr * sim_years
    proj_val = max(0, current_val - est_loss)
    
    st.sidebar.metric("Est. Current Price", f"SGD ${current_val:,.0f}")
    st.sidebar.metric(f"Projected Val ({sim_years} yrs)", f"SGD ${proj_val:,.0f}", delta=f"-${est_loss:,.0f}")

# --- Main Dashboard ---
st.title("🏢 SC4024: HDB Resale & Spatial Analytics Dashboard")

# Top KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{len(filtered_df):,}")
col2.metric("Median Resale Price", f"SGD ${filtered_df['resale_price'].median():,.0f}" if not filtered_df.empty else "N/A")
col3.metric("Median Price / Sqm", f"SGD ${filtered_df['price_per_sqm'].median():,.0f}" if not filtered_df.empty else "N/A")
if 'min_mrt_dist_km' in filtered_df.columns and not filtered_df.empty:
    col4.metric("Avg MRT Distance", f"{filtered_df['min_mrt_dist_km'].mean():.2f} km")

st.divider()

if filtered_df.empty:
    st.warning("⚠️ No HDB records match the current sidebar filter selection. Please broaden your town or flat type selection.")
else:
    # --- Analytical Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Geospatial Map", 
        "🚆 MRT & Location Impact", 
        "🔀 Multi-Attribute Trade-offs",
        "📊 Town Depreciation Spread",
        "📈 Macro Benchmark"
    ])

        # Tab 1: Geospatial Map
    with tab1:
        st.subheader("Interactive Singapore HDB Valuation Map")
        fig_map = create_hdb_map(filtered_df)
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Dynamic calculations on FILTERED data
        town_medians = filtered_df.groupby('town')['price_per_sqm'].median()
        
        if len(town_medians) > 1:
            top_town = town_medians.idxmax()
            top_val = town_medians.max()
            low_town = town_medians.idxmin()
            low_val = town_medians.min()
            
            st.info(
                f"💡 **Filter-Specific Map Insights:**\n\n"
                f"* **Highest Valued in Selection:** **{top_town}** leads at **SGD ${top_val:,.0f} per sqm**.\n"
                f"* **Most Affordable in Selection:** **{low_town}** offers the lowest price at **SGD ${low_val:,.0f} per sqm**.\n"
                f"* **Spread:** There is a **SGD ${(top_val - low_val):,.0f}/sqm gap** between the highest and lowest towns in your selection."
            )
        else:
            single_town = town_medians.index[0]
            single_val = town_medians.iloc[0]
            st.info(
                f"💡 **Filter-Specific Map Insights:**\n\n"
                f"* **Selected Town:** **{single_town}** has a median price of **SGD ${single_val:,.0f} per sqm** across {len(filtered_df):,} filtered transactions."
            )

    # Tab 2: MRT Proximity Scatter
    with tab2:
        st.subheader("Does Proximity to MRT Stations Offset Lease Decay?")
        fig_mrt = create_mrt_proximity_scatter(filtered_df)
        st.plotly_chart(fig_mrt, use_container_width=True)
        
        # Dynamic calculation on FILTERED data
        near_mrt = filtered_df[filtered_df['min_mrt_dist_km'] <= 0.5]
        far_mrt = filtered_df[filtered_df['min_mrt_dist_km'] > 1.0]
        
        if not near_mrt.empty and not far_mrt.empty:
            near_med = near_mrt['price_per_sqm'].median()
            far_med = far_mrt['price_per_sqm'].median()
            premium = ((near_med - far_med) / far_med) * 100
            
            st.info(
                f"💡 **Filter-Specific MRT Insights:**\n\n"
                f"* **Walkable (<500m) Median:** **SGD ${near_med:,.0f}/sqm** ({len(near_mrt):,} flats).\n"
                f"* **Distant (>1km) Median:** **SGD ${far_med:,.0f}/sqm** ({len(far_mrt):,} flats).\n"
                f"* **Current Selection Premium:** Flats within 500m of an MRT command a **{premium:+.1f}% price premium per sqm** in your filtered subset."
            )
        else:
            st.info("💡 **Filter-Specific MRT Insights:** Insufficient spread in MRT distances within current sidebar filters to calculate the distance premium.")

    # Tab 3: Parallel Coordinates
    with tab3:
        st.subheader("Parallel Coordinates: High-Dimensional Trade-off Analysis")
        st.markdown("Drag vertically along any vertical axis line to filter flats matching your criteria.")
        fig_pcoords = create_parallel_coordinates(filtered_df)
        st.plotly_chart(fig_pcoords, use_container_width=True)
        
        med_lease = filtered_df['remaining_lease_years'].median()
        med_price = filtered_df['resale_price'].median()
        med_area = filtered_df['floor_area_sqm'].median()
        
        st.info(
            f"💡 **Current Selection Subset Profile:**\n\n"
            f"* **Median Price:** **SGD ${med_price:,.0f}** | **Median Lease:** **{med_lease:.0f} years** | **Median Size:** **{med_area:.0f} sqm**.\n"
            f"* **Trade-off Pattern:** Comparing the lines across your {len(filtered_df):,} selected transactions reveals how buyers balance floor area against lease age and MRT proximity.\n"
            f"* **Interactive Brushing Tip:** Click and drag vertically along any axis (e.g., **Price**) to isolate specific property profiles."
        )

    # Tab 4: Town Depreciation Spread
    with tab4:
        st.subheader("Town-Level Depreciation Spread")
        fig_box = create_town_depreciation_boxplot(filtered_df)
        st.plotly_chart(fig_box, use_container_width=True)
        
        town_depr = filtered_df.groupby('town')['depreciation_per_year'].median().sort_values(ascending=False)
        
        if len(town_depr) > 1:
            top_depr_town = town_depr.index[0]
            top_depr_val = town_depr.iloc[0]
            low_depr_town = town_depr.index[-1]
            low_depr_val = town_depr.iloc[-1]
            
            st.info(
                f"💡 **Filter-Specific Depreciation Insights:**\n\n"
                f"* **Highest Annual Cost Town:** **{top_depr_town}** at **SGD ${top_depr_val:,.0f}/year**.\n"
                f"* **Lowest Annual Cost Town:** **{low_depr_town}** at **SGD ${low_depr_val:,.0f}/year**.\n"
                f"* **National Baseline comparison:** The red dashed line shows the median annual depreciation across all filtered records."
            )
        else:
            st.info(f"💡 **Filter-Specific Depreciation Insights:** Displaying depreciation spread for **{town_depr.index[0]}** with a median rate of **SGD ${town_depr.iloc[0]:,.0f}/year**.")

    # Tab 5: Macro Benchmark
    with tab5:
        st.subheader("Macro Market Benchmark: HDB Resale vs. Macroeconomic Rates")
        st.markdown("Examine how overall price trends compare against macroeconomic interest rate cycles.")
        fig_macro = create_macro_benchmark_chart(filtered_df)
        st.plotly_chart(fig_macro, use_container_width=True)
        
        sorted_dates = filtered_df.sort_values('transaction_date')
        first_p = sorted_dates['price_per_sqm'].iloc[0]
        last_p = sorted_dates['price_per_sqm'].iloc[-1]
        growth = ((last_p - first_p) / first_p) * 100
        
        st.info(
            f"💡 **Filter-Specific Macro Trend Insights:**\n\n"
            f"* **Selection Price Trajectory:** Median price/sqm shifted from **SGD ${first_p:,.0f}** to **SGD ${last_p:,.0f}** (**{growth:+.1f}% growth**).\n"
            f"* **Interest Rate Impact:** Compare your selection's price curve against the red dashed line (3-Month SORA rate) to see if high interest rates impacted demand."
        )
