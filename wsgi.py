import sys
sys.path.append('/srv/www/2lead.in/api/')

from main import app_factory
import config

app = app_factory(config.Prod)