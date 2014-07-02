# coding:utf-8

import re
import locale
from jinja2 import evalcontextfilter, Markup, escape
from flask import g

@evalcontextfilter
def nl2br(eval_ctx, value):
    if not value:
        return value
    value = value.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br />')

    if eval_ctx.autoescape:
        value = Markup(value)

    return value

def dateformat(value):
    # TODO :
        # date is UTC, switch to correct timestamp

    if not value:
        return ''

    if g.member.lang == 'fr':
        locale.setlocale( locale.LC_ALL, 'fr_FR.UTF-8' )
        date_format = '%d/%m/%Y'
    else:
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
        date_format = '%m-%d-%Y'

    return value.strftime(date_format)

# @see http://stackoverflow.com/questions/320929/currency-formatting-in-python
def money(value):
    if value is None:
        return ''

    if g.member.lang == 'fr':
        locale.setlocale( locale.LC_ALL, 'fr_FR.UTF-8' )
    else:
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

    return locale.currency(value, grouping=True, symbol=False)