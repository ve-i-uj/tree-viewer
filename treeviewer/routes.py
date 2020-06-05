"""???"""

from treeviewer import views


def setup_routes(app):
    app.router.add_route('GET', '/', views.root)
    app.router.add_route('GET', '/tree', views.tree)
    app.router.add_route('GET', "/ping", views.ping)
