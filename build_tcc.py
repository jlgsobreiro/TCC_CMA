# -*- coding: utf-8 -*-
"""
Gerador do TCC expandido (>= 50 paginas) para o projeto TCC_CMA.

Reproduz o conteudo original, incorpora as imagens ja existentes e adiciona
dois capitulos novos e extensos:
  - Guia do Usuario (instalacao, execucao, interface web, API, DSL de consultas)
  - Casos de Uso e Consultas Cross-Database (associando CMS/Clientes com
    Logistica/FMS/OMS, financeiro, estoque, etc.)

Uso:
    python build_tcc.py
Gera: TCC_SOBREIRO_EXPANDIDO.docx
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(
    BASE, ".output", "TCC_SOBREIRO_FORMATADO_5(1)_-1883fbb7_media"
)


def img(n):
    return os.path.join(MEDIA, "img-%04d.png" % n)


doc = Document()

# ---------------------------------------------------------------------------
# Estilos base (ABNT aproximado): Times New Roman 12, espacamento 1.5, justif.
# ---------------------------------------------------------------------------
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
normal.paragraph_format.space_after = Pt(6)

for i in range(1, 5):
    st = doc.styles["Heading %d" % i]
    st.font.name = "Times New Roman"
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.font.bold = True
    st.font.size = Pt(14 - (i - 1))

sec = doc.sections[0]
sec.top_margin = Cm(3)
sec.bottom_margin = Cm(2)
sec.left_margin = Cm(3)
sec.right_margin = Cm(2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def h(text, level=1):
    p = doc.add_heading(text, level=level)
    return p


def para(text, align="justify", bold=False, italic=False, size=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def numbered(text):
    p = doc.add_paragraph(style="List Number")
    p.add_run(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def _shade(cell_or_par, color="F2F2F2"):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    return shd


def code(text, caption=None):
    """Bloco de codigo/JSON em tabela sombreada monoespacada."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    cell._tc.get_or_add_tcPr().append(_shade(cell, "F4F4F4"))
    first = True
    for line in text.strip("\n").split("\n"):
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
    if caption:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc = cap.add_run(caption)
        rc.italic = True
        rc.font.size = Pt(10)
    doc.add_paragraph()


def figure(n, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    try:
        p.add_run().add_picture(img(n), width=Cm(14))
    except Exception as e:
        p.add_run("[Imagem %d indisponivel: %s]" % (n, e))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rc = cap.add_run(caption)
    rc.italic = True
    rc.font.size = Pt(10)
    src = doc.add_paragraph()
    src.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = src.add_run("Fonte: O Autor (2025)")
    rs.italic = True
    rs.font.size = Pt(9)
    doc.add_paragraph()


def table(headers, rows, caption=None, widths=None):
    if caption:
        cap = doc.add_paragraph()
        rc = cap.add_run(caption)
        rc.bold = True
        rc.font.size = Pt(10)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i]._tc.get_or_add_tcPr().append(_shade(hdr[i], "D9D9D9"))
        pp = hdr[i].paragraphs[0]
        rr = pp.add_run(htext)
        rr.bold = True
        rr.font.size = Pt(10)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            pp = cells[i].paragraphs[0]
            rr = pp.add_run(str(val))
            rr.font.size = Pt(10)
    doc.add_paragraph()
    return t


def page_break():
    doc.add_page_break()


# ===========================================================================
# CAPA
# ===========================================================================
for _ in range(0):
    pass

def capa():
    para("UNIVERSIDADE DO ESTADO DO RIO DE JANEIRO", "center", bold=True)
    para("Centro de Tecnologia e Ciencias - Faculdade de Ciencia da Computacao",
         "center")
    for _ in range(4):
        doc.add_paragraph()
    para("Jose Leonardo Guimaraes Sobreiro", "center", bold=True)
    for _ in range(4):
        doc.add_paragraph()
    para("SISTEMA DE CONSULTA MULTIBANCO ANINHADA (TCC_CMA)", "center",
         bold=True, size=16)
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(7)
    p.add_run(
        "Trabalho de Conclusao de Curso apresentado ao Curso de Ciencia da "
        "Computacao da Universidade do Estado do Rio de Janeiro como requisito "
        "parcial para obtencao do titulo de Bacharel em Ciencia da Computacao."
    )
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(7)
    p.add_run("Orientadora: Profa. Adriana Aparicio Sicsu Ayres do Nascimento")
    for _ in range(6):
        doc.add_paragraph()
    para("Rio de Janeiro", "center")
    para("2025", "center")


capa()
page_break()


# ===========================================================================
# RESUMO / ABSTRACT
# ===========================================================================
h("RESUMO", 1)
para(
    "Este trabalho apresenta o desenvolvimento de um sistema web para a "
    "orquestracao de consultas aninhadas em ambientes de persistencia poliglota. "
    "O objetivo foi resolver a complexidade de integracao de dados em "
    "arquiteturas de microsservicos, onde informacoes correlatas encontram-se "
    "fragmentadas em tecnologias heterogeneas. O sistema desenvolvido, "
    "denominado TCC_CMA, oferece uma API REST unificada que permite descrever "
    "consultas encadeadas em formato JSON, integrando nativamente bancos "
    "relacionais (MySQL), orientados a documentos (MongoDB) e chave-valor "
    "(Redis). A implementacao utilizou a linguagem Python e o framework Flask, "
    "aplicando padroes de projeto como Factory Method e Singleton para garantir "
    "extensibilidade. Os resultados obtidos, validados atraves de um estudo de "
    "caso em um cenario de logistica e de E-commerce, demonstram que a camada "
    "de abstracao proposta reduz o acoplamento e simplifica a recuperacao de "
    "dados distribuidos. Este documento inclui ainda um guia de usuario completo "
    "e um extenso conjunto de casos de uso com consultas cross-database."
)
para("Palavras-chave: Persistencia Poliglota. Microsservicos. Integracao de "
     "Dados. Padroes de Projeto. Python.", italic=True)

doc.add_paragraph()
h("ABSTRACT", 1)
para(
    "This work presents the development of a web system for orchestrating "
    "nested queries in polyglot persistence environments. The goal was to solve "
    "the complexity of data integration in microservice architectures, where "
    "related information is fragmented across heterogeneous technologies. The "
    "developed system, named TCC_CMA, offers a unified REST API that allows "
    "describing chained queries in JSON format, natively integrating relational "
    "(MySQL), document-oriented (MongoDB) and key-value (Redis) databases. The "
    "implementation used Python and the Flask framework, applying design "
    "patterns such as Factory Method and Singleton to ensure extensibility. The "
    "results, validated through a logistics and E-commerce case study, show that "
    "the proposed abstraction layer reduces coupling and simplifies the "
    "retrieval of distributed data."
)
para("Keywords: Polyglot Persistence. Microservices. Data Integration. Design "
     "Patterns. Python.", italic=True)
page_break()


# ===========================================================================
# SUMARIO (estatico)
# ===========================================================================
h("SUMARIO", 1)
sumario = [
    "1 INTRODUCAO",
    "2 FUNDAMENTACAO TEORICA",
    "3 DESENVOLVIMENTO E ARQUITETURA",
    "4 GUIA DO USUARIO",
    "5 CASOS DE USO E CONSULTAS CROSS-DATABASE",
    "6 TESTES E RESULTADOS",
    "7 CONCLUSAO",
    "REFERENCIAS",
    "ANEXOS",
]
for s in sumario:
    p = doc.add_paragraph()
    p.add_run(s)
page_break()



# ===========================================================================
# 1 INTRODUCAO
# ===========================================================================
h("1 INTRODUCAO", 1)
h("1.1 Problema", 2)
para(
    "No cenario corporativo atual, e comum que empresas operem com multiplos "
    "sistemas heterogeneos que se comunicam entre si, onde cada um utiliza a "
    "tecnologia de banco de dados que melhor atende as suas necessidades "
    "especificas. Nesse contexto, um unico evento de negocio pode gerar "
    "registros em diferentes sistemas, fazendo com que as informacoes fiquem "
    "fragmentadas em varias bases de dados distintas."
)
para(
    "O desafio surge quando e necessario reunir todas as informacoes "
    "relacionadas a esse evento. Para isso, o desenvolvedor precisa acessar "
    "cada banco de dados separadamente, exigindo um conhecimento tecnico "
    "detalhado de onde cada parte do dado esta armazenada e como cada "
    "tecnologia funciona. A complexidade aumenta quando dados presentes em um "
    "banco sao pre-requisitos para filtrar informacoes em outro, criando uma "
    "dependencia entre as consultas. Na pratica, nem sempre os profissionais "
    "que demandam essas informacoes possuem o tempo ou o conhecimento tecnico "
    "especifico de todas as tecnologias envolvidas para construir essas "
    "consultas integradas manualmente."
)
para(
    "Um gestor de negocios, por exemplo, raramente domina simultaneamente a "
    "linguagem SQL do MySQL, a sintaxe de agregacao do MongoDB e os comandos de "
    "acesso do Redis. Ainda assim, ele frequentemente precisa de relatorios que "
    "cruzam dados desses tres mundos. O custo dessa fragmentacao manifesta-se "
    "em tres dimensoes: (i) tempo, pois cada consulta manual e lenta e sujeita "
    "a erros; (ii) conhecimento, pois exige especialistas em cada tecnologia; e "
    "(iii) acoplamento, pois qualquer mudanca no local fisico de um dado quebra "
    "os procedimentos manuais construidos ao redor dele."
)

h("1.2 Objetivos", 2)
h("1.2.1 Objetivo Geral", 3)
para(
    "O objetivo deste trabalho e desenvolver um sistema poliglota capaz de, a "
    "partir de uma unica requisicao de consulta, recuperar dados distribuidos "
    "em diferentes bancos de dados. O sistema deve permitir que o resultado de "
    "uma consulta em um banco seja reutilizado automaticamente como parametro "
    "de filtro para consultas subsequentes em outros bancos."
)
h("1.2.2 Objetivos Especificos", 3)
para("Para alcancar o objetivo geral, foram definidos os seguintes objetivos "
     "especificos:")
