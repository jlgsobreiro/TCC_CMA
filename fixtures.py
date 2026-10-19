from os import getenv
from databases.databases_model import Databases, find_database
from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient


MYSQL_HOST = getenv('MYSQL_HOST', 'localhost')
MONGO_HOST = getenv('MONGO_HOST', 'localhost')
REDIS_HOST = getenv('REDIS_HOST', 'localhost')


def setup_databases():
    Databases.drop_collection()

    # Conexoes originais de teste (test_db / 0)
    db_mysql_test = Databases(
        database_type='mysql',
        database='test_db',
        params={
            'host': MYSQL_HOST,
            'port': 3306,
            'target': 'test',
            'user': 'root',
            'password': 'rootpassword'
        }
    )
    db_mysql_test.save()

    db_redis = Databases(
        database_type='redis',
        database='0',
        params={'host': REDIS_HOST, 'port': 6379}
    )
    db_redis.save()

    db_mongo_test = Databases(
        database_type='mongodb',
        database='test_db',
        params={'host': MONGO_HOST, 'port': 27017, 'target': 'test'}
    )
    db_mongo_test.save()

    # Sistemas do cenario de logistica do TCC (Capitulos 3 e 5)
    # 1. CMS - Client Management System (MySQL)
    db_cms = Databases(
        database_type='mysql',
        database='cms',
        params={
            'host': MYSQL_HOST,
            'port': 3306,
            'target': 'clientes',
            'user': 'root',
            'password': 'rootpassword'
        }
    )
    db_cms.save()

    # 2. SMS - Storage Management System (MySQL)
    db_sms = Databases(
        database_type='mysql',
        database='sms',
        params={
            'host': MYSQL_HOST,
            'port': 3306,
            'target': 'produtos',
            'user': 'root',
            'password': 'rootpassword'
        }
    )
    db_sms.save()

    # 3. FNMS - Financial Management System (MySQL)
    db_fnms = Databases(
        database_type='mysql',
        database='fnms',
        params={
            'host': MYSQL_HOST,
            'port': 3306,
            'target': 'notas_fiscais',
            'user': 'root',
            'password': 'rootpassword'
        }
    )
    db_fnms.save()

    # 4. OMS - Order Management System (MongoDB)
    db_oms = Databases(
        database_type='mongodb',
        database='oms',
        params={'host': MONGO_HOST, 'port': 27017, 'target': 'pedidos'}
    )
    db_oms.save()

    # 5. FMS - Fleet Management System (MongoDB; rastreamento usa Redis db '0')
    db_fms = Databases(
        database_type='mongodb',
        database='fms',
        params={'host': MONGO_HOST, 'port': 27017, 'target': 'rotas'}
    )
    db_fms.save()


def create_mysql_fixtures():
    db1 = find_database({'database_type': 'mysql', 'database': 'test_db'})
    mysql_client: MysqlClient = db1.get_connection()
    with mysql_client.connection as connection:
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
            cursor.execute('USE test_db')
            cursor.execute('DROP TABLE IF EXISTS test')
            cursor.execute('CREATE TABLE IF NOT EXISTS test (id VARCHAR(255), external_id VARCHAR(255))')
        connection.commit()
        mysql_client.insert_data({'id': '1', 'external_id': 'value'})
        mysql_client.insert_data({'id': '2', 'external_id': 'value2'})
        mysql_client.insert_data({'id': '3', 'external_id': 'value3'})


def create_redis_fixtures():
    db2 = find_database({'database_type': 'redis', 'database': '0'})
    redis_client: RedisClient = db2.get_connection()
    redis_client.connection.flushdb()
    redis_client.insert_data({'id': '1', 'external_id': 'value'})
    redis_client.insert_data({'id': '2', 'external_id': 'value2'})
    redis_client.insert_data({'id': '3', 'external_id': 'value3'})


def create_mongo_fixtures():
    db3 = find_database({'database_type': 'mongodb', 'database': 'test_db'})
    mongo_client: MongodbClient = db3.get_connection()
    mongo_client.db.drop_collection('test')
    mongo_client.insert_data({'id': '1', 'external_id': 'value'})
    mongo_client.insert_data({'id': '2', 'external_id': 'value2'})
    mongo_client.insert_data({'id': '3', 'external_id': 'value3'})


