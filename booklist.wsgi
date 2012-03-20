import os, sys

sys.stdout = sys.stderr

sys.path.append('/root/project/infxbooklist')
sys.path.append('/root/project')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
