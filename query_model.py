from databases.databases_model import Databases


class QueryModel:
    def __init__(self, target: str, filtered_query=None, project=None, alias=None):
        self.filter = filtered_query
        self.project = project
        self.alias = alias
        self.target_database = target.split('__')[0]
        self.target_table = target.split('__')[1]
        self.on_result: QueryModel
        self.database = self.get_database()

    def get_database(self):
        if not self.target_database:
            return
        db_found = Databases.objects(database=self.target_database).first()
        if not db_found:
            raise ValueError(f'Database {self.target_database} not found')
        db_found.table = self.target_table
        return db_found.get_connection()