def create_cms_fixtures():
    """
    Quadro 2 - Esquema do banco CMS (MySQL):
      - clientes: id, tipo, nome, documento, email, telefone, uf
      - enderecos: id, cliente_id, tipo, logradouro, cidade, uf, cep
      - meios_pagamento: id, cliente_id, token, bandeira, validade
    """
    cms_client = MysqlClient(
        host=MYSQL_HOST,
        port=3306,
        database='cms',
        target='clientes',
        user='root',
        password='rootpassword'
    )
    with cms_client.connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS meios_pagamento')
        cursor.execute('DROP TABLE IF EXISTS enderecos')
        cursor.execute('DROP TABLE IF EXISTS clientes')

        cursor.execute('''
            CREATE TABLE clientes (
                id VARCHAR(50) PRIMARY KEY,
                tipo VARCHAR(10),
                nome VARCHAR(255),
                documento VARCHAR(50),
                email VARCHAR(255),
                telefone VARCHAR(50),
                uf VARCHAR(2)
            )
        ''')
        cursor.execute('''
            CREATE TABLE enderecos (
                id VARCHAR(50) PRIMARY KEY,
                cliente_id VARCHAR(50),
                tipo VARCHAR(50),
                logradouro VARCHAR(255),
                cidade VARCHAR(100),
                uf VARCHAR(2),
                cep VARCHAR(20)
            )
        ''')
        cursor.execute('''
            CREATE TABLE meios_pagamento (
                id VARCHAR(50) PRIMARY KEY,
                cliente_id VARCHAR(50),
                token VARCHAR(100),
                bandeira VARCHAR(50),
                validade VARCHAR(20)
            )
        ''')
    cms_client.connection.commit()

    # Clientes (Casos 1, 4, 5, 6, 9, 11, 13, 14)
    cms_client.table = 'clientes'
    for cliente in [
        {
            'id': '1',
            'tipo': 'PJ',
            'nome': 'Acme Ltda',
            'documento': '12345678000199',
            'email': 'contato@acme.com',
            'telefone': '2199999-0000',
            'uf': 'RJ'
        },
        {
            'id': '2',
            'tipo': 'PJ',
            'nome': 'Beta SA',
            'documento': '98765432000188',
            'email': 'vendas@beta.com',
            'telefone': '2198888-0000',
            'uf': 'RJ'
        },
        {
            'id': '7',
            'tipo': 'PF',
            'nome': 'Carlos Pereira',
            'documento': '11122233344',
            'email': 'carlos@email.com',
            'telefone': '1197777-0000',
            'uf': 'SP'
        }
    ]:
        cms_client.insert_data(cliente)

    # Enderecos (Caso 4)
    cms_client.table = 'enderecos'
    for endereco in [
        {
            'id': 'E-1',
            'cliente_id': '1',
            'tipo': 'ENTREGA',
            'logradouro': 'Av. Rio Branco, 100',
            'cidade': 'Rio de Janeiro',
            'uf': 'RJ',
            'cep': '20040-007'
        },
        {
            'id': 'E-2',
            'cliente_id': '1',
            'tipo': 'FATURAMENTO',
            'logradouro': 'Av. Rio Branco, 100 - Sala 501',
            'cidade': 'Rio de Janeiro',
            'uf': 'RJ',
            'cep': '20040-007'
        },
        {
            'id': 'E-3',
            'cliente_id': '2',
            'tipo': 'ENTREGA',
            'logradouro': 'Rua da Assembleia, 50',
            'cidade': 'Rio de Janeiro',
            'uf': 'RJ',
            'cep': '20011-000'
        },
        {
            'id': 'E-4',
            'cliente_id': '7',
            'tipo': 'ENTREGA',
            'logradouro': 'Av. Paulista, 1000',
            'cidade': 'Sao Paulo',
            'uf': 'SP',
            'cep': '01310-100'
        }
    ]:
        cms_client.insert_data(endereco)

    # Meios de pagamento (Caso 13)
    cms_client.table = 'meios_pagamento'
    for mp in [
        {
            'id': 'MP-1',
            'cliente_id': '1',
            'token': 'tok_9f8a2b',
            'bandeira': 'VISA',
            'validade': '12/2028'
        },
        {
            'id': 'MP-2',
            'cliente_id': '2',
            'token': 'tok_3c4d5e',
            'bandeira': 'MASTERCARD',
            'validade': '08/2027'
        },
        {
            'id': 'MP-3',
            'cliente_id': '7',
            'token': 'tok_7a8b9c',
            'bandeira': 'ELO',
            'validade': '05/2029'
        }
    ]:
        cms_client.insert_data(mp)

    cms_client.disconnect()


