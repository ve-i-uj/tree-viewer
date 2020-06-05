#!/usr/bin/env python3

"""Точка входа для запуска сервиса к тестовому заданию."""

import logging

from aiohttp import web
from aiohttp_swagger import setup_swagger

import treeviewer
from treeviewer.misc import log, settings

logger = logging.getLogger(__name__)


async def root_handler(request):
    """Redirect to the swagger api of the service."""
    raise web.HTTPFound(location=settings.ENV('SWAGGER_URL'))


async def tree_handler(request):
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
        description: Successful operation. Returns database output for the given parameters
      400:
        description: Invalid request data
    """
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def ping_handler(request):
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


def create_app():
    """Возвращает экземпляр приложения."""
    return web.Application()


def setup_routes(app):
    app.router.add_route('GET', '/', root_handler)
    app.router.add_route('GET', '/tree', tree_handler)
    app.router.add_route('GET', "/ping", ping_handler)


def main():
    """Starts service."""
    settings.init(treeviewer.PROJ_PATH)
    log.setup_root_logger(settings.ENV('LOG_LEVEL'))
    app = create_app()
    setup_routes(app)
    setup_swagger(app, swagger_url=settings.ENV('SWAGGER_URL'), ui_version=2)
    web.run_app(app, host=settings.ENV('APP_HOST'),
                     port=settings.ENV('APP_PORT'))


if __name__ == '__main__':
    main()
