#!/usr/bin/env python3

"""Точка входа для запуска сервиса к тестовому заданию."""

import logging

from aiohttp import web

import treeviewer
from treeviewer.misc import log, settings

logger = logging.getLogger(__name__)


def create_app():
    """Возвращает экземпляр приложения."""
    return web.Application()


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


def setup_routes(app):
    # TODO: (burov_alexey@mail.ru 5 июн. 2020 г. 15:54:47)
    # Нужен редирект корня на swagger
    app.router.add_get('/tree', handle)


def main():
    """Starts service."""
    settings.init(treeviewer.PROJ_PATH)
    log.setup_root_logger(settings.ENV('LOG_LEVEL'))
    app = create_app()
    setup_routes(app)
    web.run_app(app, host=settings.ENV('APP_HOST'),
                     port=settings.ENV('APP_PORT'))


if __name__ == '__main__':
    main()
