"""The model of DB data."""

import datetime
import logging
import uuid

import aiopg.sa
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import CreateTable, DropTable

from treeviewer.misc import settings

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

Base = declarative_base()

logger = logging.getLogger(__name__)


class Node(Base):
    __tablename__ = 'node'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('node.id'), nullable=True)
    title = Column(String(length=256), nullable=False)
    registered_in = Column(DateTime, default=datetime.datetime.utcnow)
    children = relationship("Node", cascade="all, delete-orphan",
                                    backref=backref('parent', remote_side=[id]),
                                    collection_class=attribute_mapped_collection('id'))


async def init_engine():
    """Initializes a DB engine, saves and returns one."""
    engine_conf = dict(
        user=settings.ENV('PG_USER'),
        password=settings.ENV('PG_PWD'),
        host=settings.ENV('PG_HOST'),
        port=settings.ENV('PG_PORT'),
        database=settings.ENV('PG_DB'),
    )

    db_url = DSN.format(**engine_conf)
    engine = await aiopg.sa.create_engine(db_url)

    logger.debug('Model engine initialized (engine=%s)', engine)
    engine_conf['password'] = '*' * len(engine_conf['password'])
    logger.debug('PG DB url = %s', DSN.format(**engine_conf))
    return engine


async def create_tables(engine, recreate_if_exists=False):
    """Creates gotten tables."""
    logger.debug('Create tables ...')
    async with engine.acquire() as conn:
        for name, table in Base.metadata.tables.items():
            create_expr = CreateTable(table)
            try:
                await conn.execute(create_expr)
                logger.info('The table `%s` created', name)
            # TODO: (burov_alexey@mail.ru 6 июн. 2020 г. 14:16:35)
            # У меня не получается на ubuntu 16.04 установить libpq-dev, чтобы
            # затем установить psycopg2 (битые зависимости). Поэтому пока общая
            # ошибка. Нужно вернуться, если будет хватать времени.

#             except psycopg2.errors.DuplicateTable as err:
            except Exception as err:
                # см. коммент выше
                if 'psycopg2.errors.DuplicateTable' not in str(err.__class__):
                    # Это какая-то другая ошибка, кидаем её дальше
                    raise err
                logger.info('The table `%s` already exists (err = %s)', name, err)

                if not recreate_if_exists:
                    logger.info('Leave the table `%s` in the old state', name)
                    continue

                # удаляем существующую
                drop_expr = DropTable(table)
                try:
                    await conn.execute(drop_expr)
                    logger.info('The table `%s` deleted' % name)
#                 except psycopg2.ProgrammingError:
                except Exception as err:
                    # см. коммент выше по поводу psycopg2
                    raise err

                # Пробуем создать таблицу. Если ошибка, то пусть идёт дальше
                # и заваливает сервер
                await conn.execute(create_expr)
                logger.info('The table `%s` created', name)


async def close_engine(engine):
    engine.close()
    await engine.wait_closed()
    logger.info(f'PG engine closed')
