import plotly.express as px
import streamlit as st
import pandas as pd
from pathlib import Path

# Configure the Streamlit page

st.set_page_config(
    page_title="NZ Road Crash Severity Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Apply the dark dashboard theme
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: white;
    }
    h1, h2, h3 {
        color: white !important;
    }
    /* Keep the Streamlit header dark */
      [data-testid="stHeader"] {
    background-color: #000000 !important;
}
/* Match the top decoration to the page background */
[data-testid="stDecoration"] {
    background: #000000 !important;
}
    p, label {
        color: white !important;
    }
    [data-testid="stMetricLabel"] {
        color: #CFCFCF !important;
    }
    [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stCaptionContainer"] {
        color: #AAAAAA !important;
    }
    [data-baseweb="tab-list"] {
        gap: 12px;
    }
    [data-baseweb="tab"] {
        font-size: 16px;
    }
    section[data-testid="stSidebar"] {
        background-color: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the combined crash dataset
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data/combined_context/CAS_National_Context_enriched.csv"

@st.cache_data
def load_data(path):
    return pd.read_csv(path)
if not DATA_PATH.exists():
    st.error(
        "Dataset not found. Check that this file exists:\n\n"
        "data/combined_context/CAS_National_Context_enriched.csv"
    )
    st.stop()
df = load_data(DATA_PATH)

# Prepare fields used in the dashboard

# Clean region labels

df["_region"] = (
    df["region"]
    .fillna("Unknown")
    .astype(str)
)

# Store crash year as a numeric field
df["_year"] = pd.to_numeric(
    df["crashYear"],
    errors="coerce"
).astype("Int64")

# Create readable speed-limit labels

df["Speed Limit Group"] = df["speedLimit"].apply(
    lambda x: str(int(x))
    if pd.notna(x)
    else "Unknown"
)

# Group junction distance into readable bands

distance_order = [
    "0–50 m",
    "50–100 m",
    "100–250 m",
    "250–500 m",
    "500–1000 m",
    "1000+ m"
]

df["Distance Group"] = pd.cut(
    df["dist_to_junction_m"],
    bins=[
        0,
        50,
        100,
        250,
        500,
        1000,
        float("inf")
    ],
    labels=distance_order,
    include_lowest=True
)

# Define NZDep quintiles once from the full dataset so the
# group boundaries stay consistent when filters change.

nzdep_order = [
    "Q1 – Lowest Score",
    "Q2",
    "Q3",
    "Q4",
    "Q5 – Highest Score"
]

df["NZDep Group"] = pd.qcut(
    df["NZDep2023_Score"],
    q=5,
    labels=nzdep_order
)

df["NZDep Group"] = (
    df["NZDep Group"]
    .astype(object)
    .fillna("Unknown")
)

# Group elevation into bands for comparison

elevation_order = [
    "<50 m",
    "50–100 m",
    "100–200 m",
    "200–500 m",
    "500+ m",
    "Unknown"
]

df["Elevation Group"] = pd.cut(
    df["Elevation_m"],
    bins=[
        float("-inf"),
        50,
        100,
        200,
        500,
        float("inf")
    ],
    labels=[
        "<50 m",
        "50–100 m",
        "100–200 m",
        "200–500 m",
        "500+ m"
    ]
)

df["Elevation Group"] = (
    df["Elevation Group"]
    .astype(object)
    .fillna("Unknown")
)

# Keep land-cover labels complete

df["Land Cover Group"] = (
    df["LCDB_Group_clean"]
    .fillna("Unknown")
)

# Keep severity colours consistent across charts

severity_order = [
    "Non-Injury Crash",
    "Minor Crash",
    "Serious Crash",
    "Fatal Crash"
]

severity_colors = {
    "Non-Injury Crash": "#00CC96",
    "Minor Crash": "#FFA15A",
    "Serious Crash": "#AB63FA",
    "Fatal Crash": "#EF553B"
}

predicted_colors = {
    "Non-Injury": "#00CC96",
    "Minor": "#FFA15A",
    "Serious": "#AB63FA",
    "Fatal": "#EF553B"
}

# Shared Plotly chart settings

CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}

