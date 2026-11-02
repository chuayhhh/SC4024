import streamlit as st
import numpy as np
import pandas as pd
import pathlib
from src.data_loader import load_and_clean_hdb_data
from src.visual_components import (
    create_town_depreciation_boxplot,
    create_mrt_proximity_scatter,
    create_school_proximity_scatter,
    create_parallel_coordinates,
    create_hdb_map,
    create_macro_benchmark_chart
)

st.set_page_config(
    page_title="SC4024: HDB Resale Visual Analytics", 
    page_icon="🏢", 
    layout="wide"
)

@st.cache_data
def get_dashboard_data():
    return load_and_clean_hdb_data("data/resale_flat_prices_edited.csv")

df = get_dashboard_data()

# --- Sidebar Controls ---
st.sidebar.title("🔍 Multi-Attribute Filters")
st.sidebar.markdown("Filter transaction records dynamically across all visual analytics components.")

all_towns = sorted(df['town'].unique().tolist())
selected_towns = st.sidebar.multiselect(
    "Select Towns:", 
    options=all_towns, 
    default=['ANG MO KIO', 'BEDOK', 'CENTRAL AREA', 'PUNGGOL']
)

all_types = sorted(df['flat_type'].unique().tolist())
selected_types = st.sidebar.multiselect(
    "Select Flat Types:", 
    options=all_types, 
    default=all_types
)

filtered_df = df[
    (df['town'].isin(selected_towns if selected_towns else all_towns)) &
    (df['flat_type'].isin(selected_types if selected_types else all_types))
]

# --- Sidebar Valuation Simulator ---
st.sidebar.divider()
st.sidebar.subheader("🧮 Flat Valuation & Holding Simulator")
st.sidebar.caption("Estimate projected capital preservation over time based on town-specific lease decay rates.")

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
    
    st.sidebar.metric("Est. Current Valuation", f"SGD ${current_val:,.0f}")
    st.sidebar.metric(
        f"Projected Val ({sim_years} yrs)", 
        f"SGD ${proj_val:,.0f}", 
        delta=f"-SGD ${est_loss:,.0f} holding decay"
    )

# --- Main Header ---
st.title("🏢 SC4024: Singapore HDB Resale & Spatial Analytics Dashboard")
st.markdown(
    "An interactive visual analytics tool examining high-dimensional trade-offs, spatial proximity decay (MRT, CBD & Schools), "
    "and macroeconomic interest rate impacts across Singapore's public housing market."
)

# Top Metric Summary Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Transactions", f"{len(filtered_df):,}")
col2.metric("Median Resale Price", f"SGD ${filtered_df['resale_price'].median():,.0f}" if not filtered_df.empty else "N/A")
col3.metric("Median Price / Sqm", f"SGD ${filtered_df['price_per_sqm'].median():,.0f}" if not filtered_df.empty else "N/A")

if 'min_mrt_dist_km' in filtered_df.columns and not filtered_df.empty:
    col4.metric("Avg MRT Distance", f"{filtered_df['min_mrt_dist_km'].mean():.2f} km")
if 'cbd_dist_km' in filtered_df.columns and not filtered_df.empty:
    col5.metric("Avg CBD Distance", f"{filtered_df['cbd_dist_km'].mean():.2f} km")

st.divider()

if filtered_df.empty:
    st.warning("⚠️ No HDB records match the active filter selection. Please broaden your sidebar choices.")