bullet("Desenvolver um padrao de requisicao intuitivo que permita descrever "
       "consultas em diferentes bancos de dados;")
bullet("Implementar uma camada de abstracao (interface) para padronizar a "
       "comunicacao com bancos relacionais, orientados a documentos e "
       "chave-valor;")
bullet("Criar o mecanismo de processamento de consultas aninhadas, permitindo "
       "a reutilizacao de resultados entre queries;")
bullet("Desenvolver interfaces CRUD web para o gerenciamento basico de cada "
       "tipo de banco de dados suportado;")
bullet("Construir um sistema web para administrar e executar as consultas "
       "integradas;")
bullet("Documentar um guia de usuario e um conjunto abrangente de casos de uso "
       "que demonstrem a associacao entre bancos distintos.")

h("1.3 Justificativa", 2)
para(
    "Com a crescente demanda por escalabilidade e especializacao em servicos "
    "digitais, a arquitetura de microsservicos tornou-se uma abordagem popular. "
    "Nela, cada servico e responsavel por um contexto de negocio e tem a "
    "liberdade de escolher o modelo de banco de dados mais adequado - seja "
    "relacional, documental ou chave-valor -, resultando em um cenario de "
    "persistencia poliglota."
)
para(
    "Embora essa flexibilidade traga beneficios tecnicos, ela eleva a "
    "complexidade no acesso aos dados. As informacoes de uma transacao de "
    "negocio acabam espalhadas, e para reconstruir o cenario completo, o "
    "usuario precisa navegar por diferentes tecnologias e modelos de dados. "
    "Diante disso, este trabalho se justifica pela necessidade de uma solucao "
    "que simplifique esse acesso. O sistema proposto oferece uma camada de "
    "abstracao que permite descrever consultas complexas em um formato unico "
    "(JSON), reduzindo o esforco de integracao e o acoplamento com os detalhes "
    "de implementacao de cada banco de dados."
)

h("1.4 Estrutura do Trabalho", 2)
para("O restante deste documento esta organizado da seguinte forma:")
bullet("O Capitulo 2 apresenta a fundamentacao teorica, abordando persistencia "
       "poliglota, os tres paradigmas de banco de dados utilizados, o estilo "
       "arquitetural REST e os padroes de projeto aplicados;")
bullet("O Capitulo 3 detalha o desenvolvimento e a arquitetura do sistema, "
       "incluindo o cenario de uma empresa de logistica utilizado como fio "
       "condutor;")
bullet("O Capitulo 4 apresenta um guia de usuario completo, ensinando desde a "
       "instalacao ate a construcao de consultas complexas;")
bullet("O Capitulo 5 reune um extenso conjunto de casos de uso com consultas "
       "cross-database, associando, por exemplo, a base de clientes com a base "
       "de logistica;")
bullet("O Capitulo 6 descreve a estrategia de testes e os resultados;")
bullet("O Capitulo 7 traz as consideracoes finais, limitacoes e trabalhos "
       "futuros.")

h("1.5 Metodologia", 2)
para(
    "A metodologia utilizada para o desenvolvimento deste trabalho foi o TDD "
    "(Test Driven Development, ou Desenvolvimento Orientado a Testes). Nessa "
    "abordagem, antes de implementar uma funcionalidade, escreve-se um teste "
    "automatizado que descreve o comportamento esperado. Em seguida, "
    "implementa-se o codigo minimo necessario para fazer o teste passar. Depois "
    "disso, o codigo e refatorado, mantendo todos os testes verdes. Esse ciclo "
    "e conhecido como Vermelho-Verde-Refatoracao."
)
para(
    "No contexto deste sistema, o TDD foi aplicado principalmente na "
    "implementacao das consultas e do processamento de queries aninhadas. "
    "Primeiro foram escritos testes para validar a traducao da requisicao JSON "
    "em consultas para cada banco de dados e o encadeamento entre elas. Somente "
    "depois esses testes foram usados como guia para a construcao das classes "
    "de acesso aos bancos (MySQL, MongoDB e Redis) e do modulo de processamento "
    "de queries."
)
para(
    "Na experiencia pratica, o uso de TDD mostrou-se mais trabalhoso e demorado "
    "no inicio, mas contribuiu para melhorar a manutenibilidade do codigo. Com "
    "uma suite de testes automatizados, foi possivel detectar rapidamente "
    "comportamentos indesejados ao integrar diferentes componentes, aumentando "
    "a seguranca nas alteracoes e na evolucao do sistema."
)
page_break()


# ===========================================================================
# 2 FUNDAMENTACAO TEORICA
# ===========================================================================
h("2 FUNDAMENTACAO TEORICA", 1)
h("2.1 Persistencia Poliglota em Arquiteturas de Microsservicos", 2)
para(
    "A evolucao das arquiteturas de software, partindo de modelos monoliticos "
    "para microsservicos, trouxe consigo a necessidade de especializacao no "
    "armazenamento de dados. Segundo Fowler (2012), a persistencia poliglota "
    "refere-se a pratica de utilizar diferentes tecnologias de armazenamento de "
    "dados dentro de uma mesma aplicacao, escolhendo a ferramenta mais adequada "
    "para cada tipo de dado ou necessidade de negocio."
)
para(
    "No contexto deste trabalho, adota-se essa abordagem para refletir cenarios "
    "reais onde sistemas modernos precisam lidar simultaneamente com transacoes "
    "estruturadas, documentos flexiveis e dados de acesso rapido em memoria. "
    "Essa heterogeneidade, embora vantajosa para a performance individual de "
    "cada servico, introduz a complexidade de integracao abordada pelo sistema "
    "proposto."
)
para(
    "Sadalage e Fowler (2012) argumentam que o fim da era do banco de dados "
    "relacional como escolha unica e uma consequencia natural da diversidade de "
    "requisitos das aplicacoes modernas. Um mesmo dominio de negocio pode exigir "
    "consistencia forte em uma parte (financeiro) e alta disponibilidade com "
    "flexibilidade de esquema em outra (catalogo de produtos, telemetria). A "
    "persistencia poliglota assume, portanto, que a diversidade de tecnologias "
    "e um recurso, e nao um problema - desde que exista uma estrategia clara de "
    "integracao dos dados que ficam distribuidos."
)

h("2.2 Tecnologias de Banco de Dados", 2)
para(
    "Um sistema web e um software que recebe e processa requisicoes pela rede, "
    "geralmente utilizando os protocolos HTTP ou HTTPS. Nesse modelo, um "
    "cliente, como um navegador ou outra aplicacao, envia uma requisicao para o "
    "servidor, que processa a solicitacao e devolve uma resposta. Neste "
    "projeto, e utilizado o estilo arquitetural REST sobre o protocolo HTTP, o "
    "que facilita a organizacao das rotas, o uso de metodos como GET e POST e a "
    "integracao com outros sistemas."
)
para("Para demonstrar a viabilidade da solucao em um ambiente heterogeneo, "
     "foram selecionados tres Sistemas Gerenciadores de Banco de Dados (SGBDs) "
     "representativos de paradigmas distintos:")

h("2.2.1 Bancos Relacionais (MySQL)", 3)
para(
    "O MySQL foi escolhido para representar o modelo relacional, amplamente "
    "adotado devido a sua conformidade com as propriedades ACID (Atomicidade, "
    "Consistencia, Isolamento e Durabilidade). No projeto, ele simula o "
    "armazenamento de dados estruturados e criticos, onde a integridade "
    "referencial e o esquema rigido sao fundamentais. Sua manipulacao e "
    "realizada atraves da linguagem SQL, exigindo mapeamento especifico para a "
    "interface unificada do sistema. No cenario de logistica adotado neste "
    "trabalho, o MySQL sustenta o cadastro de clientes (CMS), o estoque (SMS) e "
    "o financeiro (FNMS), dominios em que a exatidao e a consistencia sao "
    "inegociaveis."
)
h("2.2.2 Bancos Orientados a Documentos (MongoDB)", 3)
para(
    "Representando a familia NoSQL, o MongoDB e utilizado para armazenar dados "
    "semi-estruturados em formato BSON (Binary JSON). Sua escolha justifica-se "
    "pela flexibilidade de esquema (schema-less), permitindo que objetos "
    "complexos e hierarquicos sejam persistidos sem a rigidez de tabelas "
    "relacionais. Essa caracteristica e essencial para microsservicos que "
    "evoluem rapidamente suas estruturas de dados. No cenario proposto, o "
    "MongoDB armazena pedidos (OMS) com historico aninhado e rotas de entrega "
    "(FMS), cujas estruturas variam conforme o tipo de operacao."
)
h("2.2.3 Armazenamento Chave-Valor (Redis)", 3)
para(
    "O Redis atua como um armazenamento de dados em memoria de alta "
    "performance. Diferente dos anteriores, seu foco nao e a persistencia de "
    "longo prazo complexa, mas sim a velocidade de leitura e escrita. Neste "
    "trabalho, o Redis ilustra cenarios de cache ou sessoes distribuidas, onde "
    "a latencia minima e prioritaria, complementando os armazenamentos em disco "
    "do MySQL e MongoDB. No cenario de logistica, o Redis guarda a ultima "
    "posicao GPS conhecida de cada veiculo da frota, um dado de altissima "
    "volatilidade que nao se beneficia de persistencia relacional."
)
para("O Quadro a seguir sintetiza as diferencas entre os tres paradigmas "
     "utilizados no sistema.")
table(
    ["Criterio", "MySQL (Relacional)", "MongoDB (Documento)", "Redis (Chave-Valor)"],
    [
        ["Modelo de dados", "Tabelas e linhas", "Documentos BSON", "Pares chave-valor"],
        ["Esquema", "Rigido (schema-on-write)", "Flexivel (schema-less)", "Nao aplicavel"],
        ["Consistencia", "Forte (ACID)", "Ajustavel", "Eventual/memoria"],
        ["Uso no projeto", "CMS, SMS, FNMS", "OMS, FMS (rotas)", "FMS (rastreamento)"],
        ["Ponto forte", "Integridade", "Flexibilidade", "Latencia minima"],
    ],
    caption="Quadro 1 - Comparacao dos paradigmas de banco de dados utilizados",
)

