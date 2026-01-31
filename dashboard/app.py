"""
NETS Business Data Enhancement - Streamlit Dashboard
Interactive visualization and exploration of Minneapolis quick service restaurants and pharmacies
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import altair as alt
import numpy as np
from pathlib import Path
import logging

# Configure page
st.set_page_config(
    page_title="NETS Minneapolis Business Dashboard",
    page_icon="business",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = logging.getLogger(__name__)


@st.cache_data
def load_parquet_data(parquet_path: str) -> pd.DataFrame:
    """Load Parquet database from file"""
    try:
        df = pd.read_parquet(parquet_path)
        st.success(f"Loaded {len(df)} records from {Path(parquet_path).name}")
        return df
    except FileNotFoundError:
        st.error(f"Parquet file not found: {parquet_path}")
        return None
    except Exception as e:
        st.error(f"Error loading Parquet: {e}")
        return None


@st.cache_data
def create_gdf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convert DataFrame to GeoDataFrame"""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None
    
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
        crs='EPSG:4326'
    )
    return gdf


def sidebar_filters(df: pd.DataFrame) -> dict:
    """
    Create sidebar filters
    
    Returns:
        Dictionary of filter values
    """
    st.sidebar.header("Filters")
    
    filters = {}
    
    # NAICS code filter
    if 'naics_code' in df.columns:
        unique_naics = df['naics_code'].dropna().unique()
        filters['naics'] = st.sidebar.multiselect(
            "NAICS Code",
            options=sorted(unique_naics),
            default=sorted(unique_naics)
        )
    
    # Business status filter
    if 'is_active_prob' in df.columns:
        status_options = {
            'All': (0, 1),
            'Likely Active (prob > 0.7)': (0.7, 1),
            'Uncertain (0.3-0.7)': (0.3, 0.7),
            'Likely Inactive (prob < 0.3)': (0, 0.3)
        }
        status_filter = st.sidebar.radio("Business Status", options=status_options.keys())
        filters['status_range'] = status_options[status_filter]
    
    # Employee count range
    if 'employees_optimized' in df.columns:
        min_emp, max_emp = st.sidebar.slider(
            "Employee Count Range",
            min_value=0,
            max_value=int(df['employees_optimized'].max()) + 1,
            value=(0, int(df['employees_optimized'].max()) + 1),
            step=1
        )
        filters['employees_range'] = (min_emp, max_emp)
    
    # Confidence level filter
    if 'employees_confidence' in df.columns:
        confidence_levels = st.sidebar.multiselect(
            "Employee Estimate Confidence",
            options=['high', 'medium', 'low'],
            default=['high', 'medium']
        )
        filters['confidence'] = confidence_levels
    
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply selected filters to DataFrame"""
    filtered_df = df.copy()
    
    if 'naics' in filters and filters['naics']:
        filtered_df = filtered_df[filtered_df['naics_code'].isin(filters['naics'])]
    
    if 'status_range' in filters:
        lower, upper = filters['status_range']
        filtered_df = filtered_df[
            (filtered_df['is_active_prob'] >= lower) &
            (filtered_df['is_active_prob'] <= upper)
        ]
    
    if 'employees_range' in filters:
        min_emp, max_emp = filters['employees_range']
        filtered_df = filtered_df[
            (filtered_df['employees_optimized'] >= min_emp) &
            (filtered_df['employees_optimized'] <= max_emp)
        ]
    
    if 'confidence' in filters and filters['confidence']:
        filtered_df = filtered_df[filtered_df['employees_confidence'].isin(filters['confidence'])]
    
    return filtered_df


def create_employee_distribution_chart(df: pd.DataFrame) -> alt.Chart:
    """Create Altair chart of employee count distribution"""
    if 'employees_optimized' not in df.columns:
        return None
    
    chart = alt.Chart(df).mark_bar(opacity=0.7).encode(
        x=alt.X('employees_optimized:Q', bin=alt.Bin(maxbins=20), title='Employee Count'),
        y='count()',
        color='naics_code:N',
        tooltip=['count()', 'naics_code']
    ).properties(
        width=700,
        height=300,
        title='Distribution of Employee Counts by Industry'
    )
    
    return chart


def create_survival_probability_chart(df: pd.DataFrame) -> alt.Chart:
    """Create Altair chart of business survival probabilities"""
    if 'is_active_prob' not in df.columns:
        return None
    
    # Bin survival probability
    df_binned = df.copy()
    df_binned['survival_bin'] = pd.cut(
        df['is_active_prob'],
        bins=[0, 0.25, 0.5, 0.75, 1.0],
        labels=['Low (0-0.25)', 'Medium-Low (0.25-0.5)', 'Medium-High (0.5-0.75)', 'High (0.75-1.0)']
    )
    
    chart = alt.Chart(df_binned).mark_bar(opacity=0.7).encode(
        x='survival_bin:O',
        y='count()',
        color='naics_code:N',
        tooltip=['count()', 'naics_code']
    ).properties(
        width=700,
        height=300,
        title='Business Survival Probability Distribution'
    ).interactive()
    
    return chart


def create_folium_heatmap(gdf: gpd.GeoDataFrame, metric: str = 'employees_optimized') -> folium.Map:
    """
    Create Folium heatmap of Minneapolis
    
    Args:
        gdf: GeoDataFrame with geometry
        metric: Column to visualize on heatmap
        
    Returns:
        Folium map object
    """
    if metric not in gdf.columns or 'geometry' not in gdf.columns:
        return None
    
    # Center map on Minneapolis
    minneapolis_center = [44.9778, -93.2650]
    m = folium.Map(
        location=minneapolis_center,
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Create heatmap layer
    heat_data = [
        [point.y, point.x, value]
        for point, value in zip(gdf.geometry, gdf[metric])
        if pd.notna(value) and value > 0
    ]
    
    folium.plugins.HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)
    
    # Add marker layer
    for idx, row in gdf.iterrows():
        if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
            popup_text = f"""
            <b>{row.get('company_name', 'Unknown')}</b><br>
            NAICS: {row.get('naics_code', 'N/A')}<br>
            Employees: {row.get('employees_optimized', 'N/A')}<br>
            Survival Prob: {row.get('is_active_prob', 'N/A'):.2f if pd.notna(row.get('is_active_prob')) else 'N/A'}<br>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=folium.Popup(popup_text, max_width=300),
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.7,
                opacity=0.8
            ).add_to(m)
    
    return m


