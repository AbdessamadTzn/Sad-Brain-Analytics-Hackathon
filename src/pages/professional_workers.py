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
    df = pd.read_csv("../assets/df_work_professionals.csv")
except Exception as e:
    print(f'File reading error: {str(e)}')
    exit()

# Group the data by Degree category and calculate the average Job Satisfaction
avg_job_satisfaction_degree = df.groupby('Degree')['Job Satisfaction'].mean().reset_index()

# Group by profession and calculate the average work pressure
avg_work_pressure_profession = df.groupby('Profession')['Work Pressure'].mean().reset_index()

# Convert 'Depression' column to numeric: 'Yes' = 1, 'No' = 0
df['Depression_numeric'] = df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)

# Average depression score by city (now as numeric)
avg_depression_city = df.groupby('City')['Depression_numeric'].mean().reset_index()

# Define approximate latitude and longitude for the cities (assumed coordinates)
city_coords = {
    'Ghaziabad': [28.6692, 77.4538],
    'Kalyan': [19.2412, 73.1350],
    'Bhopal': [23.2599, 77.4126],
    'Thane': [19.2183, 72.9784],
    'Indore': [22.7196, 75.8577],
    'Pune': [18.5204, 73.8567],
    'Bangalore': [12.9716, 77.5946],
    'Hyderabad': [17.3850, 78.4867],
    'Srinagar': [34.0836, 74.7973],
    'Nashik': [19.9975, 73.7910],
    'Kolkata': [22.5726, 88.3639],
    'Ahmedabad': [23.0225, 72.5714],
    'Varanasi': [25.3176, 82.9739],
    'Chennai': [13.0827, 80.2707],
    'Jaipur': [26.9124, 75.7873],
    'Surat': [21.1702, 72.8311],
    'Vasai-Virar': [19.3000, 72.8178],
    'Patna': [25.5941, 85.1376],
    'Rajkot': [22.3039, 70.8022],
    'Lucknow': [26.8467, 80.9462],
    'Meerut': [28.9845, 77.7050],
    'Faridabad': [28.4089, 77.3133],
    'Kanpur': [26.4499, 80.3319],
    'Visakhapatnam': [17.6868, 83.2185],
    'Ludhiana': [30.9000, 75.8500],
    'Nagpur': [21.1458, 79.0882],
    'Mumbai': [19.0760, 72.8777],
    'Vadodara': [22.3072, 73.1812],
    'Agra': [27.1767, 78.0081],
    'Delhi': [28.6139, 77.2090]
}

# Merge the coordinates with the city depression data
avg_depression_city['Lat'] = avg_depression_city['City'].map(lambda city: city_coords.get(city, [None, None])[0])
avg_depression_city['Lon'] = avg_depression_city['City'].map(lambda city: city_coords.get(city, [None, None])[1])

# Define a Bootstrap-like color palette from Plotly
color_palette = plotly.colors.qualitative.Pastel

# Layout with only the graphs for this page
layout = html.Div([
    # First graph: Profession vs Work Pressure
    dcc.Graph(
        id='barplot-profession',
        figure=px.bar(avg_work_pressure_profession, x='Profession', y='Work Pressure',
                      title="Profession vs Average Work Pressure",
                      template="minty",
                      labels={'Profession': 'Profession', 'Work Pressure': 'Average Work Pressure'},
                      color='Profession',  # Set color based on profession
                      color_discrete_sequence=color_palette),  # Apply the custom color palette
        clickData=None  # Initialize clickData as None
    ),

    html.Br(),

    # Second graph: Job Satisfaction by Degree category
    dcc.Graph(
        id='barplot-degree',
        figure=px.bar(avg_job_satisfaction_degree,
                      x='Degree', y='Job Satisfaction',
                      title="Job Satisfaction by Degree Category",
                      template="minty",
                      labels={'Degree': 'Degree Category', 'Job Satisfaction': 'Average Job Satisfaction'},
                      color='Degree',  # Set color based on Degree category
                      color_discrete_sequence=color_palette),  # Apply the custom color palette
        clickData=None  # Initialize clickData as None
    ),

    html.Br(),

    # Choropleth map for city depression levels
    dcc.Graph(
        id='city-depression-map',
        figure=go.Figure(go.Choropleth(
            z=avg_depression_city['Depression_numeric'],
            hoverinfo='location+z',
            locations=avg_depression_city['City'],
            locationmode='country names',
            colorscale='Viridis',
            colorbar_title="Average Depression Level",
            text=avg_depression_city['City'],
            showscale=True
        )),
        config={'scrollZoom': False, 'displayModeBar': False}
    ),

    html.Br(),

    # Pie chart for depression status
    dcc.Graph(
        id='depression-pie',
        figure=go.Figure(
            go.Pie(
                labels=['Not Depressed', 'Depressed'],
                values=[df['Depression_numeric'].value_counts().get(0, 0),
                        df['Depression_numeric'].value_counts().get(1, 0)],
                title="Depression Percentage",
                hole=0.4,
                marker=dict(colors=['lightgreen', 'lightcoral'])
            )
        )
    )
])