h("2.3 O Estilo Arquitetural REST e o Formato JSON", 2)
para(
    "REST (Representational State Transfer) e um estilo arquitetural que define "
    "um conjunto de restricoes para a criacao de servicos web. Recursos sao "
    "identificados por URLs e manipulados por meio dos metodos do protocolo "
    "HTTP (GET, POST, PUT, DELETE). O formato JSON (JavaScript Object Notation) "
    "e amplamente utilizado como representacao dos recursos por ser leve, "
    "legivel por humanos e nativamente suportado pela maioria das linguagens. "
    "No sistema TCC_CMA, o JSON nao e apenas o formato de transporte, mas "
    "tambem a propria linguagem de definicao das consultas: e por meio de uma "
    "estrutura JSON declarativa que o usuario descreve o que deseja buscar e "
    "como as consultas se encadeiam."
)

h("2.4 Padroes de Projeto Aplicados", 2)
para(
    "A complexidade de gerenciar multiplas conexoes e manter o estado entre "
    "consultas aninhadas exigiu a aplicacao de padroes de projeto classicos "
    "(Gamma et al., 1994) para garantir a manutenibilidade e a extensibilidade "
    "do codigo."
)
h("2.4.1 Factory Method", 3)
para(
    "O padrao Factory foi implementado para encapsular a logica de criacao das "
    "conexoes com os bancos de dados. Atraves da classe Databases, o sistema "
    "decide dinamicamente qual implementacao de cliente (MySQL, MongoDB ou "
    "Redis) instanciar com base na string de configuracao recebida na "
    "requisicao JSON. Isso permite que novos tipos de bancos sejam adicionados "
    "futuramente sem alterar a logica principal de processamento das queries, "
    "respeitando o principio Aberto/Fechado (Open/Closed Principle)."
)
h("2.4.2 Singleton", 3)
para(
    "Para resolver o problema de compartilhamento de contexto entre as "
    "multiplas interacoes recursivas das consultas aninhadas, utilizou-se o "
    "padrao Singleton na classe VarsSingleton. Este padrao assegura que exista "
    "uma unica instancia responsavel por armazenar os resultados intermediarios "
    "das queries, permitindo que uma consulta interna acesse dados recuperados "
    "por uma consulta externa (pai) sem a necessidade de passar esses dados "
    "complexos como parametros em toda a cadeia de chamadas."
)
h("2.4.3 Strategy e Interface Comum", 3)
para(
    "A classe abstrata DBInterface define um contrato comum (metodos de leitura "
    "e escrita) que todas as implementacoes concretas devem seguir. Essa "
    "aplicacao do padrao Strategy permite que o motor de consultas trate "
    "qualquer banco de forma polimorfica: para o QueryModel, tanto faz se o "
    "cliente por tras da interface e MySQL, MongoDB ou Redis, pois todos "
    "expoem os mesmos metodos."
)

h("2.5 Infraestrutura e Web", 2)
para(
    "O sistema foi construido sobre o microframework Flask, escolhido por sua "
    "leveza e flexibilidade na criacao de APIs RESTful. A arquitetura web segue "
    "o modelo cliente-servidor, onde o Flask gerencia o roteamento das "
    "requisicoes HTTP e a injecao de dependencias dos servicos de banco de "
    "dados."
)
para(
    "Para garantir a reprodutibilidade do ambiente poliglota - que exige a "
    "orquestracao simultanea de servicos Python, MySQL, MongoDB e Redis -, "
    "utilizou-se o Docker. A conteinerizacao isola as dependencias de cada "
    "servico, permitindo que toda a pilha tecnologica seja instanciada com um "
    "unico comando, eliminando problemas de compatibilidade entre diferentes "
    "ambientes de desenvolvimento e producao."
)
page_break()


# ===========================================================================
# 3 DESENVOLVIMENTO E ARQUITETURA
# ===========================================================================
h("3 DESENVOLVIMENTO E ARQUITETURA", 1)

h("3.1 O Cenario: Uma Empresa de Logistica", 2)
para(
    "Para conduzir o desenvolvimento e a validacao do sistema, adotou-se como "
    "fio condutor o cenario de uma empresa de logistica de medio porte, com "
    "atuacao nacional, que administra diversos sistemas diferentes para "
    "problemas distintos, com solucoes e tecnologias diversas. Um gestor nessa "
    "empresa precisa saber navegar por sistemas de cadastro de clientes (CMS), "
    "gerenciamento de frota (FMS), gerenciamento de estoque (SMS), "
    "gerenciamento financeiro (FNMS) e gerenciamento de pedidos (OMS)."
)
para("Cada um desses sistemas foi projetado independentemente e escolheu a "
     "tecnologia de persistencia mais adequada ao seu dominio:")
bullet("CMS (Client Management System): responsavel por administrar o cadastro "
       "dos clientes e seus dados sensiveis, como nomes, documentos, enderecos, "
       "formas de contato e meios de pagamento. Consultas e cadastros sao "
       "feitos via API utilizando um banco de dados MySQL.")
bullet("FMS (Fleet Management System): gerencia a frota de veiculos da empresa, "
       "como custos de rodagem, otimizacao de rotas, rastreamento e "
       "balanceamento de carga. Consultas e cadastros sao feitos via API, com "
       "rastreamento em tempo real em um banco Redis e outros registros em um "
       "MongoDB.")
bullet("SMS (Storage Management System): mantem os registros dos produtos, como "
       "quantidades, validades, tamanhos, localidade e necessidades "
       "especificas. Cadastros feitos via sistema, retiradas via API e "
       "consultas por relatorios ou diretamente no banco de dados MySQL.")
bullet("FNMS (Financial Management System): pagamentos em geral, emissao de "
       "notas fiscais e gerencia de contas bancarias. Consultas via relatorio "
       "ou diretamente no banco de dados MySQL e cadastros via sistema.")
bullet("OMS (Order Management System): recebe e orquestra o envio de pedidos - "
       "para quem, para onde e como - entre os armazens e para os clientes "
       "finais. Consultas e cadastros via API ou via sistema, com banco de "
       "dados MongoDB.")
para(
    "Em todos esses sistemas a integracao e feita ou por APIs ou por ingestao "
    "manual. O sistema OMS, quando envia uma requisicao de transporte, nao tem "
    "como saber se os dados recebidos na requisicao ou inseridos via sistema "
    "sao verdadeiros; eles sao apenas dados de referencia que tem origem em "
    "outro sistema. Ou seja, nao ha como haver uma constraint de banco de dados "
    "que impeca a insercao de dados inconsistentes entre sistemas."
)
para(
    "Se um gestor precisar fazer um relatorio completo com todos os dados "
    "relacionados a um pedido, serao necessarias pelo menos uma consulta em "
    "cada sistema; mas, em alguns casos, havera a necessidade de voltar a um "
    "sistema ja consultado para conseguir algum dado, ja que sua referencia de "
    "utilizacao esta em um banco terceiro e nao no mesmo. A operacao de todos "
    "esses sistemas requer que dados sejam consultados manualmente, seja em um "
    "relatorio ou diretamente em um sistema, para serem utilizados em outro, o "
    "que torna todo o processo mais lento."
)
para(
    "Para melhorar essa situacao, foi concebido o TCC_CMA: um sistema que se "
    "integra diretamente a cada um dos bancos de dados utilizados por todos os "
    "sistemas da empresa, de modo que as consultas sejam concentradas em um "
    "unico ponto, agilizando o processo e melhorando a eficiencia da empresa "
    "como um todo."
)

h("3.2 Modelagem dos Sistemas de Origem", 2)
para("Para viabilizar os casos de uso do Capitulo 5, cada sistema de origem "
     "foi modelado com um conjunto de entidades. As secoes a seguir descrevem "
     "essas entidades e apresentam os esquemas de dados adotados.")

h("3.2.1 Sistema de Gerenciamento de Clientes (CMS)", 3)
para(
    "Este componente opera como a autoridade central para os dados cadastrais "
    "da organizacao. No ambito de uma arquitetura baseada em microsservicos, a "
    "manutencao das propriedades ACID e fundamental para assegurar a "
    "integridade informacional e impedir a existencia de registros redundantes "
    "entre as bases distribuidas."
)
bullet("Clientes: gerencia a identidade central dos sujeitos, abrangendo tanto "
       "Pessoas Fisicas quanto Juridicas. O campo tipo viabiliza a aplicacao "
       "dinamica de distintas regras de negocio e validacao.")
bullet("Enderecos: estrutura normalizada que permite a associacao de multiplos "
       "registros a um unico cliente, diferenciando contextos de entrega e "
       "faturamento.")
bullet("Meios de Pagamento: em conformidade com o PCI-DSS, prioriza o uso de "
       "tokens para representar dados financeiros, evitando a persistencia de "
       "informacoes sensiveis em formato bruto.")
table(
    ["Tabela (MySQL - cms)", "Campos principais"],
    [
        ["clientes", "id, tipo, nome, documento, email, telefone"],
        ["enderecos", "id, cliente_id, tipo, logradouro, cidade, uf, cep"],
        ["meios_pagamento", "id, cliente_id, token, bandeira, validade"],
    ],
    caption="Quadro 2 - Esquema do banco CMS (MySQL)",
)
figure(1, "Figura 1 - Diagrama do Sistema CMS")

h("3.2.2 Sistema de Gerenciamento de Frota (FMS)", 3)
para(
    "Este componente e responsavel pela orquestracao logistica e pelo "
    "processamento de dados de telemetria. A utilizacao do MongoDB viabiliza a "
    "persistencia de historicos de rotas com estruturas variaveis, enquanto o "
    "Redis assegura o tratamento de dados de GPS caracterizados por alta "
    "volatilidade."
)
bullet("Rotas: centraliza o percurso integral dos veiculos por meio de "
       "documentos que permitem o acoplamento de historicos de custos e "
       "eventos transacionais.")
