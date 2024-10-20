from databases.databases_model import Databases


class QueryModel:
    def __init__(self, query_request:dict=None, previous_result:dict=None):
        self.previous_result = previous_result
        self.filter = query_request.get('filter')
        if previous_result:
            self.update_filter_from_previous_results_values()
        self.project = query_request.get('project')
        self.target_database = list(query_request.keys())[0].split('__')[0]
        self.target_table = list(query_request.keys())[0].split('__')[1]
        self.alias = query_request.get('alias', list(query_request.keys())[0])
        self.database = self.get_database()
        self.result = self.filter_query()
        passing_result = {self.alias: self.result}
        passing_result.update(previous_result)
        self.on_result: QueryModel = QueryModel(query_request.get('on_result'), passing_result) if query_request.get('on_result') else None

    def get_database(self):
        if not self.target_database:
            return
        db_found = Databases.objects(database=self.target_database).first()
        if not db_found:
            raise ValueError(f'Database {self.target_database} not found')
        db_found.table = self.target_table
        return db_found.get_connection()

    def filter_query(self):
        return self.database.filter_query(self.filter, self.project)

    def update_filter_from_previous_results_values(self):
        if not self.filter:
            return
        for key, value in self.filter.items():
            if value is dict:
                prev_key, prev_field = list(value.items())[0]
                if prev_field is tuple or prev_key is tuple:
                    raise ValueError(f'Key {key} should be a dict with only one key-value pair')
                self.filter[key] = self.previous_result.get(prev_key).get(prev_field)
