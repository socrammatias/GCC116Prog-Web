# Projeto: Agenda de Estudos (GAC116 - Programação Web)

![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

Este repositório contém o código-fonte de uma aplicação web de **Agenda de Estudos**, desenvolvida como projeto para a disciplina GAC116 - Programação Web.

A aplicação é construída com o framework Django e permite que os usuários se cadastrem, gerenciem suas matérias acadêmicas, controlem suas tarefas e agendem suas provas.

## Funcionalidades Principais

* **Autenticação de Usuários:** Sistema completo de Cadastro, Login e Logout. Cada usuário tem acesso apenas aos seus próprios dados.
* **Gerenciamento de Matérias (CRUD):** Os usuários podem Criar, Ler, Atualizar e Deletar suas próprias matérias (ex: "Cálculo I", "Programação Web").
* **Gerenciamento de Tarefas (CRUD):** Os usuários podem Criar, Ler, Atualizar e Deletar tarefas, associando cada uma a uma matéria.
* **Gerenciamento de Provas (CRUD):** Os usuários podem cadastrar provas, vinculando-as a uma matéria, definindo a data, observações e um link para material de apoio.
* **Atributos de Tarefa:** Cada tarefa possui título, descrição, data de início, data de fim, status (A Fazer, Em Andamento, Concluída) e prioridade (Baixa, Média, Alta).
* **Filtragem Avançada:** A página "Minhas Tarefas" possui um painel de filtros que permite ao usuário encontrar tarefas por Matéria, Status ou Prioridade.
* **Painel Administrativo:** O painel de administração do Django (`/admin`) está configurado para o gerenciamento de dados brutos.

## Estrutura Organizacional dos Arquivos

A estrutura do projeto segue o padrão recomendado pelo Django, separando as configurações do projeto da lógica da aplicação.

```
AGENDAESTUDOS/
├── agenda/           # App principal da aplicação
│   ├── migrations/     # Arquivos de migração do banco de dados
│   ├── templates/      # Arquivos HTML (páginas do site)
│   ├── __init__.py
│   ├── admin.py        # Configuração do painel de admin
│   ├── apps.py
│   ├── forms.py        # (ATUALIZADO) Formulários de Cadastro, Matéria, Tarefa e Prova
│   ├── models.py       # (ATUALIZADO) Definição das tabelas Matéria, Tarefa e Prova
│   ├── tests.py
│   ├── urls.py         # Rotas (URLs) específicas deste app
│   └── views.py        # Lógica do backend (funções que renderizam as páginas)
│
├── agendaestudos/    # Pasta de configuração do projeto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py     # Configurações globais do projeto (apps, banco de dados, etc.)
│   ├── urls.py         # Arquivo de rotas principal do projeto
│   └── wsgi.py
│
├── venv/             # Pasta do ambiente virtual (ignorada pelo Git)
├── .gitignore        # Arquivo que define quais arquivos o Git deve ignorar
├── db.sqlite3        # Arquivo do banco de dados SQLite
├── manage.py         # Script utilitário para interagir com o Django
└── requirements.txt  # Lista de bibliotecas Python necessárias para o projeto
```

## Como Executar o Projeto Localmente

Siga os passos abaixo para rodar a aplicação em sua máquina.

**Pré-requisitos:**
* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)

### 1. Clonar o Repositório

Primeiro, clone este repositório para o seu computador:
```bash
git clone [https://github.com/socrammatias/GCC116Prog-Web.git](https://github.com/socrammatias/GCC116Prog-Web.git)
cd agenda-estudos
```

### 2. Criar e Ativar o Ambiente Virtual (`venv`)

É uma boa prática criar um ambiente virtual para isolar as dependências do projeto.
```bash
# Criar o ambiente virtual
python -m venv venv
```

**Para ativar o `venv` no Windows (PowerShell):**
```bash
.\venv\Scripts\activate
```

### 3. Instalar as Dependências (`requirements`)

Com o ambiente virtual ativo, instale todas as bibliotecas listadas no arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Executar as Migrações

Este comando irá sincronizar o estado do seu banco de dados com os modelos definidos no código (incluindo o novo modelo `Prova`).
```bash
python manage.py migrate
```

### 5. Executar o Projeto

Finalmente, inicie o servidor de desenvolvimento do Django:
```bash
python manage.py runserver
```

A aplicação estará disponível no seu navegador no endereço:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### Integrantes

* Layon Walker
* Marcos Vinícius Matias
* Ruan Victor Henrique