bullet("Veiculos: administra especificacoes tecnicas e capacidades "
       "operacionais, com flexibilidade schema-less.")
bullet("Rastreamento: prioriza a altissima performance em memoria para o "
       "monitoramento em tempo real, retendo as ultimas coordenadas "
       "geograficas de cada veiculo (chave = placa).")
table(
    ["Colecao/Chave (FMS)", "Tecnologia", "Campos principais"],
    [
        ["rotas", "MongoDB (fms)", "id, veiculo_placa, pedido_id, origem, destino, status"],
        ["veiculos", "MongoDB (fms)", "id, placa, modelo, capacidade_kg, motorista"],
        ["rastreamento", "Redis (db 0)", "chave: placa -> valor: 'lat,long' (ultima posicao)"],
    ],
    caption="Quadro 3 - Esquema do banco FMS (MongoDB + Redis)",
)
figure(2, "Figura 2 - Diagrama do Sistema FMS")

h("3.2.3 Sistema de Gerenciamento de Estoque (SMS)", 3)
para(
    "Este componente e responsavel pela custodia fisica do inventario e pela "
    "rastreabilidade operacional. A arquitetura hierarquica implementada "
    "assegura que a localizacao de qualquer insumo seja auditavel ate o nivel "
    "da prateleira (setor) especifica, otimizando o fluxo logistico interno."
)
bullet("Galpao: unidade fisica macro de armazenamento (armazem), atuando como "
       "no principal da infraestrutura de estocagem.")
bullet("Setores: subdivisao logica e fisica do galpao, incorporando restricoes "
       "operacionais como 'Carga Maxima'.")
bullet("Produtos: consolida especificacoes metricas e de massa, vinculando o "
       "item a sua coordenada exata de deposito.")
table(
    ["Tabela (MySQL - sms)", "Campos principais"],
    [
        ["galpoes", "id, nome, cidade, uf"],
        ["setores", "id, galpao_id, codigo, carga_maxima_kg"],
        ["produtos", "id, setor_id, nome, sku, quantidade, validade, peso_kg"],
    ],
    caption="Quadro 4 - Esquema do banco SMS (MySQL)",
)
figure(3, "Figura 3 - Diagrama do Sistema SMS")

h("3.2.4 Sistema de Gerenciamento Financeiro (FNMS)", 3)
para(
    "Este componente e responsavel por assegurar a higidez financeira e a "
    "conformidade tributaria da operacao. A adocao do MySQL justifica-se pela "
    "necessidade de rigor transacional e suporte as propriedades ACID, "
    "garantindo a precisao na contabilizacao de cada evento economico."
)
bullet("Notas Fiscais: gerencia a documentacao legal que formaliza as "
       "transacoes comerciais.")
bullet("Linhas de Nota Fiscal: detalhamento granular de cada item "
       "comercializado.")
bullet("Cobrancas e Pagamentos: estabelece a distincao entre a expectativa de "
       "direito (Cobranca) e a efetiva liquidacao financeira (Pagamento).")
table(
    ["Tabela (MySQL - fnms)", "Campos principais"],
    [
        ["notas_fiscais", "id, pedido_id, cliente_id, valor_total, data_emissao"],
        ["linhas_nota", "id, nota_id, produto_sku, quantidade, valor_unitario"],
        ["cobrancas", "id, nota_id, valor, vencimento, status"],
        ["pagamentos", "id, cobranca_id, valor_pago, data_pagamento"],
    ],
    caption="Quadro 5 - Esquema do banco FNMS (MySQL)",
)
figure(4, "Figura 4 - Diagrama do Sistema FNMS")

h("3.2.5 Sistema de Gerenciamento de Pedidos (OMS)", 3)
para(
    "Este componente atua como o orquestrador central do fluxo de transacoes, "
    "consolidando dados provenientes dos demais sistemas perifericos. A adocao "
    "do MongoDB permite a geracao de snapshots de venda, assegurando a "
    "imutabilidade do registro historico frente a eventuais atualizacoes de "
    "precos ou especificacoes de produtos nos sistemas de origem."
)
bullet("Pedido: documento mestre que agrega os estados transacionais, "
       "abrangendo dimensoes logisticas, financeiras e cadastrais do cliente.")
bullet("Historico: implementado como um array aninhado, registra as transicoes "
       "de estado, provendo uma trilha de auditoria desde a autorizacao ate a "
       "conclusao da entrega.")
table(
    ["Colecao (MongoDB - oms)", "Campos principais"],
    [
        ["pedidos", "id, cliente_id, itens[], valor_total, status, historico[]"],
    ],
    caption="Quadro 6 - Esquema do banco OMS (MongoDB)",
)
figure(5, "Figura 5 - Diagrama do Sistema OMS")

h("3.3 Requisitos do Sistema", 2)
para(
    "Para validar a proposta de interoperabilidade entre bancos de dados "
    "heterogeneos, o sistema foi projetado para suportar tres paradigmas "
    "distintos de armazenamento: relacional (MySQL), orientado a documentos "
    "(MongoDB) e chave-valor (Redis)."
)
para(
    "Os requisitos funcionais do sistema foram definidos para cobrir todo o "
    "ciclo de vida da manipulacao de dados em uma arquitetura poliglota. O "
    "sistema deve ser capaz de traduzir uma requisicao unificada em formato "
    "JSON para os dialetos especificos de cada banco de dados suportado. Alem "
    "da execucao de consultas isoladas, e requisito fundamental que a aplicacao "
    "suporte a realizacao de consultas aninhadas (sucessivas), onde o mecanismo "
    "de processamento deve permitir que o resultado de uma consulta externa "
    "(pai) seja utilizado dinamicamente como filtro para uma consulta interna "
    "(filha). Adicionalmente, o sistema deve fornecer interfaces CRUD web para "
    "a administracao basica dos registros em cada banco de dados."
)
table(
    ["ID", "Requisito Funcional"],
    [
        ["RF01", "Traduzir requisicao JSON unificada para MySQL, MongoDB e Redis"],
        ["RF02", "Executar consultas isoladas em qualquer banco suportado"],
        ["RF03", "Executar consultas aninhadas com reuso de resultados (on_result)"],
        ["RF04", "Fornecer CRUD web por tipo de banco"],
        ["RF05", "Expor API REST em /api/query"],
        ["RF06", "Consolidar os resultados de todas as etapas em um unico JSON"],
    ],
    caption="Quadro 7 - Requisitos funcionais do sistema",
)

h("3.4 Arquitetura do Sistema", 2)
para(
    "O sistema foi desenvolvido utilizando a linguagem Python (versao 3.12) em "
    "conjunto com o framework Flask para o gerenciamento das requisicoes HTTP. "
    "A arquitetura segue o padrao em camadas, promovendo a separacao de "
    "responsabilidades e facilitando a manutencao, conforme ilustrado na "
    "Figura 6."
)
figure(6, "Figura 6 - Arquitetura em camadas do sistema TCC_CMA")

h("3.4.1 Componentes Principais", 3)
para("A arquitetura de software baseia-se na interacao entre quatro "
     "componentes principais, desenhados sobre padroes de projeto orientados a "
     "objetos:")
bullet("Database Interface (DBInterface): classe abstrata que atua como um "
       "contrato, definindo os metodos essenciais que todas as implementacoes "
       "de banco de dados devem possuir. Garante que o nucleo da aplicacao "
       "interaja com qualquer SGBD de forma transparente.")
bullet("Databases Model (Factory): responsavel por gerenciar a criacao de "
       "conexoes. Utilizando o Factory Method, decide em tempo de execucao qual "
       "classe concreta - MysqlClient, MongodbClient ou RedisClient - deve ser "
       "instanciada com base nos parametros recebidos.")
bullet("Query Model (Orquestrador): componente central da logica de aplicacao. "
       "Processa o JSON de entrada, gerencia as referencias entre consultas e "
       "implementa a recursividade necessaria para o processamento de queries "
       "aninhadas.")
bullet("VarsSingleton: implementando o padrao Singleton, mantem o estado "
       "compartilhado durante o ciclo de vida de uma requisicao complexa, "
       "armazenando os resultados intermediarios indexados por alias.")

h("3.5 Implementacao e Fluxo de Execucao", 2)
para(
    "A comunicacao com o sistema e realizada atraves de uma API REST que recebe "
    "cargas uteis (payloads) em formato JSON. A estrutura de dados da "
    "requisicao foi projetada para ser declarativa, contendo a definicao do "
    "servico alvo (service), banco de dados (database), tabela ou colecao "
    "(schema) e os filtros a serem aplicados."
)
para("O fluxo de execucao de uma consulta complexa segue os passos abaixo:")
numbered("Recepcao da requisicao POST pelo Flask no endpoint /api/query;")
numbered("O QueryModel realiza o parsing dos parametros e solicita a Factory a "
         "conexao apropriada;")
numbered("Antes da execucao, o sistema verifica se existem referencias a "
         "resultados anteriores (processamento de filtros dinamicos);")
numbered("A query e executada no banco de dados; o resultado e armazenado no "
         "VarsSingleton, indexado por alias;")
numbered("Caso a requisicao contenha a diretiva on_result, o QueryModel "
         "instancia-se recursivamente para cada item, processando a proxima "
         "consulta com os dados recem-adquiridos como contexto;")
numbered("Por fim, todos os resultados sao agregados e retornados em uma "
         "estrutura JSON consolidada.")
para("O trecho a seguir ilustra o coracao do algoritmo de encadeamento, "
     "extraido da classe QueryModel:")
