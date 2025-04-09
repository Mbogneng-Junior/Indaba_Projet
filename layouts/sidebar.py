import dash_bootstrap_components as dbc
from dash import html

def create_sidebar():
    """Crée la barre latérale de navigation"""
    return html.Div(
        [
            html.H2("Menu", className="display-4 text-white"),
            html.Hr(className="text-white"),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-home me-2"),
                            "Accueil"
                        ],
                        href="/",
                        active="exact",
                        className="nav-link text-white custom-nav-link"
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-users me-2"),
                            "Profils Donneurs"
                        ],
                        href="/profils",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-chart-bar me-2"),
                            "Analyse Campagnes"
                        ],
                        href="/analyse-campagnes",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-heartbeat me-2"),
                            "Analyse Santé "
                        ],
                        href="/analyse-sante",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-check-circle me-2"),
                            "Prédiction Éligibilité"
                        ],
                        href="/prediction",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-redo me-2"),
                            "Rétention Donneurs"
                        ],
                        href="/retention",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-comments me-2"),
                            "Analyse Feedback"
                        ],
                        href="/feedback",
                        active="exact",
                        className="nav-link text-white",
                        style={"--bs-nav-link-hover-color": "#ff0000"}
                    ),
                ],
                vertical=True,
                pills=True,
                style={
                    "--bs-nav-pills-link-active-bg": "#ff0000",  # Fond rouge pour le lien actif
                    "--bs-nav-pills-link-active-color": "#ffffff"  # Texte blanc pour le lien actif
                }
            ),
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "background": "linear-gradient(135deg, var(--secondary-dark), var(--primary-dark))",  
            "boxShadow": "2px 0px 5px rgba(0,0,0,0.2)"
        },
    )

    #linear-gradient(135deg, var(--secondary-dark), var(--primary-dark));
    #linear-gradient(180deg, #000080 0%, #000000 100%)
