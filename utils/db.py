# coding=utf-8

from sqlalchemy import engine
from sqlalchemy import event
import time
from flask import g

# @see https://gist.github.com/danbirken/10939933

class DbStats():
    def __init__(self):
        self.clear()

    def clear(self):
        self.total_queries = 0
        self.total_time = 0

    def add_query(self, timing):
        self.total_queries += 1
        self.total_time += timing

    def as_dict(self):
        return {
            'total_queries': self.total_queries,
            'total_time_ms': self.total_time * 1000
        }

@event.listens_for(engine.Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters,
                          context, exceutemany):
    context._query_start_time = time.time()

@event.listens_for(engine.Engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters,
                         context, exceutemany):
    g.db_stats.add_query(time.time() - context._query_start_time)