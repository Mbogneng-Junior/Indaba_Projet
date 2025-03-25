import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Importer les layouts
from layouts.home_layout import create_home_layout
from layouts.donor_profiles import create_donor_profiles_layout
from layouts.campaign_analysis import create_campaign_analysis_layout
from layouts.health_analysis import create_health_analysis_layout
from layouts.eligibility_prediction import create_eligibility_prediction_layout
from layouts.donor_retention import create_donor_retention_layout
from layouts.feedback_analysis import create_feedback_analysis_layout
from layouts.sidebar import create_sidebar

# Importer les callbacks
from callbacks.home_callbacks import init_home_callbacks
from callbacks.donor_profiles_callbacks import init_donor_profiles_callbacks
from callbacks.campaign_analysis_callbacks import init_campaign_analysis_callbacks
from callbacks.health_analysis_callbacks import init_health_analysis_callbacks
from callbacks.eligibility_prediction_callbacks import init_eligibility_prediction_callbacks
from callbacks.donor_retention_callbacks import init_donor_retention_callbacks
from callbacks.feedback_analysis_callbacks import init_feedback_analysis_callbacks

# Initialiser l'application
app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
                ],
                suppress_callback_exceptions=True)
server = app.server

# Définir le layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour la navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/' or pathname == '':
        # Page d'accueil sans sidebar
        return create_home_layout()
        
    elif pathname == '/profils':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_donor_profiles_layout(),
                className="content-wrapper"
            )
        ])
        
    elif pathname == '/analyse-campagnes':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_campaign_analysis_layout(),
                className="content-wrapper"
            )
        ])
        
    elif pathname == '/analyse-sante':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_health_analysis_layout(),
                className="content-wrapper"
            )
        ])
        
    elif pathname == '/prediction':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_eligibility_prediction_layout(),
                className="content-wrapper"
            )
        ])
        
    elif pathname == '/retention':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_donor_retention_layout(),
                className="content-wrapper"
            )
        ])
        
    elif pathname == '/feedback':
        return html.Div([
            create_sidebar(),
            html.Div(
                create_feedback_analysis_layout(),
                className="content-wrapper"
            )
        ])
    
    # Page 404
    return html.Div([
        html.H1("404: Page non trouvée", className="text-center mt-5")
    ])

# Initialiser les callbacks
init_home_callbacks(app)
init_donor_profiles_callbacks(app)
init_campaign_analysis_callbacks(app)
init_health_analysis_callbacks(app)
init_eligibility_prediction_callbacks(app)
init_donor_retention_callbacks(app)
init_feedback_analysis_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)