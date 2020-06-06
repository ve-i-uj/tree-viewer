"""The module contains http handlers of the app."""

import uuid
from typing import List

import anytree
from aiohttp import web
from sqlalchemy.sql import select, insert

from treeviewer import db
from treeviewer.misc import settings


async def root(request):
    """Redirect to the swagger api of the service."""
    raise web.HTTPFound(location=settings.ENV('SWAGGER_URL'))


async def show_tree(request):
    """Show tree.
    ---
    description: This end-point shows a data tree by your parameters.
    tags:
    - Show tree
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
        description: Invalid request data
    """
    conn = request.app['pg'].acquire()
    async with conn as conn:
        resultproxy = await conn.execute(select([db.Node]).order_by(db.Node.registered_in.asc()))
        nodes = await resultproxy.fetchall()

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


async def create_tree(request):
    """Create tree.
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

    def add_children(root: db.Node, child_level: int, accum: List):
        """Рекурсивная функция для создания узлов дерева."""
        # берем корневой узел и добавляем ему потомков
        parent_id = root['id']
        for i in range(settings.ENV.int('TREE_CHILDREN_NUMBER')):
            child = dict(id=uuid.uuid4(), parent_id=parent_id,
                         title=f'{root["title"]}/{i}')
            accum.append(child)

            if child_level < settings.ENV.int('TREE_DEPTH') - 1:
                # не дошли до листа дерева, добавим текущему дочернему узлу детей
                add_children(child, child_level + 1, accum)

    root = dict(id=uuid.uuid4(), parent_id=None, title='0')
    nodes = [root]

    add_children(root, child_level=1, accum=nodes)
    async with request.app['pg'].acquire() as conn:
        await conn.execute(insert(db.Node).values(nodes))

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
