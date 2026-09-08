# Permet d'utiliser PyMySQL (pur Python) comme pilote « MySQLdb » quand
# DB_ENGINE=mysql, sans dépendre de mysqlclient (qui doit se compiler).
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
