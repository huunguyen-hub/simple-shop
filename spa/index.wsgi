import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/huunguyen/.virtualenvs/pythonProject/lib/python3.9/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/var/www/spa')
sys.path.append('/var/www/spa/spa')

os.environ['DJANGO_SETTINGS_MODULE'] = 'spa.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/huunguyen/.virtualenvs/pythonProject/bin/activate")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()