# Callback to update the graphs based on selection
@callback(
    [Output('barplot-profession', 'figure'),
     Output('barplot-degree', 'figure'),
     Output('city-depression-map', 'figure'),
     Output('depression-pie', 'figure')],
    [Input('barplot-profession', 'clickData'),
     Input('barplot-degree', 'clickData')]
)
def update_graphs(profession_click, degree_click):
    # If a profession bar is clicked
    if profession_click is not None:
        selected_profession = profession_click['points'][0]['x']
        # Filter the data based on the selected profession
        filtered_degree_data = df[df['Profession'] == selected_profession]
        # Calculate the average Job Satisfaction by Degree for the selected profession
        avg_job_satisfaction_filtered = filtered_degree_data.groupby('Degree')['Job Satisfaction'].mean().reset_index()

        # Update the second graph (Degree vs Job Satisfaction)
        degree_fig = px.bar(avg_job_satisfaction_filtered,
                            x='Degree', y='Job Satisfaction',
                            title=f"Job Satisfaction for {selected_profession}",
                            template="minty",
                            labels={'Degree': 'Degree Category', 'Job Satisfaction': 'Average Job Satisfaction'},
                            color='Degree',
                            color_discrete_sequence=color_palette)
    else:
        # Default graph when no bar is clicked
        degree_fig = px.bar(avg_job_satisfaction_degree,
                            x='Degree', y='Job Satisfaction',
                            title="Job Satisfaction by Degree Category",
                            template="minty",
                            labels={'Degree': 'Degree Category', 'Job Satisfaction': 'Average Job Satisfaction'},
                            color='Degree',
                            color_discrete_sequence=color_palette)

    # If a degree bar is clicked
    if degree_click is not None:
        selected_degree = degree_click['points'][0]['x']
        # Filter the data based on the selected degree
        filtered_profession_data = df[df['Degree'] == selected_degree]
        # Calculate the average Work Pressure by Profession for the selected degree category
        avg_work_pressure_filtered = filtered_profession_data.groupby('Profession')['Work Pressure'].mean().reset_index()

        # Update the first graph (Profession vs Work Pressure)
        profession_fig = px.bar(avg_work_pressure_filtered,
                                x='Profession', y='Work Pressure',
                                title=f"Profession vs Work Pressure for {selected_degree}",
                                template="minty",
                                labels={'Profession': 'Profession', 'Work Pressure': 'Average Work Pressure'},
                                color='Profession',
                                color_discrete_sequence=color_palette)
    else:
        # Default graph when no bar is clicked
        profession_fig = px.bar(avg_work_pressure_profession,
                                x='Profession', y='Work Pressure',
                                title="Profession vs Average Work Pressure",
                                template="minty",
                                labels={'Profession': 'Profession', 'Work Pressure': 'Average Work Pressure'},
                                color='Profession',
                                color_discrete_sequence=color_palette)

    # Update the choropleth map
    map_fig = go.Figure(go.Choropleth(
        z=avg_depression_city['Depression_numeric'],
        hoverinfo='location+z',
        locations=avg_depression_city['City'],
        locationmode='country names',
        colorscale='Viridis',
        colorbar_title="Average Depression Level",
        text=avg_depression_city['City'],
        showscale=True
    ))

    # Update the pie chart (based on the filtered data)
    filtered_df = df
    if profession_click is not None:
        selected_profession = profession_click['points'][0]['x']
        filtered_df = df[df['Profession'] == selected_profession]
    if degree_click is not None:
        selected_degree = degree_click['points'][0]['x']
        filtered_df = df[df['Degree'] == selected_degree]
        
    depressed_count = filtered_df['Depression_numeric'].value_counts().get(1, 0)
    not_depressed_count = filtered_df['Depression_numeric'].value_counts().get(0, 0)
    
    pie_fig = go.Figure(
        go.Pie(
            labels=['Not Depressed', 'Depressed'],
            values=[not_depressed_count, depressed_count],
            title="Depression Percentage",
            hole=0.4,
            marker=dict(colors=['lightgreen', 'lightcoral'])
        )
    )

    return profession_fig, degree_fig, map_fig, pie_fig