code(
    'def execute_query(self):\n'
    '    self.database = self.get_database()\n'
    '    if self.previous_result:\n'
    '        self.update_filter_from_previous_results_values()\n'
    '    self.result = {self.alias: self.filter_query()}\n'
    '    if self.result:\n'
    '        self.vars.set(self.alias, self.result)\n'
    '    if self.request.get("on_result"):\n'
    '        self.next_query = []\n'
    '        for item in self.result.get(self.alias, []):\n'
    '            next_request = self.request.get("on_result").copy()\n'
    '            next_request["filter"] = self._update_filter_with_item(\n'
    '                next_request.get("filter"), item)\n'
    '            self.next_query.append(QueryModel(next_request, self.result))\n'
    '        for query in self.next_query:\n'
    '            query.execute_query()\n'
    '            self.result.update(query.result)',
    caption="Codigo 1 - Metodo execute_query (query_model.py)",
)
page_break()


# ===========================================================================
# 4 GUIA DO USUARIO
# ===========================================================================
h("4 GUIA DO USUARIO", 1)
para(
    "Este capitulo funciona como um manual pratico do sistema TCC_CMA. Ele foi "
    "escrito para que um novo usuario - desenvolvedor, analista ou gestor "
    "tecnico - consiga, do zero, instalar o ambiente, subir os bancos de dados, "
    "popular dados de exemplo, navegar pela interface web e, principalmente, "
    "construir suas proprias consultas cross-database. Ao final do capitulo, o "
    "leitor deve ser capaz de escrever consultas aninhadas que associem, por "
    "exemplo, a base de clientes (CMS) com a base de logistica (FMS/OMS)."
)

h("4.1 Pre-requisitos", 2)
para("Antes de iniciar, garanta que o ambiente possua as seguintes "
     "ferramentas instaladas:")
bullet("Python 3.10 ou superior (o projeto foi desenvolvido e testado em 3.12);")
bullet("pip, o gerenciador de pacotes do Python;")
bullet("Docker e Docker Compose - recomendados para subir MySQL, MongoDB e "
       "Redis sem instalacao manual;")
bullet("Um cliente HTTP para testar a API (curl, Postman ou Insomnia) - "
       "opcional, ja que ha interface web.")

h("4.2 Obtendo o Codigo-Fonte", 2)
para("O codigo-fonte esta disponivel no repositorio publico do projeto. Para "
     "obte-lo, utilize o comando:")
code(
    "git clone https://github.com/jlgsobreiro/TCC_CMA\n"
    "cd TCC_CMA",
    caption="Codigo 2 - Clonagem do repositorio",
)

h("4.3 Instalacao das Dependencias (modo local)", 2)
para("Recomenda-se criar um ambiente virtual isolado para instalar as "
     "dependencias do projeto:")
code(
    "python -m venv venv\n"
    "venv\\Scripts\\activate      # Windows\n"
    "# source venv/bin/activate   # Linux/Mac\n"
    "pip install -r requirements.txt",
    caption="Codigo 3 - Criacao do ambiente virtual e instalacao",
)
para(
    "As principais dependencias declaradas em requirements.txt sao: Flask "
    "(framework web), PyMySQL (driver MySQL), PyMongo e MongoEngine (MongoDB) e "
    "redis (cliente Redis). Todas sao instaladas automaticamente pelo comando "
    "acima."
)

h("4.4 Subindo os Bancos de Dados com Docker", 2)
para(
    "A forma mais simples de disponibilizar os tres bancos de dados e por meio "
    "do Docker Compose. O arquivo docker-compose.yml ja inclui a configuracao "
    "de MySQL, MongoDB, Redis e tres instancias da aplicacao Flask. Para subir "
    "toda a pilha, execute:")
code(
    "docker-compose up -d\n"
    "# ou, usando o atalho do Makefile:\n"
    "make up",
    caption="Codigo 4 - Subindo os servicos com Docker",
)
para("Apos a execucao, os servicos ficam disponiveis nas seguintes portas:")
table(
    ["Servico", "Porta", "Descricao"],
    [
        ["mysql", "3306", "Banco MySQL 8.0"],
        ["mongodb", "27017", "Banco MongoDB"],
        ["redis", "6379", "Cache Redis"],
        ["flask1", "5000", "Aplicacao Flask (DB padrao MySQL)"],
        ["flask2", "5001", "Aplicacao Flask (DB padrao MongoDB)"],
        ["flask3", "5002", "Aplicacao Flask (DB padrao Redis)"],
    ],
    caption="Quadro 8 - Servicos e portas do docker-compose",
)

h("4.5 Populando Dados de Exemplo (fixtures)", 2)
para(
    "O projeto acompanha o script fixtures.py, que registra as conexoes no "
    "catalogo de bancos e insere registros de exemplo em cada tecnologia. Para "
    "executa-lo:")
code(
    "python fixtures.py",
    caption="Codigo 5 - Carga de dados de exemplo",
)
para(
    "Esse script realiza tres tarefas: (i) limpa e recria o catalogo de "
    "conexoes (funcao setup_databases); (ii) cria a tabela de exemplo no MySQL "
    "e insere tres linhas; e (iii) insere tres pares chave-valor no Redis e "
    "tres documentos no MongoDB. E a partir desse catalogo de conexoes que o "
    "motor de consultas descobre, em tempo de execucao, como se conectar a cada "
    "banco. Para os casos de uso do Capitulo 5, o leitor pode adaptar esse "
    "script para inserir os dados de clientes, pedidos e rotas descritos no "
    "cenario de logistica."
)

h("4.6 Executando a Aplicacao", 2)
para("Com os bancos no ar e as fixtures carregadas, inicie a aplicacao web:")
code(
    "python app.py",
    caption="Codigo 6 - Inicializacao do servidor Flask",
)
para(
    "A aplicacao sobe por padrao em http://localhost:5000. Ao acessar esse "
    "endereco no navegador, o usuario e recebido pela pagina inicial, que lista "
    "os itens da conexao padrao e da acesso as demais funcionalidades."
)

h("4.7 Utilizando as Interfaces CRUD", 2)
para(
    "O sistema oferece telas de CRUD (Create, Read, Update, Delete) para cada "
    "tipo de banco, acessiveis pelas rotas /crud/mysql, /crud/mongodb e "
    "/crud/redis. Essas telas permitem inserir, listar, editar e remover "
    "registros sem escrever uma unica linha de codigo, sendo uteis para "
    "preparar os dados que serao consultados posteriormente."
)
para("O fluxo tipico de uso de uma tela CRUD e:")
numbered("Acessar a rota do banco desejado, por exemplo /crud/mysql;")
numbered("Preencher os campos id e external_id no formulario de adicao e "
         "confirmar;")
numbered("Visualizar o novo registro na listagem;")
numbered("Usar o botao Update para editar ou Delete para remover um registro.")
figure(7, "Figura 7 - Interface CRUD do MySQL")
figure(8, "Figura 8 - Interface CRUD do Redis")
figure(9, "Figura 9 - Interface CRUD do MongoDB")

h("4.8 A Interface Web de Consultas", 2)
para(
    "A rota /query oferece uma interface amigavel para submeter consultas em "
    "formato JSON e visualizar o resultado consolidado. Basta colar a estrutura "
    "da consulta na area de texto e clicar em executar; o resultado retorna "
    "logo abaixo, ja com os dados de todas as etapas mescladas. Essa e a "
    "maneira mais rapida de experimentar os casos de uso do proximo capitulo "
    "sem precisar de um cliente HTTP externo."
)

h("4.9 Utilizando a API REST", 2)
para(
    "Para integracao programatica, o sistema expoe o endpoint POST /api/query. "
    "A requisicao deve ter o cabecalho Content-Type: application/json e o corpo "
    "deve conter o objeto de consulta. Um exemplo de chamada com curl:")
code(
    'curl -X POST http://localhost:5000/api/query \\\n'
    '  -H "Content-Type: application/json" \\\n'
    '  -d \'{"service":"mysql","database":"cms","schema":"clientes",\n'
    '       "filter":{"id":"1"}}\'',
    caption="Codigo 7 - Chamada da API com curl",
)
para(
    "A resposta e um objeto JSON no formato {\"result\": { <alias>: [ ... ] }}. "
    "Em caso de JSON invalido, a API retorna status 400 com uma mensagem de "
    "erro descritiva."
)

h("4.10 Anatomia de uma Consulta (DSL em JSON)", 2)
para(
    "O coracao do sistema e a linguagem declarativa em JSON usada para "
    "descrever consultas. Cada consulta e um objeto com os campos descritos no "
    "Quadro 9. O campo on_result e o que possibilita o encadeamento: ele contem "
    "outra consulta, com exatamente a mesma estrutura, que sera executada "
    "utilizando os resultados da consulta atual.")
table(
    ["Campo", "Obrigatorio", "Descricao"],
    [
        ["service", "Sim", "Tipo do banco: mysql, mongodb ou redis"],
        ["database", "Sim", "Nome do banco (ou indice Redis, ex.: '0')"],
        ["schema", "Condicional", "Tabela/colecao (nao usado no Redis)"],
        ["alias", "Nao", "Identificador dos resultados desta etapa"],
        ["filter", "Sim", "Criterios de busca (aceita referencias)"],
        ["project", "Nao", "Lista de campos a retornar (projecao)"],
        ["on_result", "Nao", "Consulta encadeada, mesma estrutura"],
    ],
    caption="Quadro 9 - Campos da linguagem de consulta",
)

h("4.10.1 A Sintaxe de Referencia entre Etapas", 3)
para(
    "O recurso mais poderoso da DSL e a capacidade de usar, no filtro de uma "
    "consulta, um valor produzido por uma consulta anterior. Isso e feito com a "
    "notacao a seguir:")
code(
    '{ "campo_destino": { "alias_origem": "campo_origem" } }',
    caption="Codigo 8 - Notacao de referencia entre etapas",
)
para(
    "A leitura dessa estrutura e: 'use, como valor de campo_destino, o valor de "
    "campo_origem presente nos resultados da etapa alias_origem'. Quando o "
    "alias nao e informado, ele e gerado automaticamente no formato "
    "service__database__schema (por exemplo, mysql__cms__clientes)."
)
para(
    "E essa notacao que permite, por exemplo, buscar um cliente no MySQL (CMS) "
    "e, em seguida, buscar automaticamente todos os pedidos daquele cliente no "
    "MongoDB (OMS), usando o id retornado pela primeira consulta como filtro da "
    "segunda. O Capitulo 5 explora esse mecanismo em profundidade."
)

