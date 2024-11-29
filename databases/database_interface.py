class DBInterface:
    connection = None

    def connect(self, *args, **kwargs):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def get_data(self, query):
        raise NotImplementedError

    def insert_data(self, query):
        raise NotImplementedError

    def update_data(self, query, data):
        raise NotImplementedError

    def delete_data(self, query):
        raise NotImplementedError