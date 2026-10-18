# Documentação Técnica — TCC_CMA (Consulta Multibanco Aninhada)

> Documentação técnica detalhada do projeto, complementar ao [README.md](README.md).
> Enquanto o `README.md` é voltado ao uso geral (instalação e exemplos), este documento
> aprofunda a arquitetura interna, o motor de consultas, o fluxo de dados, os contratos
> de cada módulo, os testes e as observações/limitações identificadas no código-fonte.

## Índice

- [1. Visão Geral](#1-visão-geral)
- [2. Arquitetura](#2-arquitetura)
- [3. Estrutura de Diretórios](#3-estrutura-de-diretórios)
- [4. Módulos e Componentes](#4-módulos-e-componentes)
  - [4.1 app.py — Camada Web/API](#41-apppy--camada-webapi)
  - [4.2 utils.py — Funções auxiliares](#42-utilspy--funções-auxiliares)
  - [4.3 query_model.py — Motor de Consultas](#43-query_modelpy--motor-de-consultas)
  - [4.4 databases/ — Abstração de Bancos](#44-databases--abstração-de-bancos)
  - [4.5 fixtures.py — Dados de Teste](#45-fixturespy--dados-de-teste)
  - [4.6 templates/ — Interface Web](#46-templates--interface-web)
- [5. O Motor de Consultas Aninhadas](#5-o-motor-de-consultas-aninhadas)
- [6. Referência da API](#6-referência-da-api)
- [7. Rotas Web (CRUD)](#7-rotas-web-crud)
- [8. Configuração e Ambiente](#8-configuração-e-ambiente)
- [9. Execução e Deploy](#9-execução-e-deploy)
- [10. Testes](#10-testes)
- [11. Observações, Limitações e Riscos](#11-observações-limitações-e-riscos)

---

## 1. Visão Geral

O **TCC_CMA** é uma aplicação **Flask** que permite executar **consultas encadeadas
entre bancos de dados heterogêneos** (MySQL, MongoDB e Redis) a partir de uma única
requisição JSON. O diferencial do projeto é o campo `on_result`: o resultado de uma
consulta pode ser injetado como filtro da próxima consulta, mesmo que ela seja executada
em um banco de dados de tipo diferente.

O sistema oferece três formas de interação:

1. **API REST** (`POST /api/query`) — para integração programática.
2. **Interface web de consulta** (`/query`) — formulário para submeter queries JSON.
3. **CRUD web** (`/crud/<tipo>`) — gerenciamento básico de registros por tipo de banco.

Padrões de projeto empregados:

- **Strategy / Interface comum** (`DBInterface`) — cada banco implementa o mesmo contrato.
- **Factory** (`Databases.get_connection`) — instancia o cliente correto por tipo.
- **Singleton** (`VarsSingleton`) — compartilha resultados intermediários entre as etapas
  de uma consulta aninhada.

---

## 2. Arquitetura

```
                          Requisição HTTP (JSON)
                                   │
                          ┌────────▼────────┐
                          │    app.py       │  Rotas Flask
                          │  (Flask App)    │  /  /crud  /query  /api/query
                          └────────┬────────┘
                                   │  prossess_query_request()
                          ┌────────▼────────┐
                          │    utils.py     │  Factories de conexão + parsing
                          └────────┬────────┘
                                   │
                 ┌─────────────────┼──────────────────┐
                 │                                     │
        ┌────────▼─────────┐                 ┌─────────▼─────────┐
        │  query_model.py  │                 │ databases_model.py│
        │   QueryModel     │◄────────────────┤   Databases       │ (Factory + MongoEngine)
        │  VarsSingleton   │  get_connection │                   │
        └────────┬─────────┘                 └─────────┬─────────┘
                 │                                      │
                 │                          ┌───────────┼───────────┐
                 │                          │           │           │
                 │                    ┌─────▼────┐ ┌────▼────┐ ┌────▼─────┐
                 │                    │  Mysql   │ │ Mongodb │ │  Redis   │
                 └────── executa ────►│  Client  │ │ Client  │ │  Client  │  (DBInterface)
                                      └──────────┘ └─────────┘ └──────────┘
                                           │            │           │
                                       ┌───▼───┐   ┌────▼───┐   ┌───▼───┐
                                       │ MySQL │   │ Mongo  │   │ Redis │
                                       └───────┘   └────────┘   └───────┘
```

Observação importante: o registro/descoberta das conexões (`Databases`) é persistido em
um banco MongoDB chamado `databases` via **MongoEngine** (`connect('databases')` em
`databases_model.py`). Ou seja, o MongoDB é usado tanto como banco de dados de aplicação
quanto como catálogo de conexões disponíveis.

---

## 3. Estrutura de Diretórios

```
TCC_CMA/
├── app.py                      # Rotas Flask (web + API)
├── utils.py                    # Factories de conexão e processamento de query
├── query_model.py              # QueryModel (motor recursivo) + VarsSingleton
├── fixtures.py                 # Seed de conexões e dados de teste
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Imagem base (python:3.12-alpine)
├── docker-compose.yml          # 3 bancos + 3 instâncias Flask
├── Makefile                    # Atalhos: up / down / test
├── README.md                   # Documentação de uso
├── DOCUMENTATION.md            # Este documento (documentação técnica)
│
├── databases/
│   ├── database_interface.py   # Contrato base (DBInterface)
│   ├── databases_model.py      # Factory + catálogo de conexões (MongoEngine)
│   ├── mysql_model.py          # Cliente MySQL (PyMySQL)
│   ├── mongo_model.py          # Cliente MongoDB (PyMongo)
│   └── redis_model.py          # Cliente Redis (redis-py)
│
├── templates/
│   ├── index.html              # Listagem/CRUD de itens
│   ├── query.html              # Formulário de consulta JSON
│   └── update.html             # Formulário de atualização
│
├── static/                     # Arquivos estáticos (CSS/JS)
│
└── tests/
    ├── test_databases_model.py # Testa a factory de conexões
    ├── test_model_query.py     # Testa o motor de queries (simples e aninhadas)
    ├── test_mongo_model.py     # Testa o cliente MongoDB
    ├── test_mysql_model.py     # Testa o cliente MySQL
    └── test_redis_model.py     # Testa o cliente Redis
```

---

## 4. Módulos e Componentes

### 4.1 app.py — Camada Web/API

Define a aplicação Flask e todas as rotas. Delega o processamento a `utils.py`.

| Rota | Métodos | Função | Descrição |
|------|---------|--------|-----------|
| `/` | GET | `index` | Lista itens usando a conexão padrão (variáveis de ambiente `DB`, `DB_NAME`, `DB_PARAMS`). |
| `/crud/<database_type>` | GET | `crud_database` | Lista itens do banco do tipo informado. |
| `/crud/<database_type>` | POST | `add_item_by_type` | Insere item (`id`, `external_id`) via formulário. |
| `/crud/<database_type>/<target_id>` | DELETE | `delete_item_by_type` | Remove item por id. |
| `/crud/<database_type>/<target_id>` | GET/POST | `update_item_by_type` | GET renderiza o formulário; POST persiste a atualização. |
| `/query` | GET/POST | `query_data` | Interface web para consultas JSON aninhadas. |
| `/api/query` | GET/POST | `api_query_data` | API REST para consultas aninhadas. |

A aplicação sobe com `app.run(host='0.0.0.0')` (porta padrão 5000).

### 4.2 utils.py — Funções auxiliares

- `convert_objectid(obj)`: converte recursivamente `ObjectId` (BSON/Mongo) para `str`,
  tornando o resultado serializável em JSON.
- `itens_for_template(conn, database_type)`: obtém os itens para as views; para Redis,
  normaliza o campo `value` em `external_id`.
- `get_default_connection(...)`: cria a conexão padrão a partir das variáveis de ambiente
  `DB`, `DB_NAME` e `DB_PARAMS` (string `chave=valor,chave2=valor2`).
- `get_connection_by_type(database_type)`: cria a conexão com parâmetros **hardcoded**
  (`localhost` + credenciais padrão) para cada tipo — usado pelas rotas de CRUD.
- `prossess_query_request(request_dict)`: ponto de entrada do motor de consulta —
  instancia `QueryModel`, executa e retorna o resultado já serializável.

### 4.3 query_model.py — Motor de Consultas

Contém as duas peças centrais:

**`VarsSingleton`** — Singleton (via `__new__`) que mantém um dicionário `vars` global,
usado para guardar os resultados de cada etapa indexados por `alias`, permitindo que
etapas posteriores referenciem resultados anteriores.

**`QueryModel`** — Recebe um `query_request` (dict) e, opcionalmente, `previous_result`.
Principais atributos derivados da requisição:

| Atributo | Origem | Descrição |
|----------|--------|-----------|
| `target_database_type` | `service` | Tipo do banco (`mysql`/`mongodb`/`redis`). |
| `target_database` | `database` | Nome do banco / índice Redis. |
| `target_table` | `schema` | Tabela/coleção (opcional em Redis). |
| `filter` | `filter` | Critério de busca. |
| `alias` | `alias` ou `service__database__schema` | Chave dos resultados. |
| `project` | `project` | Campos a retornar (projeção). |
| `on_result` | `on_result` | Query encadeada a ser executada com os resultados. |

Métodos principais: `execute_query`, `get_database`, `filter_query`,
`update_filter_from_previous_results_values` e `_update_filter_with_item`.
O fluxo detalhado está na [seção 5](#5-o-motor-de-consultas-aninhadas).

### 4.4 databases/ — Abstração de Bancos

**`database_interface.py` (`DBInterface`)** — Contrato base. Métodos esperados:
`connect`, `disconnect`, `get_data`, `insert_data`, `update_data`, `delete_data`,
`get_all`, `delete_data_by_id`, `get_data_by_id`, `update_data_by_id`. A implementação
padrão lança `NotImplementedError`.

**`databases_model.py` (`Databases`)** — É um `Document` do MongoEngine com campos
`database_type`, `database` e `params`. Funciona como catálogo (persistido no MongoDB
`databases`) e como **Factory**: `get_connection()` mapeia o tipo para o cliente correto
(`MysqlClient`, `MongodbClient`, `RedisClient`) e o instancia com `**params`. A função
utilitária `find_database(params)` busca uma conexão registrada.

**`mysql_model.py` (`MysqlClient`)** — Cliente via **PyMySQL**. Constrói SQL dinâmico:
`get_data` monta uma ou mais consultas `SELECT ... WHERE ...` unidas por `UNION`;
suporta `project` (lista de colunas). Também implementa insert/update/delete e as
variantes `*_by_id`. O bloco `__main__` contém um teste manual de sanidade.

**`mongo_model.py` (`MongodbClient`)** — Cliente via **PyMongo**. `get_data` aceita
`query` (lista de filtros dict, com suporte a sub-listas) e retorna documentos; oferece
`filter` com projeção, além das operações CRUD e `*_by_id` (por `ObjectId`).

**`redis_model.py` (`RedisClient`)** — Cliente via **redis-py**. Modela dados como pares
chave/valor: `get_data` sem filtro lista todas as chaves; com filtro, resolve o valor da
chave informada. `insert_data` usa `id`→chave e `external_id`→valor. Trata erros de
conexão/operação com blocos `try/except` retornando listas/dicts.

### 4.5 fixtures.py — Dados de Teste

- `setup_databases()`: limpa o catálogo (`Databases.drop_collection()`) e registra três
  conexões (MySQL, Redis, MongoDB).
- `create_mysql_fixtures()`: cria `test_db.test (id, external_id)` e insere 3 linhas.
- `create_redis_fixtures()`: insere 3 pares chave/valor.
- `create_mongo_fixtures()`: insere 3 documentos na coleção `test`.
- `create_fixtures()`: orquestra todos os passos acima (executado no `__main__`).

### 4.6 templates/ — Interface Web

- `index.html`: formulário de adição + lista de itens com ações Update/Delete
  (Delete usa `fetch` com método `DELETE` via JavaScript).
- `query.html`: textarea com uma query JSON de exemplo (Mongo → Redis → MySQL) e área de
  resultado.
- `update.html`: formulário de edição de um item.

---

## 5. O Motor de Consultas Aninhadas

Este é o núcleo do projeto. O método `QueryModel.execute_query()` executa os seguintes
passos:

1. **Resolve a conexão** (`get_database`): busca no catálogo `Databases` uma entrada com
   o `service`/`database` pedidos e obtém o cliente concreto via factory. Se não existir,
   lança `ValueError`.
2. **Atualiza o filtro com resultados anteriores** (`update_filter_from_previous_results_values`):
   quando há `previous_result`, valores do filtro no formato `{"alias_anterior": "campo"}`
   são substituídos pelo valor real vindo daquela etapa.
3. **Executa a consulta** (`filter_query`): normaliza o filtro para lista e chama
   `get_data(query=..., project=...)` do cliente. O resultado é guardado em
   `self.result[alias]` e também no `VarsSingleton` sob o mesmo `alias`.
4. **Encadeia (`on_result`)**: se houver `on_result`, para **cada item** do resultado
   atual, cria uma nova `QueryModel` cujo filtro é derivado do item corrente
   (`_update_filter_with_item`), executa-a e mescla o resultado em `self.result`.
5. **Agrega**: ao final, `self.result` contém um dicionário com uma chave por `alias`,
   reunindo os resultados de todas as etapas.

### Sintaxe de referência entre etapas

Dentro de um `filter`, um valor no formato:

```json
{ "campo_destino": { "alias_origem": "campo_origem" } }
```

significa: "use, como valor de `campo_destino`, o valor de `campo_origem` presente nos
resultados da etapa `alias_origem`". Quando o `alias` não é informado, ele é gerado
automaticamente como `service__database__schema` (ex.: `mysql__test_db__test`).

### Exemplo (encadeamento Mongo → Redis → MySQL)

```json
{
  "service": "mongodb",
  "database": "test_db",
  "schema": "test",
  "alias": "mongodb",
  "filter": [{"key": "value"}],
  "on_result": {
    "service": "redis",
    "database": "0",
    "alias": "redis",
    "filter": [{"id": {"mongodb": "key"}}],
    "on_result": {
      "service": "mysql",
      "database": "test_db",
      "schema": "test",
      "alias": "mysql",
      "filter": [{"id": {"redis": "value"}}]
    }
  }
}
```

Resultado consolidado (formato):

```json
{
  "mongodb": [ { "...": "..." } ],
  "redis":   [ { "id": "...", "value": "..." } ],
  "mysql":   [ { "id": "...", "value": "..." } ]
}
```

---

## 6. Referência da API

### `POST /api/query`

- **Content-Type**: `application/json`
- **Corpo**: objeto de consulta (vide estrutura abaixo).
- **Resposta (sucesso)**: `{"result": { <alias>: [ ... ], ... }}`
- **Resposta (erro de JSON)**: `{"error": "Invalid JSON query: ..."}` com status `400`.
- **Método inválido**: `{"error": "Invalid request method"}` com status `400`.

### Estrutura do objeto de consulta

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `service` | string | Sim | `mysql`, `mongodb` ou `redis`. |
| `database` | string | Sim | Nome do banco (ou índice Redis, ex.: `"0"`). |
| `schema` | string | Condicional | Tabela/coleção (não usado em Redis). |
| `alias` | string | Não | Identificador dos resultados; padrão `service__database__schema`. |
| `filter` | objeto \| lista | Sim | Critérios de busca (aceita referências a etapas anteriores). |
| `project` | lista | Não | Campos a retornar (projeção). |
| `on_result` | objeto | Não | Query encadeada com a mesma estrutura. |

### Exemplo de chamada

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"service":"mongodb","database":"test_db","schema":"test","filter":[{"id":"1"}]}'
```

---

## 7. Rotas Web (CRUD)

As rotas `/crud/<database_type>` fornecem operações básicas por tipo de banco usando
parâmetros de conexão **fixos** (`localhost`), definidos em `get_connection_by_type`:

- **MongoDB**: `test_db`, `localhost:27017`, coleção `test`.
- **MySQL**: `test_db`, `localhost:3306`, usuário `root` / senha `rootpassword`.
- **Redis**: índice `0`, `localhost:6379`.

Cada item possui `id` e `external_id`. As telas usam os templates da pasta `templates/`.

---

## 8. Configuração e Ambiente

Variáveis de ambiente (usadas por `get_default_connection`, rota `/`):

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `DB` | `mysql` | Tipo de banco padrão. |
| `DB_NAME` | `test_db` | Nome do banco padrão. |
| `DB_PARAMS` | `host=localhost,port=3306,user=root,password=rootpassword` | Parâmetros de conexão (pares `chave=valor` separados por vírgula). |

Dependências principais (`requirements.txt`): `Flask~=3.0.3`, `pymongo~=4.8.0`,
`PyMySQL~=1.1.1`, `mongoengine~=0.29.0`, `redis~=6.2.0` (mais `setuptools`, `wheel`,
`Booktype`).

---

## 9. Execução e Deploy

### Local

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python fixtures.py             # popula catálogo e dados de teste
python app.py                  # sobe em http://localhost:5000
```

### Docker Compose

`docker-compose.yml` sobe seis serviços:

| Serviço | Porta | Configuração |
|---------|-------|--------------|
| `mysql` | 3306 | `mysql:8.0.23`, senha root `rootpassword`. |
| `mongodb` | 27017 | `mongo:latest`. |
| `redis` | 6379 | `redis:latest`. |
| `flask1` | 5000 | `DB=mysql`. |
| `flask2` | 5001 | `DB=mongodb`. |
| `flask3` | 5002 | `DB=redis`. |

Atalhos do `Makefile`:

```bash
make up      # docker compose up -d
make down    # docker compose down
make test    # python3 -m unittest discover -s tests
```

O `Dockerfile` usa `python:3.12-alpine`, instala as dependências e executa `python app.py`
expondo a porta 5000.

---

## 10. Testes

Os testes usam `unittest` e dependem de instâncias reais de MySQL, MongoDB e Redis
acessíveis em `localhost` (não há mocks). O `setUp` de cada suíte recria o catálogo via
`setup_databases()` e limpa as tabelas/coleções/índices.

- `test_databases_model.py`: valida que a factory retorna o cliente correto por tipo.
- `test_model_query.py`: cobre queries simples e aninhadas em todas as combinações de
  bancos (Mongo/Redis/MySQL), com e sem `alias` e `project`. É a suíte mais abrangente.
- `test_mysql_model.py`, `test_mongo_model.py`, `test_redis_model.py`: testam cada cliente
  isoladamente.

Execução:

```bash
python -m unittest discover -s tests
# ou
pytest tests/
```

> Como os testes exigem bancos reais em `localhost`, o caminho recomendado é subir os
> serviços com Docker (`make up`) antes de rodá-los.

---

## 11. Observações, Limitações e Riscos

Pontos identificados na leitura do código-fonte que merecem atenção (úteis para
manutenção e evolução do TCC):

1. **Import de Django não declarado**: `query_model.py` inicia com
   `from django.db.models.expressions import result`. Django **não** está em
   `requirements.txt` e esse import não é utilizado — é um resíduo que pode quebrar a
   importação do módulo em ambientes sem Django. Recomenda-se remover.
2. **`DB_PARAMS` com `localhost` no Docker**: no `docker-compose.yml`, as instâncias
   Flask usam `host=localhost` nos parâmetros, mas os bancos estão em outros containers.
   Entre containers o host correto seria o nome do serviço (`mysql`, `mongodb`, `redis`).
   Além disso, as rotas de CRUD (`get_connection_by_type`) também assumem `localhost`.
3. **SQL construído por concatenação de strings** (`mysql_model.py`): as consultas são
   montadas via f-strings sem parametrização, o que é vulnerável a **SQL injection**.
   Para produção, usar parâmetros de query do PyMySQL.
4. **Credenciais hardcoded**: senha `rootpassword` aparece em código, fixtures e compose.
5. **Acoplamento a bancos reais nos testes**: não há mocks; a suíte precisa de MySQL,
   MongoDB e Redis ativos, o que dificulta CI isolado.
6. **`VarsSingleton` global**: por ser singleton, o estado de `vars` persiste entre
   requisições no mesmo processo, podendo causar vazamento de dados entre consultas
   concorrentes. Ideal isolar o contexto por requisição.
7. **Erro de digitação no nome da função**: `prossess_query_request` (deveria ser
   `process_...`) — mantido por compatibilidade, mas convém padronizar.
8. **Tratamento de erros parcial**: as rotas capturam apenas `json.JSONDecodeError`;
   falhas de banco (`ValueError`, exceções de driver) não são tratadas nas rotas e
   podem retornar erro 500 genérico.

> Essas observações são recomendações de melhoria; o comportamento atual do sistema
> corresponde ao descrito nas seções anteriores.
