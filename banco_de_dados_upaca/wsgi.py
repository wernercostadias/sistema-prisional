import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banco_de_dados_upaca.settings')

application = get_wsgi_application()