def dark_chart(fig, height=480):
    fig.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        height=height,
        margin=dict(
            l=60,
            r=60,
            t=30,
            b=60
        ),
        hoverlabel=dict(
            bgcolor="#222222",
            font_color="white"
        )
    )
    fig.update_xaxes(
        gridcolor="#333333",
        zerolinecolor="#333333"
    )
    fig.update_yaxes(
        gridcolor="#333333",
        zerolinecolor="#333333"
    )
    return fig

# Sidebar controls and project summary

st.sidebar.title("Dashboard Controls")

# Project summary shown in the sidebar

st.sidebar.subheader("About This Project")

st.sidebar.info(
    """
    This project uses machine learning to classify the
    severity of already recorded New Zealand road crashes.
    Target classes:
    • Non-Injury
    • Minor
    • Serious
    • Fatal
    The project does not predict whether a crash will occur.
    """
)

st.sidebar.divider()

# Region selector

st.sidebar.subheader("Explore Crash Data")

region_options = sorted(
    df["_region"]
    .dropna()
    .unique()
    .tolist()
)

selected_region = st.sidebar.selectbox(
    "Region",
    options=["All Regions"] + region_options
)

# Limit year choices to the selected region

if selected_region == "All Regions":
    year_source = df.copy()
else:
    year_source = df[
        df["_region"] == selected_region
    ]
year_options = sorted(
    year_source["_year"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

selected_year = st.sidebar.selectbox(
    "Crash Year",
    options=["All Years"] +
    [str(year) for year in year_options]
)

# Apply the selected region and year filters

filtered_df = df.copy()

if selected_region != "All Regions":
    filtered_df = filtered_df[
        filtered_df["_region"] == selected_region
    ]
if selected_year != "All Years":
    filtered_df = filtered_df[
        filtered_df["_year"] == int(selected_year)
    ]

# Show the current filter selection

st.sidebar.divider()

st.sidebar.metric(
    "Displayed Crash Records",
    f"{len(filtered_df):,}"
)

st.sidebar.caption(
    f"Full dataset: {len(df):,} crash records"
)

if selected_region == "All Regions":
    region_text = "All Regions"
else:
    region_text = selected_region
if selected_year == "All Years":
    year_text = "All Years"
else:
    year_text = selected_year
st.sidebar.markdown(
    f"""
    **Current selection**
    Region: **{region_text}**
    Year: **{year_text}**
    """
)

st.sidebar.caption(
    "Filters affect Overview and Contextual Features only. "
    "Model Performance and Model Interpretation remain fixed."
)

# Let users download the current filtered view

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.sidebar.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="filtered_NZ_crash_data.csv",
    mime="text/csv"
)

# Dashboard title and project purpose

st.title(
    "New Zealand Road Crash Severity Dashboard"
)

st.markdown(
    """
    ### Project Purpose
    This project investigates whether machine-learning models
    can classify the severity of **recorded New Zealand road
    crashes** using CAS crash attributes and additional
    contextual information.
    The prediction target is **crash severity**, represented by
    four classes: **Non-Injury, Minor, Serious and Fatal**.
    **The project does not predict crash occurrence or the
    probability of a future crash.**
    """
)

st.caption(
    "Descriptive and contextual charts respond to the sidebar "
    "filters. Model evaluation and SHAP results are fixed results "
    "from the full modelling experiment."
)

st.divider()

# Main dashboard sections

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "🌍 Contextual Features",
        "🤖 Model Performance",
        "🔍 Model Interpretation"
    ]
)

# Overview tab

