"""Utilites."""

import logging
import uuid
from typing import Optional, List

from sqlalchemy.sql import select, insert

from treeviewer import db
from treeviewer.misc import settings

logger = logging.getLogger(__name__)


async def create_tree(engine):
    """Creates a tree in the DB and returns nodes."""
    logger.debug('Create a data tree ...')

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
    async with engine.acquire() as conn:
        await conn.execute(insert(db.Node).values(nodes))

    logger.debug('The data tree has created.')
    return nodes

# async def find_subtree(engine, root: Optional[str]=None, sort_fld='registered_in',
#                        sort_dir='asc', depth: Optional[int]=None) -> List:
#     """Найти поддерево с заданного узла и отсортировать его по заданным критериям.
#
#         root - начальный узел (если не задан, то начинать с корня);
#         sort_fld - поле, по которому нужно отсортировать;
#         sort_dir - направление сортировки;
#         depth - глубина выборки дерева.
#     """
#     if depth is None:
#         # т.е. всё дерево, если это корневой узел
#         depth = settings.ENV.int('TREE_DEPTH')
#
#     select([db.Node])
#
#     conn = engine.acquire()
#     async with conn as conn:
#         resultproxy = await conn.execute(select([db.Node]).order_by(db.Node.registered_in.asc()))
#         nodes = await resultproxy.fetchall()
#
#     if not nodes:
#         return []

