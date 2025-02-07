import pandas as pd
import dash
from dash import dcc, html, Input, Output, clientside_callback, callback
import plotly.express as px
import plotly.colors
from dash.dependencies import Input, Output

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

# Define a Bootstrap-like color palette from Plotly
color_palette = plotly.colors.qualitative.Pastel

# Layout with two graphs
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
    
    # Add some space between graphs (optional)
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
])

# Callback to update the graphs based on selection
@callback(
    [Output('barplot-profession', 'figure'),
     Output('barplot-degree', 'figure')],
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

    return profession_fig, degree_fig
