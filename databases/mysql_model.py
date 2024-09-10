import pymysql


class MySQLConnection:
    def __init__(self, host, port, target):
        self.host = host
        self.port = port
        self.table = target
        self.connection = pymysql.connect(host=host,port=port)
