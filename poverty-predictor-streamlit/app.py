"""
Household Poverty Status Predictor - Streamlit Application
TDHS 2022 Analysis for Tanzania
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io

# Import custom modules
from models.predictor import predict_poverty
from utils.i18n import get_text, get_regions, get_districts
from utils.recommendations import get_recommendations
from utils.storage import storage

# Page configuration with custom theme
st.set_page_config(
    page_title="Poverty Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-green: #10b981;
        --dark-green: #059669;
        --light-green: #d1fae5;
        --slate-dark: #1f2937;
        --slate-light: #f3f4f6;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    /* Dashboard tab green theme */
    .dashboard-tab {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-left: 4px solid #10b981;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Form sections */
    .form-section {
        background: #f9fafb;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }
    
    /* Toggle switch styling */
    .toggle-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #10b981 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #059669 !important;
    }
    
    /* Results section */
    .results-section {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

if 'form_data' not in st.session_state:
    st.session_state.form_data = {}


def t(key: str) -> str:
    """Shortcut for translation"""
    return get_text(key, st.session_state.language)


def create_gauge_chart(probability: float, classification: str) -> go.Figure:
    """Create gauge meter for poverty probability"""
    
    color = '#ef4444' if classification == 'poor' else '#10b981'
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        title={'text': t('poverty_probability')},
        delta={'reference': 50, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 25], 'color': '#dbeafe'},
                {'range': [25, 50], 'color': '#bfdbfe'},
                {'range': [50, 75], 'color': '#fbbf24'},
                {'range': [75, 100], 'color': '#fca5a5'},
            ],
            'threshold': {
                'line': {'color': '#ef4444', 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    )])
    
    fig.update_layout(height=400, font=dict(size=12))
    return fig


def sidebar_settings():
    """Sidebar settings"""
    st.sidebar.title(t('settings_title'))
    st.sidebar.divider()
    
    # Language selector
    language_options = {'English': 'en', 'Swahili': 'sw'}
    selected_lang = st.sidebar.selectbox(
        t('language'),
        options=list(language_options.keys()),
        index=0 if st.session_state.language == 'en' else 1,
    )
    st.session_state.language = language_options[selected_lang]
    
    # Theme selector
    theme_options = {t('theme_light'): 'light', t('theme_dark'): 'dark'}
    selected_theme = st.sidebar.selectbox(
        t('theme'),
        options=list(theme_options.keys()),
        index=0 if st.session_state.theme == 'light' else 1,
    )
    st.session_state.theme = theme_options[selected_theme]
    
    st.sidebar.divider()
    st.sidebar.caption("v1.0.0 | TDHS 2022")


def toggle_switch(label: str, default: bool = False, key: str = None) -> bool:
    """Custom toggle switch component - simple checkbox"""
    if key is None:
        key = label
    
    # Simple checkbox without nested columns
    return st.checkbox(label, value=default, key=key)


def prediction_form():
    """Prediction form with TDHS 2022 fields"""
    
    st.header("📋 " + t('form_title'))
    st.write(t('form_description'))
    st.divider()
    
    # Region and District selection
    st.subheader("📍 Location Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        regions = get_regions(st.session_state.language)
        selected_region = st.selectbox(
            t('region'),
            options=regions,
            help=t('region_help'),
        )
    
    with col2:
        districts = get_districts(selected_region, st.session_state.language)
        selected_district = st.selectbox(
            t('district'),
            options=districts,
            help=t('district_help'),
        )
    
    st.divider()
    
    # Household characteristics
    st.subheader("👨‍👩‍👧‍👦 Household Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Household size - NUMBER INPUT (not slider)
        household_size = st.number_input(
            t('household_size'),
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help=t('household_size_help'),
        )
    
    with col2:
        # Residence type
        residence = st.radio(
            t('residence_type'),
            options=[t('residence_urban'), t('residence_rural')],
            horizontal=True,
        )
        residence_value = 1 if residence == t('residence_urban') else 0
    
    with col3:
        st.write("")  # Spacer
    
    st.divider()
    
    # Water and Sanitation
    st.subheader("💧 Water & Sanitation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        water_options = {
            t('water_piped'): 1,
            t('water_public'): 0,
            t('water_well'): 0,
            t('water_surface'): 0,
            t('water_other'): 0,
        }
        water_source = st.selectbox(
            t('water_source'),
            options=list(water_options.keys()),
        )
        water_value = water_options[water_source]
    
    with col2:
        toilet_options = {
            t('toilet_flush'): 1,
            t('toilet_pit'): 0,
            t('toilet_bucket'): 0,
            t('toilet_none'): 0,
            t('toilet_other'): 0,
        }
        toilet_type = st.selectbox(
            t('toilet_type'),
            options=list(toilet_options.keys()),
        )
        toilet_value = toilet_options[toilet_type]
    
    st.divider()
    
    # Asset ownership with TOGGLE SWITCHES
    st.subheader("🏠 " + t('assets_title'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        has_electricity = toggle_switch(t('electricity'), False, 'electricity')
        has_mobile = toggle_switch(t('mobile_phone'), True, 'mobile')
    
    with col2:
        has_radio = toggle_switch(t('radio'), False, 'radio')
        has_tv = toggle_switch(t('television'), False, 'tv')
    
    with col3:
        has_fridge = toggle_switch(t('refrigerator'), False, 'fridge')
        has_bicycle = toggle_switch(t('bicycle'), False, 'bicycle')
    
    with col4:
        has_motorcycle = toggle_switch(t('motorcycle'), False, 'motorcycle')
        has_car = toggle_switch(t('car'), False, 'car')
    
    st.divider()
    
    # Predict button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(t('predict_button'), use_container_width=True, type="primary"):
            # Store form data
            st.session_state.form_data = {
                'region': selected_region,
                'district': selected_district,
                'householdSize': int(household_size),
                'residence': residence_value,
                'waterSource': water_value,
                'toiletType': toilet_value,
                'hasElectricity': has_electricity,
                'hasMobilePhone': has_mobile,
                'hasRadio': has_radio,
                'hasTelevision': has_tv,
                'hasRefrigerator': has_fridge,
                'hasBicycle': has_bicycle,
                'hasMotorcycle': has_motorcycle,
                'hasCar': has_car,
            }
            
            # Make prediction
            result = predict_poverty(
                household_size=int(household_size),
                residence=residence_value,
                water_source=water_value,
                toilet_type=toilet_value,
                has_electricity=has_electricity,
                has_mobile_phone=has_mobile,
                has_radio=has_radio,
                has_television=has_tv,
                has_refrigerator=has_fridge,
                has_bicycle=has_bicycle,
                has_motorcycle=has_motorcycle,
                has_car=has_car,
            )
            
            st.session_state.prediction_result = result
            
            # Save to storage
            storage.save_prediction(st.session_state.form_data, result)
            
            st.success(t('prediction_success'))
    
    with col2:
        if st.button(t('clear_form'), use_container_width=True):
            st.session_state.prediction_result = None
            st.rerun()


def display_results():
    """Display prediction results"""
    
    if st.session_state.prediction_result is None:
        st.info(t('no_prediction_help'))
        return
    
    result = st.session_state.prediction_result
    
    st.header("📊 " + t('results_title'))
    
    # Gauge chart and classification
    col1, col2 = st.columns([2, 1])
    
    with col1:
        gauge = create_gauge_chart(
            result['probability'],
            result['classification'],
        )
        st.plotly_chart(gauge, use_container_width=True)
    
    with col2:
        # Classification badge with color
        classification_emoji = '🔴' if result['classification'] == 'poor' else '🟢'
        classification_text = t('poor') if result['classification'] == 'poor' else t('non_poor')
        
        st.metric(
            t('classification'),
            f"{classification_emoji} {classification_text}"
        )
        
        st.metric(
            t('score'),
            result['score']
        )
    
    st.divider()
    
    # Feature importance
    st.subheader("📈 " + t('feature_importance'))
    
    importance_df = pd.DataFrame(result['featureImportance'])
    importance_df = importance_df[['label', 'contribution']].rename(
        columns={'label': t('factor'), 'contribution': t('contribution')}
    )
    
    fig = px.bar(
        importance_df,
        x=t('contribution'),
        y=t('factor'),
        orientation='h',
        color=t('contribution'),
        color_continuous_scale=['#d1fae5', '#10b981'],
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    st.subheader("💡 " + t('recommendations_title'))
    
    recommendations = get_recommendations(
        result['classification'],
        st.session_state.form_data,
    )
    
    st.write(f"**{recommendations['summary']}**")
    
    # Group recommendations by priority
    for priority in ['high', 'medium', 'low']:
        priority_recs = [r for r in recommendations['recommendations'] if r['priority'] == priority]
        
        if priority_recs:
            priority_label = t(f'priority_{priority}')
            st.write(f"### {priority_label}")
            
            for rec in priority_recs:
                with st.expander(f"{rec['category']} - {rec['title']}"):
                    st.write(f"**Description:** {rec['description']}")
                    st.write(f"**Action:** {rec['action']}")
                    st.write(f"**Impact:** {rec['impact']}")


def research_dashboard():
    """Research dashboard with analytics"""
    
    # Green theme header
    st.markdown('<div class="dashboard-tab"><h1>📊 ' + t('dashboard_title') + '</h1></div>', unsafe_allow_html=True)
    st.write(t('dashboard_description'))
    
    # Get all predictions
    all_predictions = storage.get_all_predictions()
    
    if len(all_predictions) == 0:
        st.info("No predictions yet. Go to the Predictor tab to make predictions.")
        return
    
    # Statistics
    stats = storage.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(t('total_predictions'), stats['total'], delta=None)
    
    with col2:
        st.metric(t('poor_count'), stats['poor'])
    
    with col3:
        st.metric(t('non_poor_count'), stats['non_poor'])
    
    with col4:
        st.metric(t('poor_percentage'), f"{stats['poor_percentage']}%")
    
    st.divider()
    
    # Filters
    st.subheader("🔍 " + t('filters_title'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        regions = [t('filter_all')] + get_regions(st.session_state.language)
        region_filter = st.selectbox(
            t('filter_region'),
            options=regions,
        )
    
    with col2:
        if region_filter != t('filter_all'):
            districts = get_districts(region_filter, st.session_state.language)
            district_filter = st.selectbox(
                t('filter_district'),
                options=[t('filter_all')] + districts,
            )
        else:
            district_filter = t('filter_all')
    
    with col3:
        residence_filter = st.selectbox(
            t('filter_residence'),
            options=[t('filter_all'), t('residence_urban'), t('residence_rural')],
        )
    
    with col4:
        poverty_filter = st.selectbox(
            t('filter_poverty_level'),
            options=[t('filter_all'), t('poor'), t('non_poor')],
        )
    
    # Apply filters
    filtered_df = all_predictions.copy()
    
    if region_filter != t('filter_all'):
        filtered_df = filtered_df[filtered_df['region'] == region_filter]
    
    if district_filter != t('filter_all'):
        filtered_df = filtered_df[filtered_df['district'] == district_filter]
    
    if residence_filter != t('filter_all'):
        residence_val = 1 if residence_filter == t('residence_urban') else 0
        filtered_df = filtered_df[filtered_df['residence'] == residence_val]
    
    if poverty_filter != t('filter_all'):
        poverty_val = 'poor' if poverty_filter == t('poor') else 'non-poor'
        filtered_df = filtered_df[filtered_df['classification'] == poverty_val]
    
    st.divider()
    
    # Analytics charts
    st.subheader("📈 " + t('analytics_title'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Poverty distribution pie chart
        dist_data = filtered_df['classification'].value_counts()
        fig_dist = px.pie(
            values=dist_data.values,
            names=[t('poor') if x == 'poor' else t('non_poor') for x in dist_data.index],
            title=t('poverty_distribution'),
            color_discrete_sequence=['#ef4444', '#10b981'],
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Predictions by region
        region_data = filtered_df['region'].value_counts()
        fig_region = px.bar(
            x=region_data.index,
            y=region_data.values,
            title=t('predictions_by_region'),
            labels={'x': t('filter_region'), 'y': 'Count'},
            color=region_data.values,
            color_continuous_scale=['#d1fae5', '#10b981'],
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    st.divider()
    
    # Predictions table
    st.subheader("📋 " + t('predictions_table'))
    
    display_df = filtered_df[[
        'timestamp', 'region', 'district', 'household_size', 'residence', 'classification', 'probability'
    ]].copy()
    
    display_df['residence'] = display_df['residence'].map({
        1: t('residence_urban'),
        0: t('residence_rural'),
    })
    
    display_df['classification'] = display_df['classification'].map({
        'poor': t('poor'),
        'non-poor': t('non_poor'),
    })
    
    display_df.columns = [
        t('date'),
        t('region_col'),
        t('district_col'),
        t('household_size_col'),
        t('residence_col'),
        t('poverty_level'),
        t('probability_col'),
    ]
    
    st.dataframe(display_df, use_container_width=True)
    
    # Export button
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label=t('export_csv'),
        data=csv_data,
        file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def main():
    """Main application"""
    
    # Header
    st.title("🏠 " + t('app_title'))
    st.caption(t('app_subtitle'))
    
    # Sidebar settings
    sidebar_settings()
    
    # Tabs
    tab1, tab2 = st.tabs([t('tab_predictor'), t('tab_dashboard')])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            prediction_form()
        
        with col2:
            display_results()
    
    with tab2:
        research_dashboard()
    
    # Footer
    st.divider()
    st.caption(t('footer_text'))
    st.caption(t('footer_model'))


if __name__ == '__main__':
    main()
