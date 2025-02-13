import dash 
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

# Load Bootstrap themes and Plotly templates
THEMES = ["minty", "minty_dark"]
load_figure_template(THEMES)

px.defaults.template = "minty"  # Default to light mode

# External CSS for Bootstrap and Icons
external_css = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
]

# Init Dash app
app = dash.Dash(__name__, title='Sad Brain Analytics App', use_pages=True, external_stylesheets=external_css, requests_pathname_prefix="/")
server = app.server

# 🔹 Header Section
header = html.Div([
    html.H2("Sad Brain Analytics App 🧠", className="text-dark text-center fw-bold", style={'font-size': 30}),
    html.P("Analyzing the impact of academic stress on mental health.", className="text-secondary text-center"),
    print(dash.page_registry),
    
    # 🔹 Navigation Links (Horizontally Centered)
    html.Div([
        dcc.Link("🏠 Home", href="/", className="btn btn-dark m-2 fs-5"),
        *[dcc.Link(f"📊 {page['name']}", href=page['path'], className="btn btn-outline-dark m-2 fs-5") for page in dash.page_registry.values()]
    ], className="text-center"),
    
], style={
    'text-align': 'center',
    'padding': '20px',
    'background': 'linear-gradient(90deg, #f8f9fa, #e9ecef)',
    'border-bottom': '2px solid #cccccc',
    'margin-bottom': '20px'
})

# 🔹 Main Content Area
content = html.Div( dash.page_container, style={'padding': '20px'})

# 🔹 App Layout (Stacked Layout)
app.layout = html.Div([header, content])

if __name__ == '__main__':
    app.run_server(debug=True)
