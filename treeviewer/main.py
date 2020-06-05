#!/usr/bin/env python3

"""Точка входа для запуска сервиса к тестовому заданию."""

import logging

from aiohttp import web
from aiohttp_swagger import setup_swagger

import treeviewer
from treeviewer import routes
from treeviewer.misc import log, settings

logger = logging.getLogger(__name__)


def create_app():
    """Возвращает экземпляр приложения."""
    return web.Application()


def main():
    """Starts service."""
    settings.init(treeviewer.PROJ_PATH)
    log.setup_root_logger(settings.ENV('LOG_LEVEL'))
    app = create_app()
    routes.setup_routes(app)
    setup_swagger(app, swagger_url=settings.ENV('SWAGGER_URL'), ui_version=2)
    web.run_app(app, host=settings.ENV('APP_HOST'),
                     port=settings.ENV('APP_PORT'))


if __name__ == '__main__':
    main()