h("4.11 Erros Comuns e Solucao de Problemas", 2)
table(
    ["Sintoma", "Causa provavel", "Solucao"],
    [
        ["Erro 'database not found'", "Conexao nao registrada no catalogo",
         "Executar fixtures.py / registrar a conexao"],
        ["Resposta 400 Invalid JSON", "JSON malformado na requisicao",
         "Validar o JSON (virgulas, aspas, chaves)"],
        ["Lista vazia no resultado", "Filtro sem correspondencia ou alias errado",
         "Conferir o alias_origem e o campo referenciado"],
        ["Falha de conexao no Docker", "Uso de localhost entre containers",
         "Usar o nome do servico (mysql, mongodb, redis)"],
    ],
    caption="Quadro 10 - Guia rapido de solucao de problemas",
)
page_break()


# ===========================================================================
# 5 CASOS DE USO E CONSULTAS CROSS-DATABASE
# ===========================================================================
h("5 CASOS DE USO E CONSULTAS CROSS-DATABASE", 1)
para(
    "Este capitulo reune um conjunto abrangente de casos de uso reais do "
    "sistema TCC_CMA, todos ambientados na empresa de logistica descrita no "
    "Capitulo 3. Cada caso segue a mesma estrutura: uma descricao do problema "
    "de negocio, a consulta JSON correspondente, uma explicacao do que ocorre "
    "em cada etapa e um exemplo do resultado consolidado retornado. O objetivo "
    "e demonstrar, de forma pratica, como o sistema associa dados de bancos "
    "distintos - por exemplo, cruzando a base de clientes (CMS/MySQL) com a "
    "base de logistica (OMS/MongoDB, FMS/Redis)."
)


def caso(num, titulo, objetivo, req, explicacao, resultado):
    h("5.%d %s" % (num, titulo), 2)
    para(objetivo)
    para("Consulta:", bold=True)
    code(req, caption="Codigo - Requisicao do Caso %d" % num)
    para("Explicacao:", bold=True)
    para(explicacao)
    para("Resultado consolidado (exemplo):", bold=True)
    code(resultado, caption="Resultado do Caso %d" % num)


caso(
    1,
    "Cliente e seus Pedidos (CMS -> OMS)",
    "Um atendente precisa, a partir do identificador de um cliente, recuperar "
    "todos os pedidos daquele cliente. Os dados cadastrais estao no MySQL (CMS) "
    "e os pedidos no MongoDB (OMS).",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "cms",\n'
    '  "schema": "clientes",\n'
    '  "alias": "cliente",\n'
    '  "filter": {"id": "1"},\n'
    '  "on_result": {\n'
    '    "service": "mongodb",\n'
    '    "database": "oms",\n'
    '    "schema": "pedidos",\n'
    '    "alias": "pedidos",\n'
    '    "filter": {"cliente_id": {"cliente": "id"}}\n'
    '  }\n'
    '}',
    "A consulta externa busca o cliente de id 1 no CMS e guarda o resultado sob "
    "o alias 'cliente'. Em seguida, para esse cliente, a consulta interna busca "
    "no OMS todos os pedidos cujo campo cliente_id seja igual ao id do cliente "
    "recuperado - referencia expressa por {\"cliente\": \"id\"}. O sistema "
    "resolve automaticamente a substituicao do valor.",
    '{\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda", "tipo": "PJ"}],\n'
    '  "pedidos": [\n'
    '    {"id": "P-100", "cliente_id": "1", "status": "ENTREGUE"},\n'
    '    {"id": "P-131", "cliente_id": "1", "status": "EM_ROTA"}\n'
    '  ]\n'
    '}',
)

caso(
    2,
    "Pedido e sua Entrega/Rota (OMS -> FMS)",
    "O setor de operacoes deseja localizar, para um pedido especifico, a rota "
    "de entrega associada. O pedido esta no MongoDB (OMS) e a rota tambem no "
    "MongoDB, porem no banco de frota (FMS).",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "pedido",\n'
    '  "filter": {"id": "P-131"},\n'
    '  "on_result": {\n'
    '    "service": "mongodb",\n'
    '    "database": "fms",\n'
    '    "schema": "rotas",\n'
    '    "alias": "rota",\n'
    '    "filter": {"pedido_id": {"pedido": "id"}}\n'
    '  }\n'
    '}',
    "Mesmo estando no mesmo tipo de banco (MongoDB), pedido e rota vivem em "
    "bancos logicos diferentes (oms e fms). A consulta recupera o pedido e, com "
    "seu id, localiza a rota cujo pedido_id corresponde, unificando dados de "
    "dois microsservicos distintos.",
    '{\n'
    '  "pedido": [{"id": "P-131", "cliente_id": "1", "status": "EM_ROTA"}],\n'
    '  "rota": [{"id": "R-55", "pedido_id": "P-131",\n'
    '            "veiculo_placa": "ABC1D23", "destino": "Rio de Janeiro"}]\n'
    '}',
)

caso(
    3,
    "Rastreamento em Tempo Real (OMS -> FMS -> Redis)",
    "O cliente quer saber a posicao atual de seu pedido no mapa. E preciso "
    "encadear tres etapas: encontrar o pedido (OMS), descobrir o veiculo da "
    "rota (FMS) e, por fim, ler a ultima coordenada GPS no Redis.",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "pedido",\n'
    '  "filter": {"id": "P-131"},\n'
    '  "on_result": {\n'
    '    "service": "mongodb",\n'
    '    "database": "fms",\n'
    '    "schema": "rotas",\n'
    '    "alias": "rota",\n'
    '    "filter": {"pedido_id": {"pedido": "id"}},\n'
    '    "on_result": {\n'
    '      "service": "redis",\n'
    '      "database": "0",\n'
    '      "alias": "posicao",\n'
    '      "filter": {"placa": {"rota": "veiculo_placa"}}\n'
    '    }\n'
    '  }\n'
    '}',
    "Este e um exemplo de encadeamento em tres niveis atravessando os tres "
    "paradigmas de banco. O pedido leva a rota; a rota fornece a placa do "
    "veiculo; e a placa e usada como chave no Redis para obter a ultima posicao "
    "conhecida. Uma unica requisicao HTTP substitui tres consultas manuais em "
    "sistemas distintos.",
    '{\n'
    '  "pedido": [{"id": "P-131", "status": "EM_ROTA"}],\n'
    '  "rota": [{"id": "R-55", "veiculo_placa": "ABC1D23"}],\n'
    '  "posicao": [{"placa": "ABC1D23", "valor": "-22.9068,-43.1729"}]\n'
    '}',
)

caso(
    4,
    "Enderecos de Entrega de um Cliente (CMS clientes -> CMS enderecos)",
    "Para emitir uma etiqueta de envio, o operador precisa dos enderecos de "
    "entrega de um cliente. Ambas as informacoes estao no MySQL (CMS), em "
    "tabelas normalizadas diferentes.",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "cms",\n'
    '  "schema": "clientes",\n'
    '  "alias": "cliente",\n'
    '  "filter": {"documento": "12345678000199"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "cms",\n'
    '    "schema": "enderecos",\n'
    '    "alias": "enderecos",\n'
    '    "filter": {"cliente_id": {"cliente": "id"}}\n'
    '  }\n'
    '}',
    "Aqui o cruzamento ocorre dentro do mesmo banco relacional, demonstrando "
    "que o sistema tambem substitui, de forma unificada, os JOINs manuais "
    "tradicionais - com a vantagem de usar a mesma sintaxe empregada para "
    "bancos heterogeneos.",
    '{\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda",\n'
    '               "documento": "12345678000199"}],\n'
    '  "enderecos": [\n'
    '    {"id": "E-1", "cliente_id": "1", "tipo": "ENTREGA",\n'
    '     "cidade": "Rio de Janeiro", "uf": "RJ"}\n'
    '  ]\n'
    '}',
)

caso(
    5,
    "Notas Fiscais de um Cliente (CMS -> FNMS)",
    "O setor financeiro precisa listar todas as notas fiscais emitidas para um "
    "determinado cliente. O cadastro esta no CMS (MySQL) e o financeiro no FNMS "
    "(MySQL), em bancos separados.",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "cms",\n'
    '  "schema": "clientes",\n'
    '  "alias": "cliente",\n'
    '  "filter": {"id": "1"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "fnms",\n'
    '    "schema": "notas_fiscais",\n'
    '    "alias": "notas",\n'
    '    "filter": {"cliente_id": {"cliente": "id"}}\n'
    '  }\n'
    '}',
    "A consulta cruza dois bancos MySQL logicamente separados (cadastro e "
    "financeiro), reunindo em uma unica resposta o cliente e suas notas "
    "fiscais.",
    '{\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda"}],\n'
    '  "notas": [\n'
    '    {"id": "NF-900", "cliente_id": "1", "valor_total": 1580.0},\n'
    '    {"id": "NF-912", "cliente_id": "1", "valor_total": 240.5}\n'
    '  ]\n'
    '}',
)

caso(
    6,
    "Projecao de Campos: Contatos para Campanha (CMS)",
    "O time de marketing deseja apenas nome e email dos clientes de um "
    "determinado estado, sem trazer os demais campos sensiveis. Isso e feito "
    "com o campo project.",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "cms",\n'
    '  "schema": "clientes",\n'
    '  "alias": "contatos",\n'
    '  "filter": {"uf": "RJ"},\n'
    '  "project": ["nome", "email"]\n'
    '}',
    "O campo project restringe as colunas retornadas, reduzindo trafego e "
    "expondo apenas o necessario - importante em contextos de privacidade "
    "(LGPD).",
    '{\n'
    '  "contatos": [\n'
    '    {"nome": "Acme Ltda", "email": "contato@acme.com"},\n'
    '    {"nome": "Beta SA", "email": "vendas@beta.com"}\n'
    '  ]\n'
    '}',
)