else:
    # --- Analytical Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Geospatial Spatial Map", 
        "🚆 MRT & School Location Proximity", 
        "🔀 Multi-Attribute Trade-offs",
        "📊 Town Depreciation Spread",
        "📈 Macro Benchmark"
    ])

    # --- TAB 1: GEOSPATIAL MAP ---
    with tab1:
        st.subheader("Interactive Singapore Spatial Price Distribution")
        st.caption("👇 Click on any point on the map to reveal specific flat details below.")
        
        fig_map = create_hdb_map(filtered_df)
        map_selection = st.plotly_chart(
            fig_map, 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points",
            key="tab1_map"
        )
        
        town_medians = filtered_df.groupby('town')['price_per_sqm'].median()
        
        if len(town_medians) > 1:
            top_town = town_medians.idxmax()
            top_val = town_medians.max()
            low_town = town_medians.idxmin()
            low_val = town_medians.min()
            
            cbd_avg = filtered_df['cbd_dist_km'].mean() if 'cbd_dist_km' in filtered_df.columns else 0
            mrt_avg = filtered_df['min_mrt_dist_km'].mean() if 'min_mrt_dist_km' in filtered_df.columns else 0
            sch_avg = filtered_df['nearest_distance_to_school_m'].mean() if 'nearest_distance_to_school_m' in filtered_df.columns else 0
            
            st.info(
                f"💡 Spatial Overview Insights:\n\n"
                f"🏆 Highest Valued Region: {top_town} commands the highest median valuation at SGD ${top_val:,.0f} / sqm.\n\n"
                f"🏠 Baseline Region: {low_town} provides the entry-level baseline at SGD ${low_val:,.0f} / sqm.\n\n"
                f"📊 Valuation Spread: A regional gap of SGD ${(top_val - low_val):,.0f} / sqm exists within your active selection.\n\n"
                f"📍 Spatial Proximity Profile: Selected flats average {cbd_avg:.1f} km from the CBD, {mrt_avg:.2f} km from the nearest MRT, and {sch_avg:.0f} m from a school."
            )

        # Tab 1 Click Detail Panel
        if map_selection and "points" in map_selection["selection"] and len(map_selection["selection"]["points"]) > 0:
            point = map_selection["selection"]["points"][0]
            lat = point.get("lat")
            lon = point.get("lon")
            
            clicked_flat = filtered_df[
                (np.isclose(filtered_df['latitude'], lat, atol=0.0001)) & 
                (np.isclose(filtered_df['longitude'], lon, atol=0.0001))
            ]
            
            if not clicked_flat.empty:
                row = clicked_flat.iloc[0]
                addr_name = row.get('full_address', row.get('address', f"Block {row['block']} {row['street_name']}"))
                st.success(
                    f"🔍 Selected Flat Detailed Breakdown:\n\n"
                    f"📍 Location: {addr_name} ({row['town']})\n\n"
                    f"💰 Resale Price: SGD ${row['resale_price']:,.0f}  |  Unit Rate: SGD ${row['price_per_sqm']:,.0f} / sqm\n\n"
                    f"📐 Flat Specifications: {row['flat_type']}  |  {row['floor_area_sqm']} sqm  |  {row['remaining_lease_years']} years lease remaining\n\n"
                    f"🚆 Transit Access: {row.get('nearest_mrt', 'N/A')} ({row.get('min_mrt_dist_km', 0):.2f} km away  |  Exit: {row.get('nearest_mrt_exit', 'N/A')})\n\n"
                    f"🏫 School Proximity: {row.get('nearest_school', 'N/A')} ({row.get('nearest_distance_to_school_m', 0):.0f} meters away)\n\n"
                    f"🏙️ CBD Distance: {row.get('cbd_dist_km', 0):.2f} km to Central Business District"
                )

    # --- TAB 2: MRT & SCHOOL LOCATION PROXIMITY ---
    with tab2:
        st.subheader("Transit & School Distance Decay Analysis")
        st.caption("👇 Click on any scatter point to inspect location details below.")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("##### 🚆 MRT Distance Decay")
            fig_mrt = create_mrt_proximity_scatter(filtered_df)
            mrt_click = st.plotly_chart(
                fig_mrt, 
                use_container_width=True, 
                on_select="rerun", 
                selection_mode="points",
                key="tab2_mrt"
            )
            
        with col_right:
            st.markdown("##### 🏫 Primary / Secondary School Proximity Decay")
            fig_school = create_school_proximity_scatter(filtered_df)
            school_click = None
            if fig_school:
                school_click = st.plotly_chart(
                    fig_school, 
                    use_container_width=True, 
                    on_select="rerun", 
                    selection_mode="points",
                    key="tab2_school"
                )
            else:
                st.info("School proximity features unavailable in dataset.")

        # Overview Insights Callout
        near_mrt = filtered_df[filtered_df['min_mrt_dist_km'] <= 0.5] if 'min_mrt_dist_km' in filtered_df.columns else pd.DataFrame()
        far_mrt = filtered_df[filtered_df['min_mrt_dist_km'] > 1.0] if 'min_mrt_dist_km' in filtered_df.columns else pd.DataFrame()
        
        near_sch = filtered_df[filtered_df['nearest_distance_to_school_m'] <= 500] if 'nearest_distance_to_school_m' in filtered_df.columns else pd.DataFrame()
        far_sch = filtered_df[filtered_df['nearest_distance_to_school_m'] > 1000] if 'nearest_distance_to_school_m' in filtered_df.columns else pd.DataFrame()

        mrt_insight_str = ""
        if not near_mrt.empty and not far_mrt.empty:
            mrt_premium = ((near_mrt['price_per_sqm'].median() - far_mrt['price_per_sqm'].median()) / far_mrt['price_per_sqm'].median()) * 100
            mrt_insight_str = f"🚆 MRT Transit Premium: Flats within 500m of an MRT command a {mrt_premium:+.1f}% price premium per sqm over flats >1km away.\n\n"

        sch_insight_str = ""
        if not near_sch.empty and not far_sch.empty:
            sch_premium = ((near_sch['price_per_sqm'].median() - far_sch['price_per_sqm'].median()) / far_sch['price_per_sqm'].median()) * 100
            sch_insight_str = f"🏫 School Zone Premium: Flats within 500m of a school command a {sch_premium:+.1f}% price premium per sqm over flats >1km away.\n\n"

        st.info(
            f"💡 Spatial Proximity Insights:\n\n"
            f"{mrt_insight_str}"
            f"{sch_insight_str}"
            f"📍 Location Premium Synergy: Flats positioned within both a 500m MRT zone and a 1km school priority radius experience the lowest lease-adjusted valuation decay."
        )

        # Tab 2 Fixed Click Detail Panel
        mrt_pts = mrt_click["selection"]["points"] if (mrt_click and "selection" in mrt_click and "points" in mrt_click["selection"]) else []
        sch_pts = school_click["selection"]["points"] if (school_click and "selection" in school_click and "points" in school_click["selection"]) else []

        clicked_flat = pd.DataFrame()

        if len(mrt_pts) > 0:
            pt = mrt_pts[0]
            mrt_x = pt.get("x")
            price_y = pt.get("y")
            
            clicked_flat = filtered_df[
                (np.isclose(filtered_df['min_mrt_dist_km'], mrt_x, atol=0.01)) & 
                (np.isclose(filtered_df['price_per_sqm'], price_y, atol=2.0))
            ]

        elif len(sch_pts) > 0:
            pt = sch_pts[0]
            sch_x = pt.get("x")
            price_y = pt.get("y")
            
            clicked_flat = filtered_df[
                (np.isclose(filtered_df['nearest_distance_to_school_m'], sch_x, atol=5.0)) & 
                (np.isclose(filtered_df['price_per_sqm'], price_y, atol=2.0))
            ]

        if not clicked_flat.empty:
            row = clicked_flat.iloc[0]
            addr_name = row.get('full_address', row.get('address', f"Block {row['block']} {row['street_name']}"))
            st.success(
                f"🎯 Clicked Property Detailed Breakdown:\n\n"
                f"📍 Address & Town: {addr_name} ({row['town']})\n\n"
                f"💰 Resale Price: SGD ${row['resale_price']:,.0f}  |  Unit Rate: SGD ${row['price_per_sqm']:,.0f} / sqm\n\n"
                f"🚆 Transit Proximity: {row.get('nearest_mrt', 'MRT')} ({row.get('min_mrt_dist_km', 0):.2f} km away  |  Exit: {row.get('nearest_mrt_exit', 'N/A')})\n\n"
                f"🏫 School Proximity: {row.get('nearest_school', 'School')} ({row.get('nearest_distance_to_school_m', 0):.0f} meters away)\n\n"
                f"📐 Flat Specifications: {row['flat_type']}  |  {row['floor_area_sqm']} sqm  |  {row['remaining_lease_years']} years lease remaining"
            )

    # --- TAB 3: PARALLEL COORDINATES BRUSHING ---
    with tab3:
        st.subheader("High-Dimensional Multi-Variable Brushing")
        st.markdown(
            "Interactive Brushing Instructions: Click and drag vertically along any vertical axis line to isolate specific property profiles."
        )
        
        fig_pcoords = create_parallel_coordinates(filtered_df)
        st.plotly_chart(fig_pcoords, use_container_width=True)
        
        med_lease = filtered_df['remaining_lease_years'].median()
        med_price = filtered_df['resale_price'].median()
        med_area = filtered_df['floor_area_sqm'].median()
        med_cbd = filtered_df['cbd_dist_km'].median() if 'cbd_dist_km' in filtered_df.columns else 0
        med_sch = filtered_df['nearest_distance_to_school_m'].median() if 'nearest_distance_to_school_m' in filtered_df.columns else 0
        
        st.info(
            f"💡 High-Dimensional Trade-off Summary:\n\n"
            f"📊 Active Filtered Profile: Median Price of SGD ${med_price:,.0f}  |  Median Lease of {med_lease:.0f} years  |  Median Size of {med_area:.0f} sqm  |  Median CBD Dist of {med_cbd:.1f} km  |  Median School Dist of {med_sch:.0f} m.\n\n"
            f"🔀 Key Trade-off Insight: Lower resale price points require buyers to trade off remaining lease length or accept increased transit and CBD distances."
        )

        st.success(
            f"🔀 Active Selection Axis Spectrum ({len(filtered_df):,} Matching Flats):\n\n"
            f"💰 Price Spectrum: SGD ${filtered_df['resale_price'].min():,.0f} to SGD ${filtered_df['resale_price'].max():,.0f}\n\n"
            f"⏳ Remaining Lease Spectrum: {filtered_df['remaining_lease_years'].min():.1f} yrs to {filtered_df['remaining_lease_years'].max():.1f} yrs\n\n"
            f"🏫 School Proximity Range: {filtered_df['nearest_distance_to_school_m'].min():.0f} m to {filtered_df['nearest_distance_to_school_m'].max():.0f} m\n\n"
            f"🏙️ CBD Distance Range: {filtered_df['cbd_dist_km'].min():.1f} km to {filtered_df['cbd_dist_km'].max():.1f} km"
        )

    # --- TAB 4: TOWN DEPRECIATION SPREAD ---
    with tab4:
        st.subheader("Leasehold Depreciation Risk & Town-Level Holding Costs")
        st.caption("👇 Click on any town boxplot to view specific town statistics below.")
        
        fig_box = create_town_depreciation_boxplot(filtered_df)
        box_click = st.plotly_chart(
            fig_box, 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points",
            key="tab4_box"
        )
        
        town_depr = filtered_df.groupby('town')['depreciation_per_year'].median().sort_values(ascending=False)
        
        if len(town_depr) > 1:
            st.info(
                f"💡 Depreciation Risk Insights:\n\n"
                f"📈 Highest Annual Cost Town: {town_depr.index[0]} at SGD ${town_depr.iloc[0]:,.0f} / year.\n\n"
                f"📉 Lowest Annual Cost Town: {town_depr.index[-1]} at SGD ${town_depr.iloc[-1]:,.0f} / year.\n\n"
                f"📌 Baseline Reference: The dashed horizontal line indicates the median annual holding cost across all selected towns."
            )

        # Tab 4 Click Detail Panel
        if box_click and "points" in box_click["selection"] and len(box_click["selection"]["points"]) > 0:
            point = box_click["selection"]["points"][0]
            clicked_town = point.get("x")
            
            town_data = filtered_df[filtered_df['town'] == clicked_town]
            if not town_data.empty:
                med_depr = town_data['depreciation_per_year'].median()
                med_p = town_data['resale_price'].median()
                med_l = town_data['remaining_lease_years'].median()
                med_sch = town_data['nearest_distance_to_school_m'].median() if 'nearest_distance_to_school_m' in town_data.columns else 0
                med_mrt = town_data['min_mrt_dist_km'].median() if 'min_mrt_dist_km' in town_data.columns else 0
                
                st.success(
                    f"📊 Selected Town Deep-Dive ({clicked_town}):\n\n"
                    f"🏠 Total Transactions in Subset: {len(town_data):,} HDB flats\n\n"
                    f"💸 Median Annual Holding Depreciation: SGD ${med_depr:,.0f} / year\n\n"
                    f"💰 Median Resale Price: SGD ${med_p:,.0f}  |  Median Lease: {med_l:.1f} years remaining\n\n"
                    f"📍 Town Proximity Profile: Avg {med_mrt:.2f} km to MRT  |  Avg {med_sch:.0f} m to School"
                )

    # --- TAB 5: MACRO BENCHMARK ---
    with tab5:
        st.subheader("Macroeconomic Benchmark: Resale Trajectory vs. 3-Month SORA Rates")
        st.caption("👇 Click on any point on the trend line to inspect historical market data below.")
        
        fig_macro = create_macro_benchmark_chart(filtered_df)
        macro_click = st.plotly_chart(
            fig_macro, 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points",
            key="tab5_macro"
        )
        
        sorted_dates = filtered_df.sort_values('transaction_date')
        first_p = sorted_dates['price_per_sqm'].iloc[0]
        last_p = sorted_dates['price_per_sqm'].iloc[-1]
        growth = ((last_p - first_p) / first_p) * 100
        
        st.info(
            f"💡 Macro Economic Insights:\n\n"
            f"📈 Market Trajectory: Price per sqm shifted from SGD ${first_p:,.0f} to SGD ${last_p:,.0f} ({growth:+.1f}% overall change).\n\n"
            f"🏦 Interest Rate Impact: Compare price movement during low SORA rate environments vs recent mortgage rate adjustment cycles."
        )

        # Tab 5 Click Detail Panel
        if macro_click and "points" in macro_click["selection"] and len(macro_click["selection"]["points"]) > 0:
            point = macro_click["selection"]["points"][0]
            selected_date = point.get("x")
            
            m_data = filtered_df[filtered_df['transaction_date'].dt.strftime('%Y-%m') == str(selected_date)[:7]]
            vol = len(m_data) if not m_data.empty else "N/A"
            med_m_p = m_data['resale_price'].median() if not m_data.empty else 0
            
            st.success(
                f"📈 Selected Transaction Timeframe Breakdown ({selected_date}):\n\n"
                f"📅 Transaction Month: {selected_date}\n\n"
                f"📊 Monthly Sales Volume: {vol} HDB flats sold\n\n"
                f"💰 Recorded Median Resale Price: SGD ${med_m_p:,.0f}  (SGD ${point.get('y', 0):,.0f} / sqm)\n\n"
                f"🏦 Macro Environment: Reflects market demand during the benchmark mortgage interest rate of that quarter."
            )
