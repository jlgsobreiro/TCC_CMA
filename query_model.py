from databases.databases_model import Databases


class QueryModel:
    def __init__(self, query_request:dict=None, previous_result:dict=None):
        target = list(query_request.keys())[0]
        request = query_request[target]
        target_list = target.split('__')
        self.target_database_type:str = target_list[0]
        self.target_database:str = target_list[1]
        self.target_table:str = target_list[2] if len(target_list) > 2 else None
        self.previous_result = previous_result
        self.filter = request.get('filter')
        if previous_result:
            self.update_filter_from_previous_results_values()
        self.project = request.get('project')
        self.alias = request.get('alias', target)
        self.database = self.get_database()
        self.result = {self.alias: dict(self.filter_query())}
        if previous_result:
            self.result.update(previous_result)
        self.on_result: QueryModel = QueryModel(request.get('on_result'), self.result) if request.get('on_result') else None
        if self.on_result:
            self.result.update(self.on_result.result)

    def get_database(self):
        if not self.target_database_type:
            return
        db_found = Databases.objects(database_type=self.target_database_type, database=self.target_database).first()
        if not db_found:
            raise ValueError(f'{self.target_database_type.capitalize()} database {self.target_database} not found')
        db_found.database = self.target_database
        db_found.table = self.target_table
        return db_found.get_connection()

    def filter_query(self):
        return self.database.filter(self.filter, self.project)

    def update_filter_from_previous_results_values(self):
        if not self.filter:
            return
        for key, value in self.filter.items():
            if type(value) is dict:
                prev_key, prev_field = list(value.items())[0]
                if prev_field is tuple or prev_key is tuple:
                    raise ValueError(f'Key {key} should be a dict with only one key-value pair')
                self.filter[key] = self.previous_result.get(prev_key).get(prev_field)
