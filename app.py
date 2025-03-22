import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from layouts.home import create_home_layout
from layouts.donor_map import create_donor_map_layout
from layouts.donor_profiles import create_donor_profiles_layout
from layouts.campaign_analysis import create_campaign_analysis_layout
from layouts.donor_retention import create_donor_retention_layout
from layouts.feedback_analysis import create_feedback_analysis_layout
from layouts.health_analysis import create_health_analysis_layout
from layouts.eligibility_prediction import create_eligibility_prediction_layout
from callbacks.donor_map_callbacks import init_donor_map_callbacks
from callbacks.donor_profiles_callbacks import init_donor_profiles_callbacks
from callbacks.campaign_analysis_callbacks import init_campaign_analysis_callbacks
from callbacks.donor_retention_callbacks import init_donor_retention_callbacks
from callbacks.feedback_analysis_callbacks import init_feedback_analysis_callbacks
from callbacks.health_analysis_callbacks import init_health_analysis_callbacks
from callbacks.eligibility_prediction_callbacks import init_eligibility_prediction_callbacks

# Initialisation de l'application Dash avec un thème moderne
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,  
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"  
    ],
    suppress_callback_exceptions=True
)

server = app.server  # Expose le serveur pour Gunicorn

# Sidebar avec style moderne
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src="/assets/blood-drop.png", style={"width": "50px"}),
                html.H2("Don de Sang", className="sidebar-title"),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), "Accueil"],
                    href="/",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-map-marker-alt me-2"), "Cartographie"],
                    href="/cartographie",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-check-circle me-2"), "Prédiction d'Éligibilité"],
                    href="/prediction",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-heartbeat me-2"), "Santé & Éligibilité"],
                    href="/sante",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-users me-2"), "Profils Donneurs"],
                    href="/profils",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-chart-line me-2"), "Analyse Campagnes"],
                    href="/campagnes",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-sync me-2"), "Fidélisation"],
                    href="/fidelisation",
                    active="exact",
                    className="nav-link"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-comments me-2"), "Retours"],
                    href="/retours",
                    active="exact",
                    className="nav-link"
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.P("Campagne 2023", className="campaign-info"),
                html.Div([
                    html.Span("Status: "),
                    html.Span("Active", className="status-active"),
                ], className="status-container"),
            ],
            className="sidebar-footer"
        ),
    ],
    className="sidebar",
)

# Layout principal avec contenu
content = html.Div(id="page-content", className="content")

# Layout général de l'application
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

# Callbacks pour la navigation
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        return create_home_layout()
    elif pathname == "/cartographie":
        return create_donor_map_layout()
    elif pathname == "/prediction":
        return create_eligibility_prediction_layout()
    elif pathname == "/profils":
        return create_donor_profiles_layout()
    elif pathname == "/campagnes":
        return create_campaign_analysis_layout()
    elif pathname == "/fidelisation":
        return create_donor_retention_layout()
    elif pathname == "/retours":
        return create_feedback_analysis_layout()
    elif pathname == "/sante":
        return create_health_analysis_layout()
    
    # Si l'URL n'est pas valide, retourner une page 404
    return html.Div(
        [
            html.H1("404: Page non trouvée", className="text-danger"),
            html.Hr(),
            html.P(f"La page {pathname} n'existe pas..."),
        ],
        className="p-3"
    )

# Initialiser les callbacks
init_donor_map_callbacks(app)
init_donor_profiles_callbacks(app)
init_campaign_analysis_callbacks(app)
init_eligibility_prediction_callbacks(app)
init_donor_retention_callbacks(app)
init_feedback_analysis_callbacks(app)
init_health_analysis_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