caso(
    7,
    "Localizacao Fisica de um Produto (SMS)",
    "O operador de armazem precisa saber em qual galpao e setor um produto "
    "esta armazenado, a partir do seu SKU. Os dados estao hierarquizados no "
    "SMS (MySQL).",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "sms",\n'
    '  "schema": "produtos",\n'
    '  "alias": "produto",\n'
    '  "filter": {"sku": "SKU-777"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "sms",\n'
    '    "schema": "setores",\n'
    '    "alias": "setor",\n'
    '    "filter": {"id": {"produto": "setor_id"}}\n'
    '  }\n'
    '}',
    "A consulta encontra o produto pelo SKU e, com o setor_id retornado, "
    "localiza o setor correspondente, revelando a posicao exata do item no "
    "armazem.",
    '{\n'
    '  "produto": [{"id": "PR-3", "sku": "SKU-777",\n'
    '               "nome": "Cafe 1kg", "setor_id": "S-12"}],\n'
    '  "setor": [{"id": "S-12", "galpao_id": "G-1", "codigo": "A-04"}]\n'
    '}',
)

caso(
    8,
    "Itens de um Pedido e seu Estoque (OMS -> SMS)",
    "Antes de confirmar o despacho, o sistema verifica a disponibilidade em "
    "estoque dos itens de um pedido. O pedido esta no OMS (MongoDB) e o estoque "
    "no SMS (MySQL).",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "pedido",\n'
    '  "filter": {"id": "P-131"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "sms",\n'
    '    "schema": "produtos",\n'
    '    "alias": "estoque",\n'
    '    "filter": {"sku": {"pedido": "sku"}}\n'
    '  }\n'
    '}',
    "A consulta recupera o pedido no MongoDB e, para o SKU referenciado, "
    "consulta a quantidade disponivel no MySQL, unindo o mundo documental ao "
    "relacional.",
    '{\n'
    '  "pedido": [{"id": "P-131", "sku": "SKU-777", "quantidade": 2}],\n'
    '  "estoque": [{"sku": "SKU-777", "nome": "Cafe 1kg", "quantidade": 320}]\n'
    '}',
)

caso(
    9,
    "Cobrancas em Aberto e o Cliente (FNMS -> CMS)",
    "O setor de cobranca deseja, para uma cobranca vencida, recuperar os dados "
    "de contato do cliente. A cobranca esta no FNMS (MySQL) e o contato no CMS "
    "(MySQL).",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "fnms",\n'
    '  "schema": "notas_fiscais",\n'
    '  "alias": "nota",\n'
    '  "filter": {"id": "NF-912"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "cms",\n'
    '    "schema": "clientes",\n'
    '    "alias": "cliente",\n'
    '    "filter": {"id": {"nota": "cliente_id"}}\n'
    '  }\n'
    '}',
    "Partindo de uma nota fiscal, a consulta recupera o cliente responsavel, "
    "invertendo o sentido do Caso 5 e mostrando a flexibilidade das "
    "referencias.",
    '{\n'
    '  "nota": [{"id": "NF-912", "cliente_id": "1", "valor_total": 240.5}],\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda",\n'
    '               "email": "contato@acme.com", "telefone": "2199999-0000"}]\n'
    '}',
)

caso(
    10,
    "Veiculo Responsavel por um Pedido (OMS -> FMS rota -> FMS veiculo)",
    "A central de operacoes deseja saber qual motorista e veiculo estao "
    "responsaveis por um pedido, encadeando pedido, rota e veiculo.",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "pedido",\n'
    '  "filter": {"id": "P-131"},\n'
    '  "on_result": {\n'
    '    "service": "mongodb",\n'
    '    "database": "fms",\n'
    '    "schema": "rotas",\n'
    '    "alias": "rota",\n'
    '    "filter": {"pedido_id": {"pedido": "id"}},\n'
    '    "on_result": {\n'
    '      "service": "mongodb",\n'
    '      "database": "fms",\n'
    '      "schema": "veiculos",\n'
    '      "alias": "veiculo",\n'
    '      "filter": {"placa": {"rota": "veiculo_placa"}}\n'
    '    }\n'
    '  }\n'
    '}',
    "Encadeamento de tres niveis dentro do dominio de frota, mostrando que a "
    "profundidade das consultas nao tem limite pratico imposto pela sintaxe.",
    '{\n'
    '  "pedido": [{"id": "P-131"}],\n'
    '  "rota": [{"id": "R-55", "veiculo_placa": "ABC1D23"}],\n'
    '  "veiculo": [{"placa": "ABC1D23", "modelo": "VUC",\n'
    '               "motorista": "Joao Silva"}]\n'
    '}',
)

caso(
    11,
    "Relatorio 360 do Pedido (OMS -> CMS + FMS + FNMS)",
    "O gestor precisa de um relatorio completo de um pedido: dados do cliente "
    "(CMS), rota de entrega (FMS) e nota fiscal (FNMS). Este e o caso que "
    "melhor evidencia o valor do sistema.",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "pedido",\n'
    '  "filter": {"id": "P-131"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "cms",\n'
    '    "schema": "clientes",\n'
    '    "alias": "cliente",\n'
    '    "filter": {"id": {"pedido": "cliente_id"}}\n'
    '  }\n'
    '}',
    "Este caso parte do pedido e recupera o cliente. Em um cenario real, o "
    "gestor combinaria varias dessas cadeias (rota, nota fiscal) para montar o "
    "relatorio 360. Sem o TCC_CMA, seriam necessarias ao menos quatro consultas "
    "manuais em quatro sistemas com tecnologias diferentes.",
    '{\n'
    '  "pedido": [{"id": "P-131", "cliente_id": "1", "valor_total": 240.5}],\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda", "tipo": "PJ"}]\n'
    '}',
)

caso(
    12,
    "Consulta Isolada no Redis (posicao por placa)",
    "As vezes basta uma consulta simples e direta. Aqui, obtem-se a ultima "
    "posicao de um veiculo diretamente no Redis, sem encadeamento.",
    '{\n'
    '  "service": "redis",\n'
    '  "database": "0",\n'
    '  "alias": "posicao",\n'
    '  "filter": {"placa": "ABC1D23"}\n'
    '}',
    "Demonstra que o sistema tambem atende consultas simples de um unico banco, "
    "usando a mesma sintaxe declarativa. No Redis, o schema nao e necessario.",
    '{\n'
    '  "posicao": [{"placa": "ABC1D23", "valor": "-22.9068,-43.1729"}]\n'
    '}',
)

caso(
    13,
    "Meios de Pagamento de um Cliente (CMS)",
    "O checkout precisa recuperar os meios de pagamento tokenizados de um "
    "cliente para exibir opcoes salvas.",
    '{\n'
    '  "service": "mysql",\n'
    '  "database": "cms",\n'
    '  "schema": "clientes",\n'
    '  "alias": "cliente",\n'
    '  "filter": {"id": "1"},\n'
    '  "on_result": {\n'
    '    "service": "mysql",\n'
    '    "database": "cms",\n'
    '    "schema": "meios_pagamento",\n'
    '    "alias": "pagamentos",\n'
    '    "filter": {"cliente_id": {"cliente": "id"}},\n'
    '    "project": ["bandeira", "token"]\n'
    '  }\n'
    '}',
    "Combina encadeamento com projecao: apenas bandeira e token sao retornados, "
    "nunca o dado bruto do cartao, reforcando boas praticas de seguranca.",
    '{\n'
    '  "cliente": [{"id": "1", "nome": "Acme Ltda"}],\n'
    '  "pagamentos": [{"bandeira": "VISA", "token": "tok_9f8a2b"}]\n'
    '}',
)

caso(
    14,
    "Pedidos por Status para o Painel Operacional (OMS)",
    "O painel de operacoes lista todos os pedidos que estao em rota, para "
    "acompanhamento em tempo real.",
    '{\n'
    '  "service": "mongodb",\n'
    '  "database": "oms",\n'
    '  "schema": "pedidos",\n'
    '  "alias": "em_rota",\n'
    '  "filter": {"status": "EM_ROTA"},\n'
    '  "project": ["id", "cliente_id", "valor_total"]\n'
    '}',
    "Consulta de listagem com filtro por status e projecao, tipica de "
    "dashboards. Poderia ser encadeada com o Caso 3 para exibir a posicao de "
    "cada pedido no mapa.",
    '{\n'
    '  "em_rota": [\n'
    '    {"id": "P-131", "cliente_id": "1", "valor_total": 240.5},\n'
    '    {"id": "P-140", "cliente_id": "7", "valor_total": 99.9}\n'
    '  ]\n'
    '}',
)

h("5.15 Sintese dos Casos de Uso", 2)
para("O Quadro a seguir resume os casos apresentados, evidenciando a "
     "diversidade de combinacoes entre bancos e a natureza cross-database da "
     "solucao.")
table(
    ["Caso", "Fluxo", "Bancos envolvidos"],
    [
        ["1", "Cliente -> Pedidos", "MySQL + MongoDB"],
        ["2", "Pedido -> Rota", "MongoDB + MongoDB"],
        ["3", "Pedido -> Rota -> Posicao", "MongoDB + MongoDB + Redis"],
        ["4", "Cliente -> Enderecos", "MySQL + MySQL"],
        ["5", "Cliente -> Notas", "MySQL + MySQL"],
        ["6", "Contatos (projecao)", "MySQL"],
        ["7", "Produto -> Setor", "MySQL + MySQL"],
        ["8", "Pedido -> Estoque", "MongoDB + MySQL"],
        ["9", "Nota -> Cliente", "MySQL + MySQL"],
        ["10", "Pedido -> Rota -> Veiculo", "MongoDB x3"],
        ["11", "Relatorio 360", "MongoDB + MySQL"],
        ["12", "Posicao isolada", "Redis"],
        ["13", "Meios de pagamento", "MySQL + MySQL"],
        ["14", "Painel por status", "MongoDB"],
    ],
    caption="Quadro 11 - Sintese dos casos de uso cross-database",
)
para(
    "Alem dos casos apresentados, novas combinacoes podem ser criadas livremente "
    "pelo usuario, ja que a linguagem e composta por blocos reutilizaveis. "
    "Como sugestoes adicionais de exploracao, citam-se: (i) cruzar pagamentos "
    "(FNMS) com clientes inadimplentes para uma regua de cobranca; (ii) associar "
    "produtos proximos da validade (SMS) aos pedidos em aberto (OMS) para "
    "priorizacao de despacho; e (iii) relacionar rotas (FMS) por regiao com os "
    "enderecos de entrega (CMS) para otimizacao de carga. Todas seguem "
    "exatamente o mesmo padrao demonstrado neste capitulo."
)
page_break()


