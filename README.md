# TCC_CMA - Consulta Multibanco Aninhada

## 📋 Índice
- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API de Consultas](#api-de-consultas)
- [Exemplos](#exemplos)
- [Testes](#testes)
- [Docker](#docker)

---

## 📖 Sobre o Projeto

O **TCC_CMA** (Consulta Multibanco Aninhada) é uma aplicação Flask que permite realizar consultas aninhadas em diferentes bancos de dados (MySQL, MongoDB e Redis) através de uma única requisição JSON. O sistema suporta consultas encadeadas onde o resultado de uma query pode alimentar a próxima, criando um fluxo de dados entre diferentes tipos de bancos.

### Características Principais

- ✅ **Consultas Unificadas**: Execute queries em MySQL, MongoDB e Redis através de uma interface comum
- ✅ **Queries Aninhadas**: Encadeie consultas onde resultados anteriores alimentam filtros de consultas subsequentes
- ✅ **Interface Web**: CRUD completo via interface web para cada tipo de banco
- ✅ **API REST**: Endpoint `/api/query` para integração programática
- ✅ **Docker Support**: Configuração completa com Docker Compose
- ✅ **Padrão de Projeto**: Implementação do padrão Strategy para diferentes bancos

---

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura baseada em interfaces e factory pattern:

```
┌─────────────────┐
│   Flask App     │
│   (app.py)      │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
┌────────▼────────┐  ┌─────▼──────┐  ┌────────▼────────┐
│  QueryModel     │  │ Databases  │  │   Templates     │
│ (query_model.py)│  │  Model     │  │  (CRUD Views)   │
└────────┬────────┘  └─────┬──────┘  └─────────────────┘
         │                 │
         │           ┌─────▼──────────┐
         │           │ DBInterface    │
         │           │  (Interface)   │
         │           └─────┬──────────┘
         │                 │
         │      ┌──────────┼──────────┐
         │      │          │          │
         │  ┌───▼───┐  ┌──▼───┐  ┌───▼────┐
         └──┤ MySQL │  │ Mongo│  │ Redis  │
            │ Model │  │ Model│  │ Model  │
            └───────┘  └──────┘  └────────┘
```

### Componentes Principais

1. **DBInterface**: Interface base para todos os bancos de dados
2. **Databases Model**: Factory que gerencia conexões com diferentes bancos
3. **QueryModel**: Processador de queries aninhadas com suporte a encadeamento
4. **VarsSingleton**: Singleton para compartilhar variáveis entre queries

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.10+**
- **Flask 3.0.3** - Framework web
- **PyMongo 4.8.0** - Driver MongoDB
- **PyMySQL 1.1.1** - Driver MySQL
- **Redis 6.2.0** - Cliente Redis
- **MongoEngine 0.29.0** - ODM para MongoDB

### Bancos de Dados
- **MySQL 8.0.23**
- **MongoDB (latest)**
- **Redis (latest)**

### DevOps
- **Docker & Docker Compose**
- **Pytest** - Framework de testes

---

## 📦 Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose (opcional, para ambiente containerizado)
- pip (gerenciador de pacotes Python)

---

## 🚀 Instalação

### Opção 1: Instalação Local

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd TCC_CMA
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure os bancos de dados** (certifique-se que MySQL, MongoDB e Redis estão rodando)

5. **Execute as fixtures** (dados de teste)
```bash
python fixtures.py
```

6. **Inicie a aplicação**
```bash
python app.py
```

### Opção 2: Usando Docker

1. **Inicie todos os serviços**
```bash
docker-compose up -d
```

Isso iniciará:
- MySQL na porta 3306
- MongoDB na porta 27017
- Redis na porta 6379
- Flask App1 na porta 5000 (MySQL)
- Flask App2 na porta 5001 (MongoDB)
- Flask App3 na porta 5002 (Redis)

---

## ⚙️ Configuração

### Variáveis de Ambiente

Cada instância do Flask pode ser configurada com:

```bash
DB=mysql|mongodb|redis          # Tipo de banco padrão
DB_NAME=nome_do_banco           # Nome do banco
DB_PARAMS=key=value,key2=value2 # Parâmetros de conexão
```

### Exemplo de Configuração (docker-compose.yml)

```yaml
environment:
  - DB=mysql
  - DB_NAME=test_db
  - DB_PARAMS=host=localhost,port=3306,user=root,password=rootpassword
```

---

## 💻 Uso

### Interface Web

Acesse `http://localhost:5000` para a interface principal com:

- **CRUD MySQL**: `/crud/mysql`
- **CRUD MongoDB**: `/crud/mongodb`
- **CRUD Redis**: `/crud/redis`
- **Query Aninhada**: `/query`

### API REST

**Endpoint**: `POST /api/query`

**Content-Type**: `application/json`

---

## 📁 Estrutura do Projeto

```
TCC_CMA/
├── app.py                      # Aplicação Flask principal
├── query_model.py              # Lógica de queries aninhadas
├── fixtures.py                 # Dados de teste/seed
├── requirements.txt            # Dependências Python
├── docker-compose.yml          # Configuração Docker
├── Dockerfile                  # Imagem Docker
├── Makefile                    # Comandos úteis
├── README.md                   # Documentação
│
├── databases/                  # Módulo de bancos de dados
│   ├── database_interface.py  # Interface base
│   ├── databases_model.py     # Factory de conexões
│   ├── mongo_model.py         # Implementação MongoDB
│   ├── mysql_model.py         # Implementação MySQL
│   └── redis_model.py         # Implementação Redis
│
├── templates/                  # Templates HTML
│   ├── index.html             # Lista de itens (CRUD)
│   ├── query.html             # Interface de queries
│   └── update.html            # Formulário de atualização
│
├── static/                     # Arquivos estáticos (CSS/JS)
│
└── tests/                      # Testes unitários
    ├── test_databases_model.py
    ├── test_model_query.py
    ├── test_mongo_model.py
    ├── test_mysql_model.py
    └── test_redis_model.py
```

---

## 🔍 API de Consultas

### Estrutura da Requisição

A proposta deste projeto é demonstrar consultas feitas em diferentes bancos de dados a partir de uma única requisição JSON.

#### Formato Base

```json
{
  "service": "mysql|mongodb|redis",
  "database": "nome_do_banco",
  "schema": "nome_da_tabela",
  "alias": "identificador_unico",
  "filter": {"campo": "valor"},
  "project": ["campo1", "campo2"],
  "on_result": {
    // Query aninhada (mesma estrutura)
  }
}
```

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `service` | string | ✅ | Tipo de banco: `mysql`, `mongodb` ou `redis` |
| `database` | string | ✅ | Nome do banco de dados |
| `schema` | string | ⚠️ | Nome da tabela/coleção (opcional para Redis) |
| `alias` | string | ❌ | Identificador dos resultados (padrão: `service__database__schema`) |
| `filter` | object | ✅ | Critérios de busca |
| `project` | array | ❌ | Campos a retornar (projeção) |
| `on_result` | object | ❌ | Query a executar com os resultados desta |

---

## 📝 Exemplos

### Exemplo 1: Consulta Simples (MongoDB)

```json
{
  "service": "mongodb",
  "database": "test_db",
  "schema": "test",
  "alias": "usuarios",
  "filter": {"status": "ativo"}
}
```

### Exemplo 2: Consulta Aninhada (Multi-banco)

Busca no MongoDB → Usa resultado no Redis → Usa resultado no MySQL

```json
{
  "service": "mongodb",
  "database": "test_db",
  "schema": "test",
  "alias": "mongo",
  "filter": {"key": "value"},
  "on_result": {
    "service": "redis",
    "database": "0",
    "alias": "redis",
    "filter": {"key": {"mongo": "key"}},
    "on_result": {
      "service": "mysql",
      "database": "test_db",
      "schema": "test",
      "alias": "mysql",
      "filter": {"value": {"redis": "key"}}
    }
  }
}
```

### Exemplo 3: Consulta com Projeção

```json
{
  "service": "mongodb",
  "database": "test_db",
  "schema": "usuarios",
  "alias": "users",
  "filter": {"idade": {"$gte": 18}},
  "project": ["nome", "email", "idade"]
}
```

### Exemplo 4: Usando Referências de Queries Anteriores

O sistema permite usar resultados de queries anteriores nos filtros:

```json
{
  "service": "mongodb",
  "database": "test_db",
  "schema": "pedidos",
  "alias": "pedidos",
  "filter": {"status": "pendente"},
  "on_result": {
    "service": "mysql",
    "database": "test_db",
    "schema": "clientes",
    "alias": "clientes",
    "filter": {
      "id": {"pedidos": "cliente_id"}
    }
  }
}
```

**Explicação**: O filtro `{"pedidos": "cliente_id"}` significa "use o valor do campo `cliente_id` dos resultados da query `pedidos`".

---

## 🧪 Testes

Execute os testes unitários:

```bash
pytest tests/
```

Testes disponíveis:
- `test_databases_model.py` - Testa factory de bancos
- `test_model_query.py` - Testa lógica de queries
- `test_mongo_model.py` - Testa operações MongoDB
- `test_mysql_model.py` - Testa operações MySQL
- `test_redis_model.py` - Testa operações Redis

---

## 🐳 Docker

### Serviços Disponíveis

O `docker-compose.yml` configura:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| mysql | 3306 | Banco MySQL 8.0.23 |
| mongodb | 27017 | Banco MongoDB (latest) |
| redis | 6379 | Cache Redis (latest) |
| flask1 | 5000 | App Flask configurado para MySQL |
| flask2 | 5001 | App Flask configurado para MongoDB |
| flask3 | 5002 | App Flask configurado para Redis |

### Comandos Docker Úteis

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir imagens
docker-compose build

# Acessar container
docker exec -it flask_container bash
```

---

## 🔧 Makefile

Se houver um Makefile, comandos úteis podem incluir:

```bash
make install    # Instala dependências
make run        # Executa a aplicação
make test       # Executa testes
make docker     # Inicia Docker Compose
```

---

## 📊 Fluxo de Execução de Queries

1. **Recepção**: A requisição JSON chega no endpoint `/api/query`
2. **Parse**: `QueryModel` interpreta a estrutura da query
3. **Conexão**: `Databases` factory cria a conexão apropriada
4. **Execução**: Query é executada no banco especificado
5. **Armazenamento**: Resultado é salvo no `VarsSingleton` com o alias
6. **Recursão**: Se houver `on_result`, executa query aninhada usando resultados anteriores
7. **Agregação**: Todos os resultados são combinados em um único JSON
8. **Resposta**: JSON consolidado é retornado ao cliente

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC).

---

## 👥 Autores

- **Desenvolvedor Principal** - *Trabalho Inicial* - TCC_CMA

---

## 🆘 Suporte

Para reportar bugs ou solicitar features, abra uma issue no repositório.

---

## 📚 Referências

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
