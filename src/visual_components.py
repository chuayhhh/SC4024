import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

# --- Uniform Styling Constants ---
CHART_HEIGHT = 520
STANDARD_MARGINS = dict(l=60, r=40, t=30, b=50)


def create_hdb_map(df):
    """
    Tab 1: Geospatial Scatter Map of HDB Flats across Singapore.
    Updated to display Nearest School, School Distance, and MRT Exit on hover.
    """
    plot_df = df.dropna(subset=['latitude', 'longitude']).copy()
    if len(plot_df) > 2500:
        plot_df = plot_df.sample(2500, random_state=42)

    # Safe fallback between 'address' and Weng Shi's 'full_address'
    hover_addr = 'address' if 'address' in plot_df.columns else 'full_address'

    # Build dynamic hover dictionary based on available enriched columns
    hover_dict = {
        "town": True,
        "resale_price": ":$,.0f",
        "price_per_sqm": ":$,.0f",
        "remaining_lease_years": ":.1f",
        "latitude": False,
        "longitude": False
    }

    if 'nearest_mrt' in plot_df.columns:
        hover_dict['nearest_mrt'] = True
    if 'min_mrt_dist_km' in plot_df.columns:
        hover_dict['min_mrt_dist_km'] = ":.2f"
    if 'nearest_mrt_exit' in plot_df.columns:
        hover_dict['nearest_mrt_exit'] = True
    if 'nearest_school' in plot_df.columns:
        hover_dict['nearest_school'] = True
    if 'nearest_distance_to_school_m' in plot_df.columns:
        hover_dict['nearest_distance_to_school_m'] = ":.0f"

    map_fn = getattr(px, 'scatter_map', getattr(px, 'scatter_mapbox', None))
    style_param = 'map_style' if hasattr(px, 'scatter_map') else 'mapbox_style'
    
    fig = map_fn(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="price_per_sqm",
        size="floor_area_sqm",
        hover_name=hover_addr,
        hover_data=hover_dict,
        color_continuous_scale=px.colors.sequential.Viridis,
        range_color=[3000, 10000],
        zoom=10.5,
        center={"lat": 1.3521, "lon": 103.8198},
        **{style_param: "carto-darkmatter"}
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        margin=dict(l=20, r=20, t=20, b=20)  # Map uses full container width
    )
    return fig