# ===========================================================================
# 6 TESTES E RESULTADOS
# ===========================================================================
h("6 TESTES E RESULTADOS", 1)
h("6.1 Estrategia de Testes", 2)
para(
    "Para garantir a confiabilidade e a robustez do sistema TCC_CMA, adotou-se "
    "uma estrategia de testes automatizados abrangente, focada na validacao "
    "unitaria e de integracao. Foram implementados cenarios que cobrem desde a "
    "conexao isolada com cada SGBD ate o fluxo complexo de consultas aninhadas. "
    "A bateria de testes valida nao apenas o sucesso das operacoes (caminho "
    "feliz), mas tambem o comportamento do sistema diante de falhas de conexao "
    "ou inconsistencia de dados."
)
h("6.2 Casos de Teste e Validacao", 2)
para("Os testes foram segmentados para validar as responsabilidades de cada "
     "componente da arquitetura:")
bullet("Conectividade e CRUD: testes especificos verificam a instanciacao "
       "correta das classes MysqlClient, MongodbClient e RedisClient atraves da "
       "Factory, validando as operacoes basicas em cada banco isoladamente.")
bullet("Processamento de Consultas: a logica do QueryModel foi submetida a "
       "testes que simulam requisicoes JSON variadas, garantindo o parsing "
       "correto dos parametros e a aplicacao dos filtros.")
bullet("Integracao e Recursividade: o ponto critico do sistema - as consultas "
       "aninhadas - foi validado com cenarios envolvendo multiplos bancos "
       "simultaneamente. O teste test_multiple_query_model_mysql_mongo simula a "
       "busca de um registro no MySQL cujo ID e utilizado para recuperar um "
       "documento correlato no MongoDB.")
table(
    ["Suite de testes", "Responsabilidade validada"],
    [
        ["test_databases_model.py", "Factory retorna o cliente correto por tipo"],
        ["test_model_query.py", "Consultas simples e aninhadas (todas as combinacoes)"],
        ["test_mysql_model.py", "Operacoes CRUD do cliente MySQL"],
        ["test_mongo_model.py", "Operacoes CRUD do cliente MongoDB"],
        ["test_redis_model.py", "Operacoes chave-valor do cliente Redis"],
    ],
    caption="Quadro 12 - Suites de teste do projeto",
)
h("6.3 Analise dos Resultados", 2)
para(
    "A execucao da suite de testes demonstrou a viabilidade tecnica da solucao "
    "proposta. O sistema foi capaz de orquestrar consultas envolvendo MySQL, "
    "MongoDB e Redis em uma unica transacao logica, com tempos de resposta "
    "adequados para o ambiente de testes. A abstracao criada pelas interfaces "
    "permitiu que o codigo cliente interagisse com diferentes tecnologias de "
    "persistencia sem necessidade de adaptacao, confirmando o desacoplamento "
    "arquitetural almejado. Alem disso, a conteinerizacao via Docker garantiu "
    "que o ambiente de execucao fosse replicavel, eliminando discrepancias de "
    "configuracao entre desenvolvimento e producao."
)
para(
    "A Figura 10 apresenta um exemplo de execucao de consulta com o resultado "
    "consolidado retornado pela aplicacao, evidenciando na pratica o "
    "comportamento descrito ao longo do Capitulo 5."
)
figure(10, "Figura 10 - Execucao de uma consulta e resultado consolidado")
page_break()


# ===========================================================================
# 7 CONCLUSAO
# ===========================================================================
h("7 CONCLUSAO", 1)
h("7.1 Consideracoes Finais", 2)
para(
    "O presente trabalho atingiu seu objetivo principal ao desenvolver e "
    "validar um sistema capaz de realizar consultas aninhadas em multiplos "
    "bancos de dados heterogeneos atraves de uma unica requisicao. A "
    "implementacao da arquitetura baseada em microsservicos, suportada pelos "
    "padroes de projeto Strategy e Factory, provou ser eficaz para criar uma "
    "camada de abstracao que isola a complexidade das tecnologias de "
    "persistencia subjacentes."
)
para(
    "Os testes realizados demonstraram que a solucao simplifica "
    "significativamente o consumo de dados em ambientes poliglota. Ao "
    "centralizar a logica de juncao de dados (application-side join) no "
    "servidor, reduziu-se a necessidade de multiplas chamadas de rede e o "
    "acoplamento entre o cliente e os detalhes de implementacao dos bancos de "
    "dados. O estudo de caso da empresa de logistica evidenciou a "
    "aplicabilidade pratica da ferramenta, permitindo a correlacao fluida entre "
    "dados cadastrais (CMS/MySQL), de pedidos (OMS/MongoDB), de frota "
    "(FMS/MongoDB e Redis), de estoque (SMS/MySQL) e financeiros (FNMS/MySQL)."
)
para(
    "O guia de usuario e o extenso conjunto de casos de uso apresentados neste "
    "documento reforcam que o sistema nao e apenas uma prova de conceito, mas "
    "uma ferramenta utilizavel: com poucos comandos o ambiente e disponibilizado "
    "e, por meio de uma linguagem declarativa simples, o usuario consegue "
    "construir consultas complexas que antes exigiriam conhecimento tecnico "
    "especializado em cada tecnologia."
)
h("7.2 Limitacoes e Trabalhos Futuros", 2)
para(
    "Apesar dos resultados satisfatorios, a solucao apresentada possui "
    "limitacoes que abrem caminhos para investigacoes futuras. A principal "
    "restricao identificada refere-se a performance em cenarios de alta "
    "volumetria: como o processamento de juncao ocorre em memoria na aplicacao "
    "(Python), consultas que retornam grandes conjuntos de dados podem impactar "
    "o tempo de resposta e o consumo de recursos. Alem disso, o sistema atual "
    "nao implementa mecanismos de transacao distribuida (SAGA pattern), o que "
    "significa que falhas parciais em uma cadeia de consultas podem resultar em "
    "estados inconsistentes."
)
para("Como sugestoes para trabalhos futuros, recomenda-se:")
bullet("Otimizacao de Performance: implementacao de estrategias de caching "
       "inteligente para resultados de sub-queries frequentes e paralelizacao "
       "de consultas independentes;")
bullet("Seguranca e Governanca: adicao de camadas de autenticacao (JWT), "
       "parametrizacao das consultas SQL para eliminar riscos de SQL injection "
       "e validacao granular de permissoes por tipo de banco e operacao;")
bullet("Expansao da Interoperabilidade: desenvolvimento de novos drivers para "
       "suportar outros SGBDs populares, como PostgreSQL e Cassandra, alem de "
       "permitir operacoes de agregacao complexa diretamente na camada de "
       "abstracao;")
bullet("Isolamento de Contexto: substituir o VarsSingleton global por um "
       "contexto por requisicao, evitando vazamento de dados entre consultas "
       "concorrentes.")
page_break()


# ===========================================================================
# REFERENCIAS
# ===========================================================================
h("REFERENCIAS", 1)
refs = [
    "FOWLER, Martin. Patterns of Enterprise Application Architecture. "
    "Addison-Wesley, 2002.",
    "GAMMA, Erich et al. Design Patterns: Elements of Reusable "
    "Object-Oriented Software. Addison-Wesley, 1994.",
    "GRINBERG, Miguel. Flask Web Development: Developing Web Applications with "
    "Python. O'Reilly Media, 2018.",
    "MongoDB Inc. MongoDB Documentation. Disponivel em: "
    "https://docs.mongodb.com/. Acesso em: 2025.",
    "MySQL. MySQL 8.0 Reference Manual. Disponivel em: "
    "https://dev.mysql.com/doc/. Acesso em: 2025.",
    "NEWMAN, Sam. Building Microservices: Designing Fine-Grained Systems. "
    "O'Reilly Media, 2015.",
    "PERKINS, Luc; REDMOND, Eric; WILSON, Jim R. Seven Databases in Seven "
    "Weeks. The Pragmatic Bookshelf, 2018.",
    "Redis Ltd. Redis Documentation. Disponivel em: "
    "https://redis.io/documentation. Acesso em: 2025.",
    "RICHARDSON, Chris. Microservices Patterns. Manning Publications, 2018.",
    "SADALAGE, Pramod J.; FOWLER, Martin. NoSQL Distilled: A Brief Guide to "
    "the Emerging World of Polyglot Persistence. Addison-Wesley, 2012.",
    "The Pallets Projects. Flask Documentation. Disponivel em: "
    "https://flask.palletsprojects.com/. Acesso em: 2025.",
]
for r in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(r)
    doc.add_paragraph()
page_break()


# ===========================================================================
# ANEXOS
# ===========================================================================
h("ANEXOS", 1)
para("Os anexos reunem capturas de tela adicionais da aplicacao em execucao, "
     "complementando as figuras apresentadas ao longo do texto.")
figure(7, "Anexo A - Tela de CRUD (MySQL)")
figure(9, "Anexo B - Tela de CRUD (MongoDB)")
figure(8, "Anexo C - Tela de CRUD (Redis)")
figure(10, "Anexo D - Chamada de consulta com resultado")
para("Repositorio do projeto: https://github.com/jlgsobreiro/TCC_CMA")


# ---------------------------------------------------------------------------
# Salvar
# ---------------------------------------------------------------------------
OUT = os.path.join(BASE, "TCC_SOBREIRO_EXPANDIDO.docx")
doc.save(OUT)
print("Documento gerado em:", OUT)
print("Total de paragrafos:", len(doc.paragraphs))
