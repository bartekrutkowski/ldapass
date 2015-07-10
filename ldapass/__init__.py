# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)
app.secret_key = '42'
from . import ldapass


__version__ = '0.1'