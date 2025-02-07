import dash 
from dash import dcc, html, Input, Output, clientside_callback, callback
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

load_figure_template(["minty", "minty_dark"])

px.defaults.template = "ggplot2"

external_css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" ]

# Init

app = dash.Dash(__name__, title='Sad Brain Analytical app', use_pages=True, external_stylesheets=external_css)

# app.dash_auth(app, USER_PASS_MAPPING)

server = app.server



app.layout = html.Div(
    [
        # main app framework
        html.Div([
        html.H2("Sad Analytics App", className="text-dark text-center fw-bold fs-1", style={'font-size':20}),
        html.A("Pandemic Impact Monitor Report", href='https://abdessamadtouzani-portfolio.netlify.app/assets/pandemic_impact_exploring.html', target='_blank')
        ]),
        html.Br(),
        html.Div([
            dcc.Link(page['name'], href=page['path'], className="btn btn-dark m-2 fs-5")
            for page in dash.page_registry.values()
        ]),
        html.Br(),


        # content of each page
        dash.page_container
    ], style={
    'width': '1400px',
    'height': '800px',
    'margin-left': 'auto',
    'margin-right': 'auto',
    'margin-top': '50px',
    'margin-bottom': '50px',
    # 'background-color': '#010103',
    'border': '1px solid #cccccc',
    'border-radius': '10px'
}
)

if __name__ == '__main__':
    app.run_server(debug=True)