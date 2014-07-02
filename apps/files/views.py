# coding:utf-8

from flask import Blueprint
from flask import render_template, request

from .models import *

app = Blueprint('files', __name__)


@app.route("/")
def index_view():
    pass