with tab1:
    st.header("Crash Overview")
    st.caption(
        f"Current view: {region_text} | {year_text}"
    )

    # Summary cards

    severity_counts = (
        filtered_df["crashSeverity"]
        .value_counts()
    )
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "Total Crashes",
            f"{len(filtered_df):,}"
        )
    with col2:
        st.metric(
            "Non-Injury",
            f"{severity_counts.get('Non-Injury Crash', 0):,}"
        )
    with col3:
        st.metric(
            "Minor",
            f"{severity_counts.get('Minor Crash', 0):,}"
        )
    with col4:
        st.metric(
            "Serious",
            f"{severity_counts.get('Serious Crash', 0):,}"
        )
    with col5:
        st.metric(
            "Fatal",
            f"{severity_counts.get('Fatal Crash', 0):,}"
        )
    st.divider()

    # Severity distribution

    st.subheader(
        "Crash Severity Distribution"
    )
    severity_df = (
        filtered_df["crashSeverity"]
        .value_counts()
        .reindex(severity_order)
        .fillna(0)
        .reset_index()
    )
    severity_df.columns = [
        "Severity",
        "Number of Crashes"
    ]
    fig_severity = px.bar(
        severity_df,
        x="Severity",
        y="Number of Crashes",
        color="Severity",
        color_discrete_map=severity_colors,
        category_orders={
            "Severity": severity_order
        },
        text="Number of Crashes",
        template="plotly_dark"
    )
    fig_severity.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )
    fig_severity.update_layout(
        showlegend=False
    )
    dark_chart(
        fig_severity,
        height=450
    )
    st.plotly_chart(
        fig_severity,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Regional crash counts

    st.subheader(
        "Crashes by Region"
    )
    region_df = (
        filtered_df["_region"]
        .value_counts()
        .reset_index()
    )
    region_df.columns = [
        "Region",
        "Number of Crashes"
    ]
    fig_region = px.bar(
        region_df,
        x="Number of Crashes",
        y="Region",
        orientation="h",
        text="Number of Crashes",
        template="plotly_dark"
    )
    fig_region.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )
    fig_region.update_layout(
        yaxis=dict(
            title="Region",
            categoryorder="total ascending"
        ),
        xaxis_title="Number of Crashes"
    )
    dark_chart(
        fig_region,
        height=600
    )
    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Crash counts by year

    st.subheader(
        "Crashes by Year"
    )
    year_df = (
        filtered_df["_year"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    year_df.columns = [
        "Year",
        "Number of Crashes"
    ]
    year_df["Year"] = (
        year_df["Year"]
        .astype(str)
    )
    fig_year = px.bar(
        year_df,
        x="Year",
        y="Number of Crashes",
        text="Number of Crashes",
        template="plotly_dark"
    )
    fig_year.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )
    fig_year.update_layout(
        xaxis_title="Crash Year",
        yaxis_title="Number of Crashes"
    )
    dark_chart(
        fig_year,
        height=450
    )
    st.plotly_chart(
        fig_year,
        use_container_width=True,
        config=CHART_CONFIG
    )
    if 2026 in filtered_df["_year"].dropna().values:
        st.caption(
            "2026 represents partial-year data in this dataset. "
            "It should not be interpreted as a complete year-to-year "
            "comparison with 2025."
        )

    # Crash counts by speed limit

    st.subheader(
        "Crashes by Speed Limit"
    )
    speed_df = (
        filtered_df["Speed Limit Group"]
        .value_counts()
        .reset_index()
    )
    speed_df.columns = [
        "Speed Limit",
        "Number of Crashes"
    ]
    speed_df["Sort Value"] = pd.to_numeric(
        speed_df["Speed Limit"],
        errors="coerce"
    )
    speed_df.loc[
        speed_df["Speed Limit"] == "Unknown",
        "Sort Value"
    ] = 999
    speed_df = speed_df.sort_values(
        "Sort Value"
    )
    fig_speed = px.bar(
        speed_df,
        x="Speed Limit",
        y="Number of Crashes",
        text="Number of Crashes",
        template="plotly_dark"
    )
    fig_speed.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )
    fig_speed.update_layout(
        xaxis_title="Speed Limit (km/h)",
        yaxis_title="Number of Crashes"
    )
    dark_chart(
        fig_speed,
        height=450
    )
    st.plotly_chart(
        fig_speed,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "Unknown indicates records where a speed-limit value "
        "was unavailable in the dataset."
    )

    # Optional preview of filtered records

    with st.expander(
        "Preview Filtered Crash Data"
    ):
        st.dataframe(
            filtered_df.head(100),
            use_container_width=True
        )

