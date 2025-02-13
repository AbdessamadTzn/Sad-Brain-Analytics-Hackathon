import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.colors
import plotly.graph_objects as go

# Register the page for Dash
dash.register_page(__name__)

# Load the dataset
try:
    df = pd.read_csv("../assets/df_students.csv")
except Exception as e:
    print(f'File reading error: {str(e)}')
    exit()

# Assign age groups directly
df['Age Group'] = df['Age']

# Define academic pressure levels (low, medium, high)
academic_pressure_order = {"Low": 0, "Medium": 1, "High": 2}
df['Academic Pressure Level'] = df['Academic Pressure'].apply(lambda x: 'Low' if x <= 4 else ('Medium' if x <= 7 else 'High'))

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

        html.Label("Select Academic Pressure Level:"),
        dcc.Dropdown(
            id='academic-pressure-dropdown',
            options=[{'label': level, 'value': level} for level in academic_pressure_order.keys()],
            value=None,
            placeholder="Select academic pressure level",
            style={'marginBottom': '15px'}
        ),
    ], style={'width': '20%', 'float': 'left', 'padding': '10px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='barplot-cgpa1', style={'height': '400px'}),
            dcc.Graph(id='pie-depression1', config={'displayModeBar': False}, style={'height': '400px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        html.Div([
            dcc.Graph(id='sunburst-chart1', style={'height': '400px'}),
            dcc.Graph(id='animated-bar-chart1', style={'height': '400px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ], style={'width': '80%', 'float': 'right', 'padding': '10px'})
])

# Callback to update graphs based on selection
@callback(
    [Output('barplot-cgpa1', 'figure'),
     Output('pie-depression1', 'figure'),
     Output('sunburst-chart1', 'figure'),
     Output('animated-bar-chart1', 'figure')],
    [Input('age-group-dropdown', 'value'),
     Input('degree-category-dropdown', 'value'),
     Input('gender-dropdown', 'value'),
     Input('academic-pressure-dropdown', 'value'),
     Input('barplot-cgpa1', 'clickData')]
)
def update_graphs(selected_age_group, selected_degree_category, selected_gender, 
                  selected_academic_pressure, click_data):
    filtered_df = df
    if selected_age_group:
        filtered_df = filtered_df[filtered_df['Age'] == selected_age_group]
    if selected_degree_category:
        filtered_df = filtered_df[filtered_df['Degree'] == selected_degree_category]
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    if selected_academic_pressure is not None:
        filtered_df = filtered_df[filtered_df['Academic Pressure Level'] == selected_academic_pressure]
    
    # highlight_city = None
    # if click_data and 'points' in click_data:
    #     highlight_city = click_data_city['points'][0]['x']
    
    # Bar Plot: CGPA vs. City
    bar_data = filtered_df.groupby('City')['CGPA'].mean().reset_index()
    # bar_data['Highlight'] = bar_data['City'].apply(lambda x: 'Selected' if x == highlight_city else 'Others')
    
    barplot_fig = px.bar(
        bar_data,
        x='City', y='CGPA',
        title="Average CGPA by City",
        template="minty",
        labels={'City': 'City', 'CGPA': 'Average CGPA'},
        color='City',
        color_discrete_sequence=color_palette
    )

    # Filter pie chart based on the clicked profession (if any)
    if click_data:
        clicked_city = click_data['points'][0]['x']
        filtered_df = filtered_df[filtered_df['City'] == clicked_city]


    # Pie Chart: Depression Distribution
    pie_fig = go.Figure(
        go.Pie(
            labels=['Not Depressed', 'Depressed'],
            values=[filtered_df['Depression_numeric'].value_counts().get(0, 0),
                    filtered_df['Depression_numeric'].value_counts().get(1, 0)],
            hole=0.4,
            marker=dict(colors=['lightgreen', 'lightcoral'])
        )
    )

    # Sunburst Chart: Academic Pressure, Sleep, City, Dietary Habits
    sunburst_fig = px.sunburst(
        filtered_df,
        path=['Academic Pressure Level', 'Sleep Duration', 'City', 'Dietary Habits'],
        values='Depression_numeric',
        title="Academic Pressure, Sleep, City, and Dietary Habits"
    )

    # Animated Bar Chart: Financial Stress by Gender & City
    animated_bar_fig = px.bar(
        filtered_df.groupby(['Gender', 'City'], as_index=False)['Financial Stress'].mean(),
        x="Gender", y="Financial Stress", color="City",
        title="Average Financial Stress by Gender and City",
        labels={"Financial Stress": "Avg Financial Stress"},
        barmode="group"
    )

    return barplot_fig, pie_fig, sunburst_fig, animated_bar_fig