def create_sms_fixtures():
    """
    Quadro 4 - Esquema do banco SMS (MySQL):
      - galpoes: id, nome, cidade, uf
      - setores: id, galpao_id, codigo, carga_maxima_kg
      - produtos: id, setor_id, nome, sku, quantidade, validade, peso_kg
    """
    sms_client = MysqlClient(
        host=MYSQL_HOST,
        port=3306,
        database='sms',
        target='galpoes',
        user='root',
        password='rootpassword'
    )
    with sms_client.connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS produtos')
        cursor.execute('DROP TABLE IF EXISTS setores')
        cursor.execute('DROP TABLE IF EXISTS galpoes')

        cursor.execute('''
            CREATE TABLE galpoes (
                id VARCHAR(50) PRIMARY KEY,
                nome VARCHAR(255),
                cidade VARCHAR(100),
                uf VARCHAR(2)
            )
        ''')
        cursor.execute('''
            CREATE TABLE setores (
                id VARCHAR(50) PRIMARY KEY,
                galpao_id VARCHAR(50),
                codigo VARCHAR(50),
                carga_maxima_kg DOUBLE
            )
        ''')
        cursor.execute('''
            CREATE TABLE produtos (
                id VARCHAR(50) PRIMARY KEY,
                setor_id VARCHAR(50),
                nome VARCHAR(255),
                sku VARCHAR(100),
                quantidade INT,
                validade VARCHAR(20),
                peso_kg DOUBLE
            )
        ''')
    sms_client.connection.commit()

    sms_client.table = 'galpoes'
    for galpao in [
        {'id': 'G-1', 'nome': 'Galpao Central RJ', 'cidade': 'Rio de Janeiro', 'uf': 'RJ'},
        {'id': 'G-2', 'nome': 'Galpao Distribuicao SP', 'cidade': 'Sao Paulo', 'uf': 'SP'}
    ]:
        sms_client.insert_data(galpao)

    sms_client.table = 'setores'
    for setor in [
        {'id': 'S-12', 'galpao_id': 'G-1', 'codigo': 'A-04', 'carga_maxima_kg': 5000},
        {'id': 'S-15', 'galpao_id': 'G-1', 'codigo': 'B-02', 'carga_maxima_kg': 3000},
        {'id': 'S-20', 'galpao_id': 'G-2', 'codigo': 'C-01', 'carga_maxima_kg': 8000}
    ]:
        sms_client.insert_data(setor)

    sms_client.table = 'produtos'
    for produto in [
        {
            'id': 'PR-1',
            'setor_id': 'S-15',
            'nome': 'Arroz 5kg',
            'sku': 'SKU-101',
            'quantidade': 150,
            'validade': '2027-03-15',
            'peso_kg': 5.0
        },
        {
            'id': 'PR-2',
            'setor_id': 'S-20',
            'nome': 'Azeite 500ml',
            'sku': 'SKU-202',
            'quantidade': 85,
            'validade': '2027-12-01',
            'peso_kg': 0.5
        },
        {
            'id': 'PR-3',
            'setor_id': 'S-12',
            'nome': 'Cafe 1kg',
            'sku': 'SKU-777',
            'quantidade': 320,
            'validade': '2027-06-30',
            'peso_kg': 1.0
        }
    ]:
        sms_client.insert_data(produto)

    sms_client.disconnect()


