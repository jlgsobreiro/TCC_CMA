class DBInterface:
    connection = None

    def connect(self, *args, **kwargs):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def get_data(self, query=None):
        raise NotImplementedError

    def insert_data(self, query):
        raise NotImplementedError

    def update_data(self, query, data):
        raise NotImplementedError

    def delete_data(self, query):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError

    def delete_data_by_id(self, target_id: str):
        raise NotImplementedError

    def get_data_by_id(self, target_id: str):
        raise NotImplementedError

    def update_data_by_id(self, target_id: str, data: dict):
        raise NotImplementedError