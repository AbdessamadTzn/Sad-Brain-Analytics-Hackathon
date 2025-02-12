import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.colors
import plotly.graph_objects as go
import numpy as np

# Register the page for Dash
dash.register_page(__name__)

# Load the dataset
try:
    df = pd.read_csv("../assets/df_work_professionals.csv")
except Exception as e:
    print(f'File reading error: {str(e)}')
    exit()

# Assign age groups directly
df['Age Group'] = df['Age']

# Define work pressure levels
work_pressure_order = {"Low": 0, "Medium": 1, "High": 2}
df['Work Pressure Level'] = df['Work Pressure'].apply(lambda x: 'Low' if x <= 1 else ('Medium' if x <= 3 else 'High'))

# Convert 'Depression' column to numeric: 'Yes' = 1, 'No' = 0
df['Depression_numeric'] = df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)

# Define a Bootstrap-like color palette from Plotly
color_palette = plotly.colors.qualitative.Pastel
age_order = {'Under 25': 0, '25-34': 1, '35-44': 2, '45-54': 3, '+55': 4}
degree_order = {'Pre-University': 0, 'Undergraduate': 1, 'Postgraduate': 2, 'Doctorate/Professional': 3, 'Other': 4}

# Layout with dropdowns and graphs
layout = html.Div([
    # Dropdown to filter by age group
    html.Label("Select Age Group:"),
    dcc.Dropdown(
        id='age-group-dropdown',
        options=[{'label': age_group, 'value': age_group} for age_group in sorted(df['Age'].unique(), key=lambda x: age_order[x])],
        value=None,
        placeholder="Select an age group",
        style={'marginBottom': '20px'}
    ),

    # Dropdown to filter by degree category
    html.Label("Select Degree Category:"),
    dcc.Dropdown(
        id='degree-category-dropdown',
        options=[{'label': degree, 'value': degree} for degree in sorted(df['Degree'].unique(), key=lambda x: degree_order[x])],
        value=None,
        placeholder="Select a degree category",
        style={'marginBottom': '20px'}
    ),

    # Dropdown to filter by gender
    html.Label("Select Gender:"),
    dcc.Dropdown(
        id='gender-dropdown',
        options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()],
        value=None,
        placeholder="Select a gender",
        style={'marginBottom': '20px'}
    ),

    # Dropdown to filter by work pressure level
    html.Label("Select Work Pressure Level:"),
    dcc.Dropdown(
        id='work-pressure-dropdown',
        options=[{'label': level, 'value': level} for level in work_pressure_order.keys()],
        value=None,
        placeholder="Select work pressure level",
        style={'marginBottom': '20px'}
    ),

    # First graph: Profession vs Work Pressure
    dcc.Graph(id='barplot-profession'),
    html.Br(),

    # Pie chart for depression percentage
    dcc.Graph(id='pie-depression', config={'displayModeBar': False}),
    
    # 3D Scatter plot: Activity Hours vs Sleep Duration vs Work Pressure
    dcc.Graph(id='scatter-3d'),

    # Sunburst Chart: City, Dietary Habits, Sleep Duration, Work Pressure Level
    dcc.Graph(id='sunburst-chart')
])

# Callback to update graphs based on selection
@callback(
    [Output('barplot-profession', 'figure'),
     Output('pie-depression', 'figure'),
     Output('scatter-3d', 'figure'),
     Output('sunburst-chart', 'figure')],  # Added output for Sunburst chart
    [Input('age-group-dropdown', 'value'),
     Input('degree-category-dropdown', 'value'),
     Input('gender-dropdown', 'value'),
     Input('work-pressure-dropdown', 'value'),
     Input('barplot-profession', 'clickData')]  # Capture clickData for interaction
)
def update_graphs(selected_age_group, selected_degree_category, selected_gender, selected_work_pressure, click_data):
    # Filter the data (this filter will apply to all charts)
    filtered_df = df
    if selected_age_group:
        filtered_df = filtered_df[filtered_df['Age Group'] == selected_age_group]
    if selected_degree_category:
        filtered_df = filtered_df[filtered_df['Degree'] == selected_degree_category]
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    if selected_work_pressure:
        filtered_df = filtered_df[filtered_df['Work Pressure Level'] == selected_work_pressure]

    # Update bar chart (showing all professions)
    profession_fig = px.bar(
        filtered_df.groupby('Profession')['Work Pressure'].mean().reset_index(),
        x='Profession', y='Work Pressure',
        title="Profession vs Average Work Pressure",
        template="minty",
        labels={'Profession': 'Profession', 'Work Pressure': 'Average Work Pressure'},
        color='Profession',
        color_discrete_sequence=color_palette
    )

    # Filter pie chart based on the clicked profession (if any)
    if click_data:
        clicked_profession = click_data['points'][0]['x']
        filtered_df = filtered_df[filtered_df['Profession'] == clicked_profession]

    # Update pie chart based on filtered data
    pie_fig = go.Figure(
        go.Pie(
            labels=['Not Depressed', 'Depressed'],
            values=[filtered_df['Depression_numeric'].value_counts().get(0, 0),
                    filtered_df['Depression_numeric'].value_counts().get(1, 0)],
            hole=0.4,
            marker=dict(colors=['lightgreen', 'lightcoral'])
        )
    )

    # Create 3D Scatter plot
    scatter_3d_fig = px.scatter_3d(
        filtered_df,
        height=700,
        width=1000,
        x='Activity Hours',
        y='Sleep Duration',
        z='Work Pressure',
        color='Work Pressure Level',
        size='Work Pressure',
        title="3D Scatter Plot: Activity Hours vs Sleep Duration vs Work Pressure",
        opacity=0.8
    )

    # # Prepare data for sunburst chart
    # agg_df = filtered_df.groupby(['City', 'Dietary Habits', 'Sleep Duration', 'Work Pressure Level']).agg(
    #     count=('Depression_numeric', 'size'),
    #     avg_depression=('Depression_numeric', 'mean')
    # ).reset_index()

    # Prepare data for sunburst chart
    agg_df = filtered_df.groupby(['City', 'Dietary Habits', 'Sleep Duration', 'Work Pressure Level']).agg(
        count=('Depression_numeric', 'size'),
        percentage_depression=('Depression_numeric', lambda x: (x.sum() / len(x)) * 100)  # Calculate percentage
    ).reset_index()

    # Create Sunburst Chart
    sunburst_fig = px.sunburst(
        agg_df,
        path=['City', 'Dietary Habits', 'Sleep Duration', 'Work Pressure Level'],  # Hierarchy
        values='count',  # Number of individuals in each category
        color='percentage_depression',  # Color by average depression rate
        color_continuous_scale='RdBu',  # Red for high, blue for low depression
        color_continuous_midpoint=np.average(agg_df['percentage_depression'], weights=agg_df['count']),
        title="Sunburst Chart: City, Dietary Habits, Sleep, and Work Pressure with Depression Levels"
    )

    return profession_fig, pie_fig, scatter_3d_fig, sunburst_fig
