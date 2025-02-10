import dash 
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

'''
For auth...TODO
import dash_auth 
USER_PASS_MAPPING = {
    "ADMIN":"ADMIN",
    "Developer":"Developer",
    "User":"User"
}
'''

# Load Bootstrap themes and plotly templates
load_figure_template(["minty", "minty_dark"])

px.defaults.template = "ggplot2"

external_css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"]

# Init Dash app
app = dash.Dash(__name__, title='Sad Brain Analytical app', use_pages=True, external_stylesheets=external_css)

# app.dash_auth(app, USER_PASS_MAPPING)

server = app.server

# Layout for the app
app.layout = html.Div(
    [
        # Main app header with navigation
        html.Div([
            html.H2("Sad Analytics App", className="text-dark text-center fw-bold fs-1", style={'font-size': 30}),
            html.A("Pandemic Impact Monitor Report", href='https://abdessamadtouzani-portfolio.netlify.app/assets/pandemic_impact_exploring.html', target='_blank'),
        ], style={
            'text-align': 'center',
            'padding': '20px',
            'background-color': '#f8f9fa',
            'border-bottom': '2px solid #cccccc',
        }),

        # Navigation Links for pages
        html.Div([
            dcc.Link(page['name'], href=page['path'], className="btn btn-dark m-2 fs-5")
            for page in dash.page_registry.values()
        ], style={
            'text-align': 'center',
            'margin-top': '20px',
        }),

        html.Br(),

        # Content Area for individual pages (dash.page_container)
        dash.page_container

    ], style={
        'width': '100%',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top': '50px',
        'padding': '20px',
        'border-radius': '10px',
        'border': '1px solid #cccccc',
        'position': 'relative',
    }
)

if __name__ == '__main__':
    app.run_server(debug=True)
