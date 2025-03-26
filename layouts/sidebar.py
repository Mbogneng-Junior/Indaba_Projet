import dash_bootstrap_components as dbc
from dash import html

def create_sidebar():
    """Crée la barre latérale de navigation"""
    return html.Div(
        [
            html.H2("Menu", className="display-4"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-home me-2"),
                            "Accueil"
                        ],
                        href="/",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-users me-2"),
                            "Profils Donneurs"
                        ],
                        href="/profils",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-chart-bar me-2"),
                            "Analyse Campagnes"
                        ],
                        href="/analyse-campagnes",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-heartbeat me-2"),
                            "Analyse Santé "
                        ],
                        href="/analyse-sante",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-check-circle me-2"),
                            "Prédiction Éligibilité"
                        ],
                        href="/prediction",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-sync me-2"),
                            "Rétention Donneurs"
                        ],
                        href="/retention",
                        active="exact",
                        className="nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-comments me-2"),
                            "Analyse Feedback"
                        ],
                        href="/feedback",
                        active="exact",
                        className="nav-link"
                    ),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar",
    )
