"""The module contains http handlers of the app."""

import uuid

import anytree
from aiohttp import web
from sqlalchemy.sql import select
from sqlalchemy.orm import aliased
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy import desc, asc

from treeviewer import db, utils
from treeviewer.misc import settings


async def root(request):
    """Redirect to the swagger api of the service."""
    raise web.HTTPFound(location=settings.ENV('SWAGGER_URL'))


async def show_tree(request):
    """Show the data tree.
    ---
    description: This end-point shows all data tree.
    tags:
    - Render a data tree
    produces:
    - text/plain
    responses:
      200:
        description: Successful operation. Return database output for the given parameters
      400:
        description: No data in the DB. Use POST /tree at first.
    """
    conn = request.app['pg'].acquire()
    async with conn as conn:
        resultproxy = await conn.execute(select([db.Node]))
        nodes = await resultproxy.fetchall()

    if not nodes:
        raise web.HTTPBadRequest(reason='No data in the DB. Use POST /tree at first.')

    # Для наглядности прорисуем дерево с помощью библиотеке anytree
    # И отправим его в ответе.
    anytree_nodes = {}
    anytree_root = anytree.Node('%s (%s)' % (nodes[0]['id'], nodes[0]['title']))
    anytree_nodes[nodes[0]['id']] = anytree_root
    for i, node_data in enumerate(nodes[1:], start=1):
        anytree_nodes[node_data['id']] = anytree.Node(
            '%s (%s)' % (nodes[i]['id'], nodes[i]['title']),
            parent=anytree_nodes[node_data['parent_id']]
        )

    return web.Response(text=str(anytree.RenderTree(anytree_root).by_attr()))


async def find_subtree(request):
    """Find a subtree by id of a node.
    ---
    description: This end-point returns data of subtree by your parameters.
    tags:
    - Find subtree
    produces:
    - text/plain
    parameters:
    - name: root_id
      in: query
      required: false
      type: integer
      description: ID of the node from which the search begins
    - name: sort_fld
      in: query
      required: true
      type: string
      description: Sort field
      enum:
        - id
        - parеnt_id
        - title
        - registered_in
    - name: sort_dir
      in: query
      required: true
      type: string
      description: Sort direction (asc/dsc)
      enum:
        - asc
        - dsc
    - name: depth
      in: query
      required: false
      type: integer
      description: Sample size
      default: 1
      enum: [1, 2, 3, 4, 5]
    responses:
      200:
        description: Successful operation. Return database output for the given parameters
      400:
        description: Invalid request data or there is no data in the DB.
    """

    id_ = request.rel_url.query.get('root_id')
    try:
        uuid.UUID(id_, version=4)
    except ValueError:
        raise web.HTTPBadRequest(reason=f'root_id should be UUID (gotten root_id = {id_}).')

    tbl = db.Node.__table__

    if id_ is None:
        # Найдём корневой узел
        async with request.app['pg'].acquire() as conn:
            resultproxy = await conn.execute(select([db.Node]).where(tbl.c.parent_id == None))
            root_node = await resultproxy.fetchone()
            if not root_node:
                raise web.HTTPBadRequest(reason=f'No node `{id_}` in the DB.')
            id_ = str(root_node['id'])
    else:
        # узел задан, нужно проверить, существует ли он
        async with request.app['pg'].acquire() as conn:
            resultproxy = await conn.execute(select([db.Node]).where(tbl.c.id == id_))
            root_node = await resultproxy.fetchone()
            if not root_node:
                raise web.HTTPBadRequest(reason=f'No node `{id_}` in the DB.')
            id_ = str(root_node['id'])

    Session = sessionmaker()
    engine = request.app['pg']
    Session.configure(bind=engine)
    session = Session()

    # TODO: (burov_alexey@mail.ru 7 июн. 2020 г. 16:22:54)
    # Нужно задавать глубину рекурсии
    included = session.query(
        db.Node
    ).filter(
        db.Node.parent_id == id_
    ).cte(name="included", recursive=True)

    included_alias = aliased(included, name="parent")
    node_alias = aliased(db.Node, name="child")

    included = included.union_all(
        session.query(
            node_alias
        ).filter(
            node_alias.parent_id == included_alias.c.id
        )
    )

    # TODO: (burov_alexey@mail.ru 7 июн. 2020 г. 16:20:20)
    # Здесь добавляется порядок и поле для сортировки
    q = session.query(included).distinct()
    sql = str(q.statement.compile(dialect=postgresql.dialect(),
                                  compile_kwargs={"literal_binds": True}))

    async with request.app['pg'].acquire() as conn:
        resultproxy = await conn.execute(sql)
        nodes = await resultproxy.fetchall()

    # Индескы в стоке: id - 0, parent_id - 1, title - 2, registered_in - 3

    # Для наглядности прорисуем дерево с помощью библиотеке anytree
    # И отправим его в ответе.
    anytree_nodes = {}
    anytree_root = anytree.Node(root_node['id'])
    anytree_nodes[root_node['id']] = anytree_root
    # Отсортируем узлы по дате создания, чтобы в словаре уже были узлы,
    # на которые ссылаются дети
    sorted_nodes = sorted(nodes, key=lambda tup: tup[3])
    for i, node_data in enumerate(sorted_nodes):
        node_name = '%s (%s)' % (sorted_nodes[i][0], sorted_nodes[i][2])
        anytree_nodes[node_data[0]] = anytree.Node(node_name,
            parent=anytree_nodes[node_data[1]]
        )

    return web.Response(text=str(anytree.RenderTree(anytree_root).by_attr()))


async def create_tree(request):
    """Create a tree.
    ---
    description: This end-point creates a data tree (old data will be erased).
    tags:
    - Create tree
    produces:
    - text/plain
    responses:
      200:
        description: Successful operation. Return a tree representation (by "id (title)").
    """
    nodes = await utils.create_tree(request.app['pg'])

    # Для наглядности прорисуем дерево с помощью библиотеке anytree
    # И отправим его в ответе.
    anytree_nodes = {}
    anytree_root = anytree.Node('%s (%s)' % (nodes[0]['id'], nodes[0]['title']))
    anytree_nodes[nodes[0]['id']] = anytree_root
    for i, node_data in enumerate(nodes[1:], start=1):
        anytree_nodes[node_data['id']] = anytree.Node(
            '%s (%s)' % (nodes[i]['id'], nodes[i]['title']),
            parent=anytree_nodes[node_data['parent_id']]
        )

    return web.Response(text=str(anytree.RenderTree(anytree_root).by_attr()))


async def ping(request):
    """Health check.
    ---
    description: This end-point allow to test that service is up.
    tags:
    - Health check
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return "pong" text
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="pong")
