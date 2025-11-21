from django.db.models.expressions import result

from databases.database_interface import DBInterface
from databases.databases_model import Databases

class VarsSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VarsSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'vars'):
            self.vars = {}

    def get(self, key):
        return self.vars.get(key)

    def set(self, key, value):
        self.vars[key] = value

class QueryModel:
    """
    QueryModel é uma classe que recebe um dicionário com a query a ser executada e um dicionário com o resultado da query anterior.
    A query é executada e o resultado é armazenado em self.result.
    Se houver um on_result, a query é executada e o resultado é armazenado em self.on_result.result.

    Parametros:
        query_request: dict

        query_request = {
            "service": "mysql"/"mongodb"/"redis",
            "database": "database_name",
            "schema": "table_name",
            "alias": "alias", # Deve ser único dentre as queries
            "filter": { "field": "value" },
            "project": ["field1", "field2"],
            "on_result": { # Query a ser executada após a query principal, é igual a query_request }

        previous_result: dict

        previous_result = {
            "alias": [ query_result ]
        }

    """
    def __init__(self, query_request:dict=None, previous_result:dict=None):
        self.request: dict = query_request
        self.target_database_type: str = self.request.get('service')
        self.target_database: str = self.request.get('database')
        self.target_table: str = self.request.get('schema') or None
        self.database = None
        self.filter: dict = self.request.get('filter')
        alter_alias = '__'.join([x for x in [self.target_database_type,self.target_database,self.target_table] if x])
        self.alias: str = self.request.get('alias') or alter_alias
        self.project: list = self.request.get('project')
        self.result = None
        self.on_result = self.request.get('on_result')
        self.next_query = None
        self.previous_result = previous_result
        self.vars = VarsSingleton()

    def execute_query(self):
        self.database: DBInterface = self.get_database()

        if self.previous_result:
            self.update_filter_from_previous_results_values()

        self.result = {self.alias: self.filter_query()}
        if self.result:
            self.vars.set(self.alias, self.result)

        if self.previous_result:
            self.result.update(self.previous_result)

        if self.request.get('on_result'):
            self.next_query = []

            # Itera sobre cada item em self.result para executar consultas adicionais
            for item in self.result.get(self.alias, []):
                # Atualiza o filtro da próxima consulta com base no item atual
                next_request = self.request.get('on_result').copy()
                next_request['filter'] = self._update_filter_with_item(next_request.get('filter'), item)

                # Cria uma nova instância de QueryModel para cada item
                next_query = QueryModel(next_request, self.result)
                self.next_query.append(next_query)

            # Executa todas as consultas encadeadas
            for query in self.next_query:
                query.execute_query()
                self.result.update(query.result)

    def _update_filter_with_item(self, filter_dict, item):
        if not filter_dict:
            return {}
        updated_filter = {}
        for itens in filter_dict:
            if isinstance(itens, dict):
                for key, value in itens.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key in item:
                                updated_filter[key] = item[sub_key]
                            else:
                                updated_filter[key] = self.vars.get(sub_key)[sub_key][0][sub_value]
                    else:
                        updated_filter[key] = value
            else:
                updated_filter[itens] = item.get(itens)
        # for key, value in filter_dict.items():
        #     if isinstance(value, dict):
        #         for sub_key, sub_value in value.items():
        #             if sub_key in item:
        #                 updated_filter[key] = item[sub_key]
        #             else:
        #                 updated_filter[key] = sub_value
        #     else:
        #         updated_filter[key] = value
        return updated_filter

    def get_database(self):
        if not self.target_database_type:
            return
        db_found: DBInterface = Databases.objects(database_type=self.target_database_type, database=self.target_database).first()
        if not db_found:
            raise ValueError(f'{self.target_database_type.capitalize()} database {self.target_database} not found')
        db_found.database = self.target_database
        db_found.table = self.target_table
        return db_found.get_connection()

    def filter_query(self):
        if isinstance(self.filter, dict):
            self.filter = [self.filter]
        query_result = self.database.get_data(query=self.filter, project=self.project)
        print(f'Query result: {query_result}')
        return query_result

    def update_filter_from_previous_results_values(self):
        if not self.filter:
            return
        for key, value in self.filter.items():
            if type(value) is dict:
                prev_key, prev_field = list(value.items())[0]
                # if prev_field is tuple or prev_key is tuple:
                #     raise ValueError(f'Key {key} should be a dict with only one key-value pair')
                if type(self.previous_result.get(prev_key)) is list:
                    for result in self.previous_result.get(prev_key):
                        self.filter[key] = result.get(prev_key).get(prev_field)
                else:
                    self.filter[key] = self.previous_result.get(prev_key).get(prev_field)
