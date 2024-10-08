from databases.databases_model import Databases


class QueryModel:
    def __init__(self, target_database, filtered_query=None, project=None, alias=None):
        self.filter = filtered_query
        self.project = project
        self.alias = alias
        self.target_database = target_database
        self.on_result: QueryModel
        self.database = self.get_database()

    def get_database(self):
        if not self.target_database:
            return
        database_name, table_name = self.target_database.split('__')
        db_found = Databases.objects(name=database_name).first()
        return db_found.instantiate()