def create_fnms_fixtures():
    """
    Quadro 5 - Esquema do banco FNMS (MySQL):
      - notas_fiscais: id, pedido_id, cliente_id, valor_total, data_emissao
      - linhas_nota: id, nota_id, produto_sku, quantidade, valor_unitario
      - cobrancas: id, nota_id, valor, vencimento, status
      - pagamentos: id, cobranca_id, valor_pago, data_pagamento
    """
    fnms_client = MysqlClient(
        host=MYSQL_HOST,
        port=3306,
        database='fnms',
        target='notas_fiscais',
        user='root',
        password='rootpassword'
    )
    with fnms_client.connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS pagamentos')
        cursor.execute('DROP TABLE IF EXISTS cobrancas')
        cursor.execute('DROP TABLE IF EXISTS linhas_nota')
        cursor.execute('DROP TABLE IF EXISTS notas_fiscais')

        cursor.execute('''
            CREATE TABLE notas_fiscais (
                id VARCHAR(50) PRIMARY KEY,
                pedido_id VARCHAR(50),
                cliente_id VARCHAR(50),
                valor_total DOUBLE,
                data_emissao VARCHAR(20)
            )
        ''')
        cursor.execute('''
            CREATE TABLE linhas_nota (
                id VARCHAR(50) PRIMARY KEY,
                nota_id VARCHAR(50),
                produto_sku VARCHAR(100),
                quantidade INT,
                valor_unitario DOUBLE
            )
        ''')
        cursor.execute('''
            CREATE TABLE cobrancas (
                id VARCHAR(50) PRIMARY KEY,
                nota_id VARCHAR(50),
                valor DOUBLE,
                vencimento VARCHAR(20),
                status VARCHAR(50)
            )
        ''')
        cursor.execute('''
            CREATE TABLE pagamentos (
                id VARCHAR(50) PRIMARY KEY,
                cobranca_id VARCHAR(50),
                valor_pago DOUBLE,
                data_pagamento VARCHAR(20)
            )
        ''')
    fnms_client.connection.commit()

    fnms_client.table = 'notas_fiscais'
    for nf in [
        {
            'id': 'NF-900',
            'pedido_id': 'P-100',
            'cliente_id': '1',
            'valor_total': 1580.0,
            'data_emissao': '2026-09-10'
        },
        {
            'id': 'NF-912',
            'pedido_id': 'P-131',
            'cliente_id': '1',
            'valor_total': 240.5,
            'data_emissao': '2026-10-01'
        },
        {
            'id': 'NF-920',
            'pedido_id': 'P-140',
            'cliente_id': '7',
            'valor_total': 99.9,
            'data_emissao': '2026-10-05'
        }
    ]:
        fnms_client.insert_data(nf)

    fnms_client.table = 'linhas_nota'
    for linha in [
        {
            'id': 'LN-1',
            'nota_id': 'NF-900',
            'produto_sku': 'SKU-101',
            'quantidade': 20,
            'valor_unitario': 79.0
        },
        {
            'id': 'LN-2',
            'nota_id': 'NF-912',
            'produto_sku': 'SKU-777',
            'quantidade': 2,
            'valor_unitario': 120.25
        },
        {
            'id': 'LN-3',
            'nota_id': 'NF-920',
            'produto_sku': 'SKU-202',
            'quantidade': 1,
            'valor_unitario': 99.9
        }
    ]:
        fnms_client.insert_data(linha)

    fnms_client.table = 'cobrancas'
    for cobranca in [
        {
            'id': 'CB-1',
            'nota_id': 'NF-900',
            'valor': 1580.0,
            'vencimento': '2026-09-25',
            'status': 'PAGA'
        },
        {
            'id': 'CB-2',
            'nota_id': 'NF-912',
            'valor': 240.5,
            'vencimento': '2026-10-15',
            'status': 'VENCIDA'
        },
        {
            'id': 'CB-3',
            'nota_id': 'NF-920',
            'valor': 99.9,
            'vencimento': '2026-10-20',
            'status': 'ABERTA'
        }
    ]:
        fnms_client.insert_data(cobranca)

    fnms_client.table = 'pagamentos'
    fnms_client.insert_data({
        'id': 'PG-1',
        'cobranca_id': 'CB-1',
        'valor_pago': 1580.0,
        'data_pagamento': '2026-09-24'
    })

    fnms_client.disconnect()


