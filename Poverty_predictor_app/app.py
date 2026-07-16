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
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Data/graph-motif background (inline SVG, no external image needed) -----
_BG_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='420' height='420'>
  <rect width='420' height='420' fill='none'/>
  <g stroke='%23ffffff' stroke-opacity='0.05' stroke-width='1'>
    <line x1='0' y1='60' x2='420' y2='60'/>
    <line x1='0' y1='150' x2='420' y2='150'/>
    <line x1='0' y1='240' x2='420' y2='240'/>
    <line x1='0' y1='330' x2='420' y2='330'/>
  </g>
  <g fill='%236366f1' fill-opacity='0.10'>
    <rect x='30' y='260' width='24' height='120'/>
    <rect x='66' y='210' width='24' height='170'/>
    <rect x='102' y='290' width='24' height='90'/>
    <rect x='138' y='150' width='24' height='230'/>
  </g>
  <polyline points='30,150 90,110 150,170 210,90 270,130 330,60 390,100' fill='none' stroke='%2334d399' stroke-opacity='0.18' stroke-width='3'/>
  <circle cx='330' cy='60' r='4' fill='%2334d399' fill-opacity='0.4'/>
  <circle cx='210' cy='90' r='4' fill='%2334d399' fill-opacity='0.4'/>
</svg>
"""
_BG_SVG_URI = "data:image/svg+xml;utf8," + _BG_SVG.replace("\n", "").replace("#", "%23")

# Custom CSS for the dashboard-style theme
st.markdown(f"""
<style>
    :root {{
        --primary-indigo: #6366f1;
        --deep-indigo: #312e81;
        --night-blue: #0c0a24;
        --panel-blue: #1b1745;
        --accent-teal: #34d399;
        --accent-red: #f87171;
        --text-light: #f5f4ff;
    }}

    /* Data/graph motif behind the whole app */
    @keyframes moveBackground {{
        from {{ background-position: 0 0, 0 0; }}
        to {{ background-position: -420px 0, 0 0; }}
    }}

    .stApp {{
        background-image: url("{_BG_SVG_URI}"), linear-gradient(160deg, #e0f2fe 0%, #bae6fd 55%, #7dd3fc 100%);
        background-size: 420px 420px, cover;
        background-attachment: fixed;
        animation: moveBackground 20s linear infinite;
    }}

    /* Animated Title */
    @keyframes blinkScale {{
        0%, 100% {{ opacity: 1; transform: scale(0.8); }}
        50% {{ opacity: 0.5; transform: scale(1.2); }}
    }}
    
    .animated-title {{
        font-size: 48px !important;
        font-weight: 900 !important;
        text-align: center;
        color: #1e40af !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: blinkScale 3s ease-in-out infinite;
        margin-bottom: 30px;
    }}

    /* Bold, shadowed text everywhere visible in the app */
    h1, h2, h3, h4, h5, p, label, span, .stMarkdown, .stMetric label,
    .stRadio label, .stSelectbox label, .stNumberInput label, .stCheckbox label {{
        font-weight: 700 !important;
        color: #1e3a8a !important; /* Dark blue for visibility on light blue bg */
        text-shadow: 0 1px 2px rgba(255,255,255,0.8);
    }}

    /* Section headers as solid "bars" instead of loose floating text */
    .section-bar {{
        background: linear-gradient(90deg, var(--primary-indigo) 0%, var(--deep-indigo) 100%);
        color: var(--text-light);
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-shadow: 0 2px 6px rgba(0,0,0,0.5);
        padding: 14px 20px;
        border-radius: 10px;
        margin: 22px 0 16px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }}
    .section-bar.hero {{
        font-size: 24px;
        padding: 18px 24px;
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {{
        font-size: 16px;
        font-weight: 700 !important;
        padding: 12px 24px;
    }}

    /* Phone-card style panels (mirrors the reference dashboard look) */
    .app-card {{
        background: linear-gradient(160deg, #2c2870 0%, #201c56 100%);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.08);
    }}

    /* Metric cards */
    .metric-card {{
        background: linear-gradient(160deg, #2c2870 0%, #201c56 100%);
        border-left: 4px solid var(--primary-indigo);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    }}

    /* Progress steps for the multi-step form */
    .step-track {{
        display: flex;
        gap: 8px;
        margin-bottom: 18px;
    }}
    .step-pill {{
        flex: 1;
        text-align: center;
        padding: 10px 6px;
        border-radius: 20px;
        font-size: 12.5px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
        background: rgba(255,255,255,0.06);
        color: #a5b4fc;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    .step-pill.active {{
        background: linear-gradient(90deg, var(--primary-indigo), #818cf8);
        color: white;
    }}
    .step-pill.done {{
        background: rgba(52,211,153,0.18);
        color: var(--accent-teal);
        border-color: rgba(52,211,153,0.4);
    }}

    /* Button styling */
    .stButton > button {{
        background: linear-gradient(90deg, var(--primary-indigo), #818cf8) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        border: none !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.35);
    }}
    .stButton > button:hover {{
        filter: brightness(1.1);
    }}

    /* Results section */
    .results-section {{
        background: linear-gradient(160deg, #1c2f4a 0%, #14261f 100%);
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(52,211,153,0.35);
    }}

    /* Success + view-results callout */
    .success-callout {{
        background: linear-gradient(90deg, rgba(52,211,153,0.16), rgba(52,211,153,0.05));
        border: 1px solid rgba(52,211,153,0.4);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0;
        color: var(--accent-teal);
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }}
</style>
""", unsafe_allow_html=True)


def section_bar(text: str, hero: bool = False):
    """Render a section title inside a solid bar instead of loose text."""
    if hero:
        st.markdown(f'<div class="animated-title">{text}</div>', unsafe_allow_html=True)
    else:
        cls = "section-bar"
        st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

if 'form_step' not in st.session_state:
    st.session_state.form_step = 0

if 'show_results' not in st.session_state:
    st.session_state.show_results = False


def t(key: str) -> str:
    """Shortcut for translation"""
    return get_text(key, st.session_state.language)


def create_gauge_chart(probability: float, classification: str) -> go.Figure:
    """Create gauge meter for poverty probability"""
    
    color = '#f87171' if classification == 'poor' else '#34d399'
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        title={'text': t('poverty_probability'), 'font': {'color': '#f5f4ff'}},
        number={'font': {'color': '#f5f4ff'}},
        delta={'reference': 50, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#f5f4ff'},
            'bar': {'color': color},
            'bgcolor': 'rgba(0,0,0,0)',
            'steps': [
                {'range': [0, 25], 'color': '#312e81'},
                {'range': [25, 50], 'color': '#4c46b6'},
                {'range': [50, 75], 'color': '#7c3f6a'},
                {'range': [75, 100], 'color': '#8a3b3b'},
            ],
            'threshold': {
                'line': {'color': '#f87171', 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    )])
    
    fig.update_layout(
        height=400, font=dict(size=12, color='#f5f4ff'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    )
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


def _init_draft():
    """A plain (non-widget) session_state dict that survives across wizard
    steps. Widget-bound session_state keys are cleared once a widget stops
    being rendered on a given run, so every widget's value gets copied here
    immediately after it renders."""
    if 'draft' not in st.session_state:
        st.session_state.draft = {
            'region': None, 'district': None,
            'household_size': 5, 'residence': 1,
            'water': 1, 'toilet': 1,
            'electricity': False, 'mobile': True, 'radio': False, 'tv': False,
            'fridge': False, 'bicycle': False, 'motorcycle': False, 'car': False,
        }


def toggle_switch(label: str, draft_key: str, default: bool = False) -> bool:
    """Custom toggle switch component - checkbox backed by the draft dict."""
    current = st.session_state.draft.get(draft_key, default)
    val = st.checkbox(label, value=current, key=f'w_{draft_key}')
    st.session_state.draft[draft_key] = val
    return val


STEP_KEYS = ['step_location', 'step_household', 'step_water', 'step_assets']


def _render_step_track():
    """Progress bar of pill-shaped steps for the wizard."""
    labels = [t(k) for k in STEP_KEYS]
    current = st.session_state.form_step
    pills = ""
    for i, label in enumerate(labels):
        cls = "step-pill"
        if i == current:
            cls += " active"
        elif i < current:
            cls += " done"
        pills += f'<div class="{cls}">{i + 1}. {label}</div>'
    st.markdown(f'<div class="step-track">{pills}</div>', unsafe_allow_html=True)


def prediction_form():
    """Prediction form with TDHS 2022 fields, shown page-by-page (wizard)."""

    _init_draft()
    draft = st.session_state.draft

    section_bar(t('form_title'), hero=True)
    st.write(t('form_description'))
    _render_step_track()

    step = st.session_state.form_step

    water_options = {
        t('water_piped'): 1, t('water_public'): 0, t('water_well'): 0,
        t('water_surface'): 0, t('water_other'): 0,
    }
    toilet_options = {
        t('toilet_flush'): 1, t('toilet_pit'): 0, t('toilet_bucket'): 0,
        t('toilet_none'): 0, t('toilet_other'): 0,
    }

    # ---------------- Step 0: Location ----------------
    if step == 0:
        section_bar(t('step_location'))
        col1, col2 = st.columns(2)
        
        # Get regions
        regions = get_regions(st.session_state.language)
        
        with col1:
            # Region selection
            region_val = st.selectbox(
                t('region'), 
                options=regions, 
                index=regions.index(draft['region']) if draft['region'] in regions else 0,
                help=t('region_help'),
                key='region_selector'
            )
            
            # If region changed, update draft and reset district
            if region_val != draft['region']:
                draft['region'] = region_val
                # Reset district to the first one in the new region
                new_districts = get_districts(region_val, st.session_state.language)
                draft['district'] = new_districts[0] if new_districts else None
                st.rerun()

        with col2:
            # Get districts for the selected region
            districts = get_districts(draft['region'], st.session_state.language)
            
            # District selection
            district_val = st.selectbox(
                t('district'), 
                options=districts, 
                index=districts.index(draft['district']) if draft['district'] in districts else 0,
                help=t('district_help'),
                key='district_selector'
            )
            draft['district'] = district_val

    # ---------------- Step 1: Household details ----------------
    elif step == 1:
        section_bar(t('step_household'))
        col1, col2 = st.columns(2)
        with col1:
            hs = st.number_input(
                t('household_size'), min_value=1, max_value=30,
                value=int(draft['household_size']), step=1,
                help=t('household_size_help'), key='w_household_size',
            )
            draft['household_size'] = int(hs)
        with col2:
            res_options = [t('residence_urban'), t('residence_rural')]
            default_idx = 0 if draft['residence'] == 1 else 1
            residence_choice = st.radio(
                t('residence_type'), options=res_options, index=default_idx,
                horizontal=True, key='w_residence',
            )
            draft['residence'] = 1 if residence_choice == t('residence_urban') else 0

    # ---------------- Step 2: Water & Sanitation ----------------
    elif step == 2:
        section_bar(t('step_water'))
        water_labels = list(water_options.keys())
        toilet_labels = list(toilet_options.keys())
        col1, col2 = st.columns(2)
        with col1:
            water_choice = st.selectbox(t('water_source'), options=water_labels, key='w_water_select')
            draft['water'] = water_options[water_choice]
        with col2:
            toilet_choice = st.selectbox(t('toilet_type'), options=toilet_labels, key='w_toilet_select')
            draft['toilet'] = toilet_options[toilet_choice]

    # ---------------- Step 3: Assets + Predict ----------------
    elif step == 3:
        section_bar(t('assets_title'))
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            toggle_switch(t('electricity'), 'electricity', False)
            toggle_switch(t('mobile_phone'), 'mobile', True)
        with col2:
            toggle_switch(t('radio'), 'radio', False)
            toggle_switch(t('television'), 'tv', False)
        with col3:
            toggle_switch(t('refrigerator'), 'fridge', False)
            toggle_switch(t('bicycle'), 'bicycle', False)
        with col4:
            toggle_switch(t('motorcycle'), 'motorcycle', False)
            toggle_switch(t('car'), 'car', False)

    st.divider()

    # ---------------- Navigation ----------------
    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if step > 0:
            if st.button(t('back_button'), use_container_width=True, key=f'back_{step}'):
                st.session_state.form_step -= 1
                st.rerun()

    with nav3:
        if step < len(STEP_KEYS) - 1:
            if st.button(t('next_button'), use_container_width=True, type="primary", key=f'next_{step}'):
                st.session_state.form_step += 1
                st.rerun()
        else:
            if st.button(t('predict_button'), use_container_width=True, type="primary", key='predict_btn'):
                st.session_state.form_data = {
                    'region': draft['region'],
                    'district': draft['district'],
                    'householdSize': int(draft['household_size']),
                    'residence': draft['residence'],
                    'waterSource': draft['water'],
                    'toiletType': draft['toilet'],
                    'hasElectricity': draft['electricity'],
                    'hasMobilePhone': draft['mobile'],
                    'hasRadio': draft['radio'],
                    'hasTelevision': draft['tv'],
                    'hasRefrigerator': draft['fridge'],
                    'hasBicycle': draft['bicycle'],
                    'hasMotorcycle': draft['motorcycle'],
                    'hasCar': draft['car'],
                }

                result = predict_poverty(
                    household_size=int(draft['household_size']),
                    residence=draft['residence'],
                    water_source=draft['water'],
                    toilet_type=draft['toilet'],
                    has_electricity=draft['electricity'],
                    has_mobile_phone=draft['mobile'],
                    has_radio=draft['radio'],
                    has_television=draft['tv'],
                    has_refrigerator=draft['fridge'],
                    has_bicycle=draft['bicycle'],
                    has_motorcycle=draft['motorcycle'],
                    has_car=draft['car'],
                )

                st.session_state.prediction_result = result
                storage.save_prediction(st.session_state.form_data, result)
                st.session_state.show_results = False  # require explicit click to view
                st.rerun()

    if step == len(STEP_KEYS) - 1:
        if st.button(t('clear_form'), key='clear_form_btn'):
            st.session_state.prediction_result = None
            st.session_state.show_results = False
            st.session_state.form_step = 0
            st.rerun()

    # ---------------- Success + "view results" callout ----------------
    if st.session_state.prediction_result is not None and not st.session_state.show_results:
        st.markdown(f'<div class="success-callout">{t("prediction_success")}</div>', unsafe_allow_html=True)
        if st.button(t('view_results_button'), use_container_width=True, type="primary", key='view_results_btn'):
            st.session_state.show_results = True
            st.rerun()


def display_results():
    """Display prediction results"""
    
    if st.session_state.prediction_result is None:
        st.info(t('no_prediction_help'))
        return
    
    result = st.session_state.prediction_result
    
    section_bar(t('results_title'), hero=True)
    
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        gauge = create_gauge_chart(
            result['probability'],
            result['classification'],
        )
        st.plotly_chart(gauge, use_container_width=True)
    
    with col2:
        classification_text = t('poor') if result['classification'] == 'poor' else t('non_poor')
        
        st.metric(
            t('classification'),
            classification_text
        )
        
        st.metric(
            t('score'),
            result['score']
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature importance
    section_bar(t('feature_importance'))
    
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
        color_continuous_scale=['#4c46b6', '#818cf8'],
    )
    fig.update_layout(
        showlegend=False, height=400,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f5f4ff'),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    section_bar(t('recommendations_title'))
    
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
    
    section_bar(t('dashboard_title'), hero=True)
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
    section_bar(t('filters_title'))
    
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
    section_bar(t('analytics_title'))
    
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
    section_bar(t('predictions_table'))
    
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
    section_bar(t('app_title'), hero=True)
    st.caption(t('app_subtitle'))
    
    # Sidebar settings
    sidebar_settings()
    
    # Tabs
    tab1, tab2 = st.tabs([t('tab_predictor'), t('tab_dashboard')])
    
    with tab1:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        prediction_form()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Results only appear after the user explicitly asks to view them
        if st.session_state.show_results:
            display_results()
    
    with tab2:
        research_dashboard()
    
    # Footer
    st.divider()
    st.caption(t('footer_text'))
    st.caption(t('footer_model'))


if __name__ == '__main__':
    main()
