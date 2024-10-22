Consulta Multibanco Aninhada

A proposta deste projeto é demonstrar consultas feitas em diferentes bancos de dados a partir de uma unica requisição json, segue o seguinte exemplo
```
"mongodb__test_db__test": {
  "filter": {"key": "value"},
  "alias" : "mongo",
  "on_result": {
    "redis__0": {
      "filter": {"key": {"mongo": "key"}},
      "alias" : "redis",
      "on_result": {
        "mysql__test_db__test": {
          "filter": {"value": {"redis": "key"}},
          "alias" : "mysql"
        }
      }
    }
  }
}
```

Destrinchando essa request podemos observar a seguinte estrutura
```
"tipo_de_banco__nome_do_banco__tabela": {
  "filter": {"chave": "valor"},
  "alias": "identificador_do_resultado_da_pesquisa",
  "project": ["campo1","campo5"]
  "on_result":{
    "tipo_de_banco__nome_do_banco__tabela": {
      "filter": {"chave": "valor"},
      "alias": "identificador_do_resultado_da_pesquisa"
      "on_result": {...}
    }
  }
}
```

"tipo_de_banco__nome_do_banco__tabela" se separado por "__" pode ser lido como
```
  "tipo_de_banco": Nome do serviço a ser utilizado ("mysql", "mongodb","redis")
  
  "nome_do_banco": Nome da base de dados dentro do serviço
  
  "tabela": Nome da tabela ou coleção a ser utilizada, para o Redis esta é opicional
```

"filter": Recebe um dicionario com chaves e valores explicitos ou um dicionario com referencia à uma consulta feita anteriormente

"alias": Nome da chave que conterá os resultados da consulta, se vazio é utilizado o "tipo_de_banco__nome_do_banco__tabela" como alias

"project": limita a volta dos campos para apenas o presentes na lista

"on_result": Este recebe a mesma estrutura descrita acima para permitir consultar em outros bancos

Para se filtrar é apenas necessario passar a coluna/campo e o valor a ser comparado
```
...
   "filter": {"chave": "valor"}
...
```

Para se utilizar o resultado das pesqisas anteriores é feita da seguinte forma
```
...
  "filter":{"campo1": {"alias":"campo4"}}
...
```
"campo1" recebe uma estrura com a referencia de qual consulta e qual campo quer ser passado como valor

Para se iniciar o projeto utilize o comando
```
make up
```

Para se parar os containers do projeto utilize o comando
```
make down
```

Para executar os testes utilize o comando
```
make tests
```