def create_oms_fixtures():
    """
    Quadro 6 - Esquema do banco OMS (MongoDB):
      - pedidos: id, cliente_id, sku, quantidade, itens[], valor_total, status, historico[]
    """
    oms_client = MongodbClient(host=MONGO_HOST, port=27017, database='oms', target='pedidos')
    oms_client.db.drop_collection('pedidos')

    for pedido in [
        {
            'id': 'P-100',
            'cliente_id': '1',
            'sku': 'SKU-101',
            'quantidade': 20,
            'itens': [
                {'sku': 'SKU-101', 'nome': 'Arroz 5kg', 'quantidade': 20, 'valor_unitario': 79.0}
            ],
            'valor_total': 1580.0,
            'status': 'ENTREGUE',
            'historico': [
                {'status': 'CRIADO', 'data': '2026-09-10T09:00:00'},
                {'status': 'ENTREGUE', 'data': '2026-09-12T16:30:00'}
            ]
        },
        {
            'id': 'P-131',
            'cliente_id': '1',
            'sku': 'SKU-777',
            'quantidade': 2,
            'itens': [
                {'sku': 'SKU-777', 'nome': 'Cafe 1kg', 'quantidade': 2, 'valor_unitario': 120.25}
            ],
            'valor_total': 240.5,
            'status': 'EM_ROTA',
            'historico': [
                {'status': 'CRIADO', 'data': '2026-10-01T10:15:00'},
                {'status': 'EM_ROTA', 'data': '2026-10-02T08:00:00'}
            ]
        },
        {
            'id': 'P-140',
            'cliente_id': '7',
            'sku': 'SKU-202',
            'quantidade': 1,
            'itens': [
                {'sku': 'SKU-202', 'nome': 'Azeite 500ml', 'quantidade': 1, 'valor_unitario': 99.9}
            ],
            'valor_total': 99.9,
            'status': 'EM_ROTA',
            'historico': [
                {'status': 'CRIADO', 'data': '2026-10-05T14:20:00'},
                {'status': 'EM_ROTA', 'data': '2026-10-06T07:45:00'}
            ]
        }
    ]:
        oms_client.insert_data(pedido)

    oms_client.disconnect()


def create_fms_fixtures():
    """
    Quadro 3 - Esquema do banco FMS (MongoDB + Redis):
      - rotas (MongoDB fms): id, veiculo_placa, pedido_id, origem, destino, status
      - veiculos (MongoDB fms): id, placa, modelo, capacidade_kg, motorista
      - rastreamento (Redis db 0): chave: placa -> valor: 'lat,long'
    """
    fms_rotas = MongodbClient(host=MONGO_HOST, port=27017, database='fms', target='rotas')
    fms_rotas.db.drop_collection('rotas')
    for rota in [
        {
            'id': 'R-50',
            'pedido_id': 'P-100',
            'veiculo_placa': 'XYZ9K88',
            'origem': 'Galpao Central RJ',
            'destino': 'Niteroi',
            'status': 'CONCLUIDA'
        },
        {
            'id': 'R-55',
            'pedido_id': 'P-131',
            'veiculo_placa': 'ABC1D23',
            'origem': 'Galpao Central RJ',
            'destino': 'Rio de Janeiro',
            'status': 'EM_TRANSITO'
        },
        {
            'id': 'R-60',
            'pedido_id': 'P-140',
            'veiculo_placa': 'DEF4G56',
            'origem': 'Galpao Distribuicao SP',
            'destino': 'Sao Paulo',
            'status': 'EM_TRANSITO'
        }
    ]:
        fms_rotas.insert_data(rota)
    fms_rotas.disconnect()

    fms_veiculos = MongodbClient(host=MONGO_HOST, port=27017, database='fms', target='veiculos')
    fms_veiculos.db.drop_collection('veiculos')
    for veiculo in [
        {
            'id': 'V-1',
            'placa': 'ABC1D23',
            'modelo': 'VUC',
            'capacidade_kg': 3500,
            'motorista': 'Joao Silva'
        },
        {
            'id': 'V-2',
            'placa': 'XYZ9K88',
            'modelo': 'Fiorino',
            'capacidade_kg': 650,
            'motorista': 'Maria Souza'
        },
        {
            'id': 'V-3',
            'placa': 'DEF4G56',
            'modelo': 'Toco',
            'capacidade_kg': 8000,
            'motorista': 'Pedro Santos'
        }
    ]:
        fms_veiculos.insert_data(veiculo)
    fms_veiculos.disconnect()

    redis_client = RedisClient(database=0, host=REDIS_HOST, port=6379)
    for pos in [
        {'id': 'ABC1D23', 'external_id': '-22.9068,-43.1729'},
        {'id': 'XYZ9K88', 'external_id': '-22.8832,-43.1034'},
        {'id': 'DEF4G56', 'external_id': '-23.5505,-46.6333'}
    ]:
        redis_client.insert_data(pos)
    redis_client.disconnect()


def create_fixtures():
    setup_databases()
    create_mysql_fixtures()
    create_redis_fixtures()
    create_mongo_fixtures()
    create_cms_fixtures()
    create_sms_fixtures()
    create_fnms_fixtures()
    create_oms_fixtures()
    create_fms_fixtures()


if __name__ == '__main__':
    create_fixtures()