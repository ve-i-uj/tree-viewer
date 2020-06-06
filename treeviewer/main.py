#!/usr/bin/env python3

"""The entry point to start the service for the test task."""

import logging

from aiohttp import web
from aiohttp_swagger import setup_swagger

import treeviewer
from treeviewer import routes, db
from treeviewer.misc import log, settings

logger = logging.getLogger(__name__)


async def on_startup_postgresql(app):
    """Creates engine connection to uapi DB and confugures DB tables."""
    engine = await db.init_engine()
    recreate_if_exists = settings.ENV('CLEAN_DB_ON_STARTUP') == 'true'
    await db.create_tables(engine, recreate_if_exists)
    app['pg'] = engine
    logger.debug('Tables initialized ...')


async def on_shutdown_postgresql(app):
    await db.close_engine(app['pg'])


def create_app():
    """Returns an instance of the application."""
    app = web.Application()

    app.on_startup.append(on_startup_postgresql)
    app.on_shutdown.append(on_shutdown_postgresql)

    return app


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
