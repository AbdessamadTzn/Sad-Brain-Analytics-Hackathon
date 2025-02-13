import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.colors
import plotly.graph_objects as go
import math

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
    html.Div([
        html.Label("Select Age Group:"),
        dcc.Dropdown(
            id='age-group-dropdown',
            options=[{'label': age_group, 'value': age_group} for age_group in sorted(df['Age'].unique(), key=lambda x: age_order[x])],
            value=None,
            placeholder="Select an age group",
            style={'marginBottom': '15px'}
        ),

        html.Label("Select Degree Category:"),
        dcc.Dropdown(
            id='degree-category-dropdown',
            options=[{'label': degree, 'value': degree} for degree in sorted(df['Degree'].unique(), key=lambda x: degree_order[x])],
            value=None,
            placeholder="Select a degree category",
            style={'marginBottom': '15px'}
        ),

        html.Label("Select Gender:"),
        dcc.Dropdown(
            id='gender-dropdown',
            options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()],
            value=None,
            placeholder="Select a gender",
            style={'marginBottom': '15px'}
        ),

        html.Label("Select Work Pressure Level:"),
        dcc.Dropdown(
            id='work-pressure-dropdown',
            options=[{'label': level, 'value': level} for level in work_pressure_order.keys()],
            value=None,
            placeholder="Select work pressure level",
            style={'marginBottom': '15px'}
        ),
    ], style={'width': '20%', 'float': 'left', 'padding': '10px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='barplot-profession', style={'height': '400px'}),
            dcc.Graph(id='pie-depression', config={'displayModeBar': False}, style={'height': '400px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        html.Div([
            dcc.Graph(id='sunburst-chart', style={'height': '400px'}),
            dcc.Graph(id='animated-bar-chart', style={'height': '400px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ], style={'width': '80%', 'float': 'right', 'padding': '10px'})
])

# Callback to update graphs based on selection
@callback(
    [Output('barplot-profession', 'figure'),
     Output('pie-depression', 'figure'),
     Output('sunburst-chart', 'figure'),
     Output('animated-bar-chart', 'figure')],  # Added output for animated bar chart
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

    # Create Sunburst Chart
    # Group by the necessary columns
    agg_df = filtered_df.groupby(['City', 'Dietary Habits', 'Sleep Duration', 'Work Pressure Level']).agg(
        count=('Depression_numeric', 'size')
    ).reset_index()

    # Calculate the total count for each combination of 'City', 'Sleep Duration', and 'Work Pressure Level'
    agg_df['total_count'] = agg_df.groupby(['City', 'Sleep Duration', 'Work Pressure Level'])['count'].transform('sum')

    # Now, calculate the percentage of each dietary habit group
    agg_df['percentage_dietary_habits'] = (agg_df['count'] / agg_df['total_count']) * 100

    # Create Sunburst Chart
    sunburst_fig = px.sunburst(
        agg_df,
        path=['Work Pressure Level', 'Sleep Duration', 'City', 'Dietary Habits'],  # Hierarchy
        values='count',  # Number of individuals in each category
        color='percentage_dietary_habits',  # Color by percentage of dietary habits
        color_continuous_scale='RdBu',  # Red for high, blue for low
        title="Work Pressure, Activity Hours, City with Dietary Habit Percentages"
    )


    # Create Animated Bar Chart
    animated_bar_fig = px.bar(
        df.groupby(['Gender', 'City'], as_index=False)['Financial Stress'].mean(),
        x="Gender", y="Financial Stress", color="City",
        title="Average Financial Stress by Gender and City",
        labels={"Financial Stress": "Avg Financial Stress"},
        barmode="group"
    )
    
    return profession_fig, pie_fig, sunburst_fig, animated_bar_fig