# Contextual features tab

with tab2:
    st.header(
        "Contextual Features"
    )
    st.caption(
        f"Current view: {region_text} | {year_text}"
    )
    st.info(
        "These charts describe associations in the recorded crash "
        "data. They do not establish causal relationships."
    )

    # Crash counts by distance to the nearest junction

    st.subheader(
        "Crashes by Distance to Nearest Junction"
    )
    junction_counts = (
        filtered_df["Distance Group"]
        .value_counts(sort=False)
        .reindex(distance_order)
        .fillna(0)
        .reset_index()
    )
    junction_counts.columns = [
        "Distance to Junction",
        "Number of Crashes"
    ]
    fig_junction = px.bar(
        junction_counts,
        x="Distance to Junction",
        y="Number of Crashes",
        text="Number of Crashes",
        template="plotly_dark"
    )
    fig_junction.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )
    fig_junction.update_layout(
        xaxis_title="Distance to Nearest Junction",
        yaxis_title="Number of Crashes"
    )
    dark_chart(
        fig_junction,
        height=450
    )
    st.plotly_chart(
        fig_junction,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Severity mix across junction-distance groups

    st.subheader(
        "Crash Severity by Distance to Nearest Junction"
    )
    junction_severity = (
        filtered_df
        .groupby(
            [
                "Distance Group",
                "crashSeverity"
            ],
            observed=True
        )
        .size()
        .reset_index(
            name="Number of Crashes"
        )
    )
    junction_severity["Percentage"] = (
        junction_severity["Number of Crashes"]
        /
        junction_severity.groupby(
            "Distance Group",
            observed=True
        )["Number of Crashes"]
        .transform("sum")
        * 100
    )
    fig_junction_severity = px.bar(
        junction_severity,
        x="Distance Group",
        y="Percentage",
        color="crashSeverity",
        color_discrete_map=severity_colors,
        category_orders={
            "Distance Group": distance_order,
            "crashSeverity": severity_order
        },
        template="plotly_dark"
    )
    fig_junction_severity.update_layout(
        barmode="stack",
        xaxis_title="Distance to Nearest Junction",
        yaxis_title="Percentage of Crashes (%)",
        legend_title="Crash Severity"
    )
    fig_junction_severity.update_yaxes(
        range=[0, 100]
    )
    dark_chart(
        fig_junction_severity,
        height=500
    )
    st.plotly_chart(
        fig_junction_severity,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Severity mix across NZDep groups

    st.subheader(
        "Crash Severity by NZDep2023 Score Group"
    )
    nzdep_severity = (
        filtered_df
        .groupby(
            [
                "NZDep Group",
                "crashSeverity"
            ],
            observed=True
        )
        .size()
        .reset_index(
            name="Number of Crashes"
        )
    )
    nzdep_severity["Percentage"] = (
        nzdep_severity["Number of Crashes"]
        /
        nzdep_severity.groupby(
            "NZDep Group"
        )["Number of Crashes"]
        .transform("sum")
        * 100
    )
    nzdep_display_order = (
        nzdep_order + ["Unknown"]
    )
    fig_nzdep = px.bar(
        nzdep_severity,
        x="NZDep Group",
        y="Percentage",
        color="crashSeverity",
        color_discrete_map=severity_colors,
        category_orders={
            "NZDep Group": nzdep_display_order,
            "crashSeverity": severity_order
        },
        template="plotly_dark"
    )
    fig_nzdep.update_layout(
        barmode="stack",
        xaxis_title=(
            "NZDep2023 Score Quintile "
            "(defined using the full crash dataset)"
        ),
        yaxis_title="Percentage of Crashes (%)",
        legend_title="Crash Severity"
    )
    fig_nzdep.update_yaxes(
        range=[0, 100]
    )
    dark_chart(
        fig_nzdep,
        height=500
    )
    st.plotly_chart(
        fig_nzdep,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "Q1–Q5 are quintiles created from NZDep2023 scores in the "
        "full crash dataset. They are not official NZDep deciles."
    )

    # Severity mix across land-cover groups

    st.subheader(
        "Crash Severity by Land Cover"
    )
    lcdb_severity = (
        filtered_df
        .groupby(
            [
                "Land Cover Group",
                "crashSeverity"
            ],
            observed=True
        )
        .size()
        .reset_index(
            name="Number of Crashes"
        )
    )
    lcdb_severity["Percentage"] = (
        lcdb_severity["Number of Crashes"]
        /
        lcdb_severity.groupby(
            "Land Cover Group"
        )["Number of Crashes"]
        .transform("sum")
        * 100
    )
    fig_lcdb = px.bar(
        lcdb_severity,
        x="Land Cover Group",
        y="Percentage",
        color="crashSeverity",
        color_discrete_map=severity_colors,
        category_orders={
            "crashSeverity": severity_order
        },
        template="plotly_dark"
    )
    fig_lcdb.update_layout(
        barmode="stack",
        xaxis_title="Land Cover Group",
        yaxis_title="Percentage of Crashes (%)",
        legend_title="Crash Severity"
    )
    fig_lcdb.update_yaxes(
        range=[0, 100]
    )
    dark_chart(
        fig_lcdb,
        height=520
    )
    st.plotly_chart(
        fig_lcdb,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Severity mix across elevation groups

    st.subheader(
        "Crash Severity by Elevation"
    )
    elevation_severity = (
        filtered_df
        .groupby(
            [
                "Elevation Group",
                "crashSeverity"
            ],
            observed=True
        )
        .size()
        .reset_index(
            name="Number of Crashes"
        )
    )
    elevation_severity["Percentage"] = (
        elevation_severity["Number of Crashes"]
        /
        elevation_severity.groupby(
            "Elevation Group"
        )["Number of Crashes"]
        .transform("sum")
        * 100
    )
    fig_elevation = px.bar(
        elevation_severity,
        x="Elevation Group",
        y="Percentage",
        color="crashSeverity",
        color_discrete_map=severity_colors,
        category_orders={
            "Elevation Group": elevation_order,
            "crashSeverity": severity_order
        },
        template="plotly_dark"
    )
    fig_elevation.update_layout(
        barmode="stack",
        xaxis_title="Elevation",
        yaxis_title="Percentage of Crashes (%)",
        legend_title="Crash Severity"
    )
    fig_elevation.update_yaxes(
        range=[0, 100]
    )
    dark_chart(
        fig_elevation,
        height=500
    )
    st.plotly_chart(
        fig_elevation,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "Unknown indicates records where a valid elevation "
        "value was unavailable."
    )

    # Contextual-data coverage checks

    with st.expander(
        "Contextual Data Coverage"
    ):
        st.write(
            f"Selected crash records: **{len(filtered_df):,}**"
        )
        st.write(
            "Missing NZDep2023 score:",
            f"{filtered_df['NZDep2023_Score'].isna().sum():,}"
        )
        st.write(
            "Missing elevation:",
            f"{filtered_df['Elevation_m'].isna().sum():,}"
        )
        st.write(
            "Distance-to-junction missing:",
            f"{filtered_df['dist_to_junction_m'].isna().sum():,}"
        )

# Model performance tab

with tab3:
    st.header(
        "Model Performance"
    )
    st.info(
        "These are fixed evaluation results from the modelling "
        "experiment on the full dataset. Sidebar filters do not "
        "recalculate model performance."
    )

    # Fixed model evaluation results

    performance_df = pd.DataFrame(
        {
            "Metric": [
                "Accuracy",
                "Balanced Accuracy",
                "Macro F1",
                "Fatal Recall",
                "Serious Recall"
            ],
            "CAS-Only": [
                0.4940,
                0.4062,
                0.3288,
                0.3077,
                0.3944
            ],
            "Final National Context": [
                0.5184,
                0.3947,
                0.3389,
                0.2215,
                0.3756
            ]
        }
    )

    # Key changes from the CAS-only baseline

    st.subheader(
        "Performance Change"
    )
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.metric(
            "Accuracy",
            "0.5184",
            "+0.0243"
        )
    with p2:
        st.metric(
            "Balanced Accuracy",
            "0.3947",
            "-0.0115"
        )
    with p3:
        st.metric(
            "Macro F1",
            "0.3389",
            "+0.0101"
        )
    with p4:
        st.metric(
            "Fatal Recall",
            "0.2215",
            "-0.0862"
        )
    with p5:
        st.metric(
            "Serious Recall",
            "0.3756",
            "-0.0188"
        )

    # Compare the baseline and final contextual model

    st.subheader(
        "CAS-Only vs Final National Context"
    )
    performance_long = performance_df.melt(
        id_vars="Metric",
        var_name="Model",
        value_name="Score"
    )
    fig_performance = px.bar(
        performance_long,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        text="Score",
        template="plotly_dark"
    )
    fig_performance.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )
    fig_performance.update_layout(
        xaxis_title="Performance Metric",
        yaxis_title="Score",
        legend_title="Model"
    )
    fig_performance.update_yaxes(
        range=[0, 0.6]
    )
    dark_chart(
        fig_performance,
        height=500
    )
    st.plotly_chart(
        fig_performance,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "The final contextual model improved Accuracy and Macro F1, "
        "but Balanced Accuracy, Fatal Recall and Serious Recall decreased."
    )

    # Five-seed robustness summary

    with st.expander(
        "Five-Seed Evaluation Summary"
    ):
        seed_summary = pd.DataFrame(
            {
                "Metric": [
                    "Accuracy",
                    "Balanced Accuracy",
                    "Macro F1",
                    "Fatal Recall",
                    "Serious Recall"
                ],
                "CAS-Only Mean ± SD": [
                    "0.4940 ± 0.0039",
                    "0.4062 ± 0.0123",
                    "0.3288 ± 0.0049",
                    "0.3077 ± 0.0435",
                    "0.3944 ± 0.0157"
                ],
                "Final Context Mean ± SD": [
                    "0.5184 ± 0.0046",
                    "0.3947 ± 0.0073",
                    "0.3389 ± 0.0043",
                    "0.2215 ± 0.0257",
                    "0.3756 ± 0.0139"
                ]
            }
        )
        st.dataframe(
            seed_summary,
            use_container_width=True,
            hide_index=True
        )

    # Severe-class error analysis

    st.subheader(
        "Final Model Error Analysis: Fatal and Serious Crashes"
    )
    saved_errors = pd.DataFrame({'Actual_Severity': ['Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash'], 'Predicted_Severity': ['Fatal Crash', 'Serious Crash', 'Minor Crash', 'Non-Injury Crash', 'Fatal Crash', 'Serious Crash', 'Minor Crash', 'Non-Injury Crash'], 'Count': [14, 30, 11, 10, 31, 198, 172, 100], 'Percentage': [21.54, 46.15, 16.92, 15.38, 6.19, 39.52, 34.33, 19.96]})
    error_df = saved_errors.rename(columns={
        "Actual_Severity": "Actual Severity",
        "Predicted_Severity": "Predicted Severity",
        "Count": "Number of Crashes"
    })
    for column in ["Actual Severity", "Predicted Severity"]:
        error_df[column] = error_df[column].str.replace(" Crash", "", regex=False)
    error_df["Percentage"] = (
        error_df["Number of Crashes"]
        /
        error_df.groupby(
            "Actual Severity"
        )["Number of Crashes"]
        .transform("sum")
        * 100
    )
    fig_error = px.bar(
        error_df,
        x="Actual Severity",
        y="Percentage",
        color="Predicted Severity",
        color_discrete_map=predicted_colors,
        text="Number of Crashes",
        barmode="stack",
        template="plotly_dark"
    )
    fig_error.update_traces(
        texttemplate="%{text}",
        textposition="inside"
    )
    fig_error.update_layout(
        xaxis_title="Actual Crash Severity",
        yaxis_title="Percentage of Crashes (%)",
        legend_title="Predicted Severity"
    )
    fig_error.update_yaxes(
        range=[0, 100]
    )
    dark_chart(
        fig_error,
        height=500
    )
    st.plotly_chart(
        fig_error,
        use_container_width=True,
        config=CHART_CONFIG
    )

    # Summarise the main severe-class errors

    e1, e2 = st.columns(2)
    with e1:
        st.markdown(
            """
            **Actual Fatal crashes**
            65 crashes in the evaluation set.
            - Predicted Fatal: 14
            - Predicted Serious: 30
            - Predicted Minor: 11
            - Predicted Non-Injury: 10
            """
        )
    with e2:
        st.markdown(
            """
            **Actual Serious crashes**
            501 crashes in the evaluation set.
            - Predicted Serious: 198
            - Predicted Fatal: 31
            - Predicted Minor: 172
            - Predicted Non-Injury: 100
            """
        )

# Model interpretation tab

with tab4:
    st.header(
        "Model Interpretation"
    )
    st.caption("SHAP explains raw class margins. Signed means do not establish monotonic relationships. Each class plot uses its saved top 15 features.")
    st.info(
        "SHAP results below are fixed results from the trained final "
        "model. Sidebar filters do not alter these values."
    )

    # Global SHAP importance

    st.subheader(
        "Global SHAP Feature Importance"
    )
    shap_df = pd.DataFrame({'Rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 'Feature': ['dist_to_junction_m', 'motorcycle', 'LCDB_Group_clean', 'NZDep2023_Score', 'speedLimit', 'carStationWagon', 'light', 'roadLane', 'Elevation_m', 'streetLight', 'flatHill', 'region', 'weatherA', 'truck', 'crashDirectionDescription'], 'Mean_Absolute_SHAP': [0.135356, 0.112051, 0.110596, 0.104752, 0.10315, 0.099278, 0.090584, 0.08853, 0.08467, 0.081191, 0.07153, 0.070644, 0.048851, 0.048303, 0.044265]}).rename(
        columns={"Mean_Absolute_SHAP": "Mean |SHAP|"}
    )
    shap_df = shap_df.sort_values(
        "Mean |SHAP|",
        ascending=True
    )
    fig_shap = px.bar(
        shap_df,
        x="Mean |SHAP|",
        y="Feature",
        orientation="h",
        text="Mean |SHAP|",
        template="plotly_dark"
    )
    fig_shap.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )
    fig_shap.update_layout(
        xaxis_title="Mean Absolute SHAP Value",
        yaxis_title="Feature"
    )
    dark_chart(
        fig_shap,
        height=600
    )
    st.plotly_chart(
        fig_shap,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "SHAP importance represents contribution to the model's "
        "predictions. It does not demonstrate causation."
    )

    # Top 15 features for each class; omitted features have no displayed value.

    st.subheader(
        "Fatal vs Serious SHAP Feature Importance"
    )
    saved_class_shap = pd.DataFrame({'Class': ['Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Fatal Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash', 'Serious Crash'], 'Rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 'Feature': ['speedLimit', 'dist_to_junction_m', 'NZDep2023_Score', 'Elevation_m', 'roadLane', 'light', 'LCDB_Group_clean', 'region', 'crashDirectionDescription', 'truck', 'carStationWagon', 'crashFinancialYear', 'directionRoleDescription', 'motorcycle', 'crashYear', 'carStationWagon', 'flatHill', 'motorcycle', 'streetLight', 'dist_to_junction_m', 'NZDep2023_Score', 'weatherA', 'Elevation_m', 'light', 'region', 'LCDB_Group_clean', 'crashFinancialYear', 'directionRoleDescription', 'speedLimit', 'trafficControl'], 'Mean_Absolute_SHAP': [0.301204, 0.285452, 0.272411, 0.202134, 0.193506, 0.15935, 0.151213, 0.142887, 0.104176, 0.100877, 0.088485, 0.072568, 0.071988, 0.066842, 0.045246, 0.179154, 0.114446, 0.110575, 0.100256, 0.088433, 0.071346, 0.066494, 0.05866, 0.05096, 0.048484, 0.044688, 0.042277, 0.040586, 0.038879, 0.032825], 'Mean_Signed_SHAP': [-0.161414, -0.256926, -0.225997, -0.165644, -0.097662, -0.066198, -0.072875, -0.094856, -0.075031, -0.036669, -0.062546, -0.032029, -0.045351, -0.040957, -0.012608, -0.085883, -0.090402, -0.056335, -0.061486, -0.025065, -0.007188, -0.00947, -0.011402, -0.004378, 0.000147, -0.018511, 0.00046, -0.002013, 0.006456, -0.005238]})
    saved_class_shap["Class"] = saved_class_shap["Class"].str.replace(" Crash", "", regex=False)
    class_shap_df = saved_class_shap.pivot(index="Feature", columns="Class", values="Mean_Absolute_SHAP").reset_index()
    class_shap_long = (
        class_shap_df.melt(
            id_vars="Feature",
            var_name="Crash Severity",
            value_name="Mean |SHAP|"
        )
    )
    class_shap_long = class_shap_long.dropna(subset=["Mean |SHAP|"])
    feature_order = (
        class_shap_df
        .assign(
            MaxImportance=
            class_shap_df[
                ["Fatal", "Serious"]
            ].max(axis=1)
        )
        .sort_values(
            "MaxImportance",
            ascending=False
        )["Feature"]
        .tolist()
    )
    fig_class_shap = px.bar(
        class_shap_long,
        x="Mean |SHAP|",
        y="Feature",
        color="Crash Severity",
        orientation="h",
        barmode="group",
        category_orders={
            "Feature": feature_order
        },
        template="plotly_dark"
    )
    fig_class_shap.update_layout(
        xaxis_title="Mean Absolute SHAP Value",
        yaxis_title="Feature",
        legend_title="Crash Severity"
    )
    fig_class_shap.update_yaxes(
        autorange="reversed"
    )
    dark_chart(
        fig_class_shap,
        height=700
    )
    st.plotly_chart(
        fig_class_shap,
        use_container_width=True,
        config=CHART_CONFIG
    )
    st.caption(
        "Fatal and Serious crashes show different feature-importance "
        "patterns. SHAP values describe model behaviour, not causal effects."
    )

    # Short guide to interpreting SHAP

    with st.expander(
        "How to Interpret SHAP"
    ):
        st.markdown(
            """
            A larger mean absolute SHAP value means that a feature
            contributed more strongly to the model's predictions on
            average.
            It does **not** mean that the feature causes a crash to
            become more severe.
            For example, a high SHAP importance for **Distance to
            Junction** means the model used that variable strongly when
            distinguishing severity classes. It does not prove that
            distance from a junction causes severe crashes.
            """
        )

# Footer
st.divider()

st.caption(
    "NZ Road Crash Severity Prediction Project | "
    "CAS crash data with contextual spatial and environmental features"
)