def create_mrt_proximity_scatter(df):
    """
    Tab 2: Proximity to MRT vs Valuation.
    Enhanced to show School proximity and MRT Exit data in hover tooltips.
    """
    plot_df = df.dropna(subset=['min_mrt_dist_km', 'price_per_sqm']).copy()
    if len(plot_df) > 2500:
        plot_df = plot_df.sample(2500, random_state=42)

    hover_addr = 'address' if 'address' in plot_df.columns else 'full_address'

    hover_dict = {
        'town': True,
        'nearest_mrt': True,
        'resale_price': ':$,.0f',
        'min_mrt_dist_km': ':.2f',
        'price_per_sqm': ':$,.0f'
    }
    
    if 'nearest_school' in plot_df.columns:
        hover_dict['nearest_school'] = True
    if 'nearest_distance_to_school_m' in plot_df.columns:
        hover_dict['nearest_distance_to_school_m'] = ':.0f'

    fig = px.scatter(
        plot_df,
        x='min_mrt_dist_km',
        y='price_per_sqm',
        color='remaining_lease_years',
        size='floor_area_sqm',
        hover_name=hover_addr,
        hover_data=hover_dict,
        labels={
            'min_mrt_dist_km': 'Distance to Nearest MRT (km)',
            'price_per_sqm': 'Price / Sqm (SGD)',
            'remaining_lease_years': 'Lease (Years)'
        },
        trendline="ols",
        trendline_color_override="#ef4444",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.add_vline(
        x=0.5, 
        line_width=2, 
        line_dash="dash", 
        line_color="#f59e0b",
        annotation_text="500m Walkable Zone", 
        annotation_position="top right"
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        margin=STANDARD_MARGINS
    )
    return fig


def create_school_proximity_scatter(df):
    """
    Tab 2 (Secondary Chart): School Distance vs Resale Valuation.
    Visualizes price decay relative to primary/secondary school proximity.
    """
    if 'nearest_distance_to_school_m' not in df.columns:
        return None

    plot_df = df.dropna(subset=['nearest_distance_to_school_m', 'price_per_sqm']).copy()
    if len(plot_df) > 2500:
        plot_df = plot_df.sample(2500, random_state=42)

    hover_addr = 'address' if 'address' in plot_df.columns else 'full_address'

    fig = px.scatter(
        plot_df,
        x='nearest_distance_to_school_m',
        y='price_per_sqm',
        color='remaining_lease_years',
        size='floor_area_sqm',
        hover_name=hover_addr,
        hover_data={
            'town': True,
            'nearest_school': True,
            'resale_price': ':$,.0f',
            'nearest_distance_to_school_m': ':.0f',
            'price_per_sqm': ':$,.0f'
        },
        labels={
            'nearest_distance_to_school_m': 'Distance to School (Meters)',
            'price_per_sqm': 'Price / Sqm (SGD)',
            'remaining_lease_years': 'Lease (Years)'
        },
        trendline="ols",
        trendline_color_override="#ef4444",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.add_vline(
        x=1000, 
        line_width=2, 
        line_dash="dash", 
        line_color="#3b82f6",
        annotation_text="1km School Zone", 
        annotation_position="top right"
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        margin=STANDARD_MARGINS
    )
    return fig


def create_parallel_coordinates(df):
    """
    Tab 3: Parallel Coordinates Trade-off Explorer.
    Dynamically includes School Distance (m) as an additional dimension if available.
    """
    base_cols = ['remaining_lease_years', 'floor_area_sqm', 'min_mrt_dist_km']
    
    # Check optional enriched columns
    if 'nearest_distance_to_school_m' in df.columns:
        base_cols.append('nearest_distance_to_school_m')
    if 'cbd_dist_km' in df.columns:
        base_cols.append('cbd_dist_km')
        
    base_cols.append('resale_price')
    
    cols_needed = [col for col in base_cols if col in df.columns]
    plot_df = df.dropna(subset=cols_needed).copy()
    if len(plot_df) > 800:
        plot_df = plot_df.sample(800, random_state=42)

    labels_map = {
        'remaining_lease_years': 'Remaining Lease (Yrs)',
        'floor_area_sqm': 'Floor Area (Sqm)',
        'min_mrt_dist_km': 'MRT Dist (km)',
        'nearest_distance_to_school_m': 'School Dist (m)',
        'cbd_dist_km': 'CBD Dist (km)',
        'resale_price': 'Price ($)'
    }

    fig = px.parallel_coordinates(
        plot_df,
        dimensions=cols_needed,
        color='resale_price',
        color_continuous_scale=px.colors.diverging.Tealrose,
        labels=labels_map
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        margin=dict(l=100, r=60, t=50, b=40),  # Extra top/left padding for axis labels
        font=dict(size=12)
    )
    return fig


def create_town_depreciation_boxplot(df):
    """
    Tab 4: Town-Level Annual Depreciation Spread.
    """
    town_order = (
        df.groupby('town')['depreciation_per_year']
        .median()
        .sort_values()
        .index.tolist()
    )
    
    fig = px.box(
        df,
        x='town',
        y='depreciation_per_year',
        color='town',
        category_orders={'town': town_order},
        hover_data=['flat_type', 'remaining_lease_years', 'resale_price'],
        labels={'town': 'HDB Town', 'depreciation_per_year': 'Annual Depreciation (SGD)'}
    )
    
    national_median = df['depreciation_per_year'].median()
    fig.add_hline(
        y=national_median,
        line_width=2,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"National Median: ${national_median:,.0f}/yr",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_tickangle=-45,
        showlegend=False,
        height=CHART_HEIGHT,
        margin=dict(l=60, r=40, t=30, b=100)  # Extra bottom margin for angled labels
    )
    return fig


def create_macro_benchmark_chart(df):
    """
    Tab 5: Dual-Axis Macro Economic Comparison.
    """
    monthly_hdb = (
        df.groupby('transaction_date')
        .agg(
            median_price_sqm=('price_per_sqm', 'median'),
            volume=('resale_price', 'count')
        )
        .reset_index()
    )
    
    def estimate_sora(date):
        yr = date.year
        if yr <= 2021:
            return 0.25 + (date.month * 0.02)
        elif yr == 2022:
            return 1.1 + (date.month * 0.18)
        elif yr == 2023:
            return 3.2 + (date.month * 0.05)
        else:
            return 3.5 - (date.month * 0.03)

    monthly_hdb['sora_rate'] = monthly_hdb['transaction_date'].apply(estimate_sora)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=monthly_hdb['transaction_date'],
            y=monthly_hdb['median_price_sqm'],
            name="HDB Resale Median ($/Sqm)",
            line=dict(color="#3b82f6", width=3)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_hdb['transaction_date'],
            y=monthly_hdb['sora_rate'],
            name="3-Month SORA Rate (%)",
            line=dict(color="#ef4444", width=2, dash="dash")
        ),
        secondary_y=True
    )

    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        margin=STANDARD_MARGINS,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text="Transaction Date")
    fig.update_yaxes(title_text="HDB Median Price / Sqm (SGD)", secondary_y=False)
    fig.update_yaxes(title_text="Macro SORA Rate (%)", secondary_y=True)

    return fig
