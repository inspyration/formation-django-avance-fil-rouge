# Permet d'utiliser PyMySQL (pur Python) comme pilote « MySQLdb » quand
# DB_ENGINE=mysql, sans dépendre de mysqlclient (qui doit se compiler).
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Charge l'application Celery au démarrage de Django (branche demo/celery).
from .celery import app as celery_app  # noqa: E402

__all__ = ("celery_app",)
