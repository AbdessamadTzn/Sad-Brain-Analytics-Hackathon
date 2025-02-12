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
    
    # Bubble chart: Activity Hours vs Sleep Duration
    dcc.Graph(id='bubble-activity-sleep')
])

# Callback to update graphs based on selection
@callback(
    [Output('barplot-profession', 'figure'),
     Output('pie-depression', 'figure'),
     Output('bubble-activity-sleep', 'figure')],  # New output for bubble chart
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

    # Now, let's create the bubble chart for Activity Hours vs Sleep Duration
    # Calculate bubble sizes based on 'Work Pressure Level'
    bubble_size = filtered_df['Work Pressure Level'].map({'Low': 30, 'Medium': 60, 'High': 90})  # Adjusted bubble size scaling

    # Color the bubbles based on 'Work Pressure Level'
    bubble_colors = filtered_df['Work Pressure Level'].map({'Low': 'lightgreen', 'Medium': 'orange', 'High': 'red'})  # Distinct colors for bubbles

    # Create hover text for the bubble chart
    hover_text_bubble = []
    for index, row in filtered_df.iterrows():
        hover_text_bubble.append(('Gender: {gender}<br>' +
                                  'Age Group: {age_group}<br>' +
                                  'Profession: {profession}<br>' +
                                  'Degree: {degree}<br>' +
                                  'City: {city}<br>' +
                                  'Dietary Habits: {dietary_habits}<br>' +
                                  'Sleep Duration: {sleep_duration}<br>' +
                                  'Activity Hours: {activity_hours}<br>' +
                                  'Depression: {depression}').format(
            gender=row['Gender'],
            age_group=row['Age Group'],
            profession=row['Profession'],
            degree=row['Degree'],
            city=row['City'],
            dietary_habits=row['Dietary Habits'],
            sleep_duration=row['Sleep Duration'],
            activity_hours=row['Activity Hours'],
            depression=row['Depression']
        ))

    filtered_df['text_bubble'] = hover_text_bubble
    sizeref = 2. * max(bubble_size) / (100**2)

    bubble_fig = go.Figure()

    bubble_fig.add_trace(go.Scatter(
        x=filtered_df['Activity Hours'],
        y=filtered_df['Sleep Duration'],
        mode='markers',
        text=filtered_df['text_bubble'],
        marker=dict(
            size=bubble_size,
            color=bubble_colors,  # Apply colors to the bubbles
            sizemode='area',
            sizeref=sizeref,
            line_width=2
        )
    ))

    # Update the layout for the bubble chart
    bubble_fig.update_layout(
        title="Activity Hours vs Sleep Duration",
        xaxis=dict(title='Activity Hours', gridcolor='white', gridwidth=2),
        yaxis=dict(title='Sleep Duration (Hours)', gridcolor='white', gridwidth=2),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    return profession_fig, pie_fig, bubble_fig