def show_statistics(df: pd.DataFrame):
    """Display summary statistics"""
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Establishments", len(df))
    
    with col2:
        if 'employees_optimized' in df.columns:
            avg_employees = df['employees_optimized'].mean()
            st.metric("Average Employees", f"{avg_employees:.1f}")
    
    with col3:
        if 'is_active_prob' in df.columns:
            likely_active = (df['is_active_prob'] > 0.7).sum()
            st.metric("Likely Active (>0.7)", likely_active)
    
    with col4:
        if 'data_quality_score' in df.columns:
            avg_quality = df['data_quality_score'].mean()
            st.metric("Avg Data Quality", f"{avg_quality:.0f}/100")


def show_data_table(df: pd.DataFrame):
    """Display filtered data table"""
    st.subheader("Establishment Records")
    
    # Select columns to display
    display_cols = [
        'company_name', 'naics_code', 'employees_optimized',
        'employees_ci_lower', 'employees_ci_upper', 'employees_confidence',
        'is_active_prob', 'is_active_confidence', 'data_quality_score'
    ]
    
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Display with pagination
    if len(df) > 100:
        page = st.slider("Page", 1, (len(df) // 100) + 1, 1)
        start = (page - 1) * 100
        end = start + 100
        display_df = df[available_cols].iloc[start:end]
    else:
        display_df = df[available_cols]
    
    st.dataframe(display_df, use_container_width=True)
    
    # Download option
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="nets_filtered_data.csv",
        mime="text/csv"
    )


def show_about():
    """Show about and instructions"""
    with st.expander("About this Dashboard", expanded=False):
        st.markdown("""
        ## NETS Business Data Enhancement System
        
        This dashboard provides an interactive view of the enhanced NETS business database for Minneapolis,
        focusing on Quick Service Restaurants (NAICS 722513) and Pharmacies (NAICS 446110).
        
        ### Key Features:
        - **Employee Estimation**: Multi-signal Bayesian ensemble combining LinkedIn, reviews, building area, and job postings
        - **Survival Detection**: 4-signal scoring for business operational status and closure probability
        - **Confidence Intervals**: 95% confidence bounds on all estimates
        - **Data Quality Scoring**: 0-100 metric based on data completeness, diversity, and estimate confidence
        - **Geographic Visualization**: Heatmaps and interactive maps of Minneapolis
        
        ### How to Use:
        1. **Filter Data**: Use sidebar filters to focus on specific industries, business status, or employee ranges
        2. **Explore Maps**: View geographic distribution of establishments and their attributes
        3. **Analyze Distributions**: See patterns in employee counts and survival probabilities
        4. **Download Results**: Export filtered data as CSV for further analysis
        
        ### Data Sources:
        - NETS establishment database (company name, location, industry)
        - LinkedIn company profiles (employee counts - optional)
        - Business reviews (review velocity, recency)
        - Job postings (hiring intensity - optional)
        - OpenStreetMap (building information - optional)
        """)


def main():
    """Main Streamlit app"""
    st.title("🏢 NETS Minneapolis Business Data Dashboard")
    st.markdown("""
    Enhanced NETS database with AI-driven employee estimation and business survival detection.
    Data for Quick Service Restaurants (NAICS 722513) and Pharmacies (NAICS 446110).
    """)
    
    # Load data
    parquet_path = "data/processed/nets_ai_minneapolis.parquet"
    
    df = load_parquet_data(parquet_path)
    if df is None or df.empty:
        st.error("Unable to load data. Please check parquet file path.")
        return
    
    # Apply filters
    filters = sidebar_filters(df)
    filtered_df = apply_filters(df, filters)
    
    st.info(f"Showing {len(filtered_df)} of {len(df)} establishments")
    
    # Statistics
    show_statistics(filtered_df)
    
    # Show about/instructions
    show_about()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Maps",
        "Employee Distribution",
        "Survival Status",
        "Data Quality",
        "Details"
    ])
    
    with tab1:
        st.subheader("Geographic Distribution")
        gdf = create_gdf(filtered_df)
        if gdf is not None:
            # Employee count heatmap
            st.markdown("**Employee Count Heatmap**")
            m_employees = create_folium_heatmap(gdf, 'employees_optimized')
            if m_employees:
                st_folium(m_employees, width=1000, height=600)
            
            # Survival probability heatmap
            if 'is_active_prob' in filtered_df.columns:
                st.markdown("**Business Survival Probability Heatmap**")
                m_survival = create_folium_heatmap(gdf, 'is_active_prob')
                if m_survival:
                    st_folium(m_survival, width=1000, height=600)
    
    with tab2:
        st.subheader("Employee Count Analysis")
        chart = create_employee_distribution_chart(filtered_df)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        
        # Confidence interval visualization
        if 'employees_optimized' in filtered_df.columns and 'employees_ci_upper' in filtered_df.columns:
            st.markdown("**Confidence Interval Examples**")
            ci_sample = filtered_df[[
                'company_name', 'employees_optimized',
                'employees_ci_lower', 'employees_ci_upper'
            ]].head(20)
            st.dataframe(ci_sample, use_container_width=True)
    
    with tab3:
        st.subheader("Business Survival Analysis")
        chart = create_survival_probability_chart(filtered_df)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        
        # Status breakdown
        if 'is_active_prob' in filtered_df.columns:
            status_counts = pd.cut(
                filtered_df['is_active_prob'],
                bins=[0, 0.3, 0.7, 1.0],
                labels=['Likely Inactive', 'Uncertain', 'Likely Active']
            ).value_counts()
            
            st.bar_chart(status_counts)
    
    with tab4:
        st.subheader("Data Quality Metrics")
        if 'data_quality_score' in filtered_df.columns:
            quality_histogram = alt.Chart(filtered_df).mark_histogram(bins=20).encode(
                x='data_quality_score:Q',
                y='count()',
                color=alt.value('steelblue')
            ).properties(width=700, height=400, title='Data Quality Score Distribution')
            
            st.altair_chart(quality_histogram, use_container_width=True)
        
        # Quality indicators
        if 'employees_confidence' in filtered_df.columns:
            confidence_dist = filtered_df['employees_confidence'].value_counts()
            st.markdown("**Employee Estimate Confidence**")
            st.bar_chart(confidence_dist)
    
    with tab5:
        st.subheader("Detailed Establishment Data")
        show_data_table(filtered_df)


if __name__ == "__main__":
    main()
