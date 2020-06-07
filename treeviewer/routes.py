"""???"""

from treeviewer import views


def setup_routes(app):
    app.router.add_route('GET', '/', views.root)
    app.router.add_route('GET', '/tree/render', views.show_tree)
    app.router.add_route('GET', '/tree', views.find_subtree)
    app.router.add_route('POST', '/tree', views.create_tree)
    app.router.add_route('GET', '/ping', views.ping)
