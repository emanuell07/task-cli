# ✅ TaskCLI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-database-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

Gerenciador de tarefas via linha de comando (CLI) feito em Python com banco de dados SQLite. Projeto desenvolvido para praticar CRUD, `argparse`, tratamento de erros e manipulação de datas.

---

## 📋 Funcionalidades

- ✅ Criar, listar, editar, concluir e deletar tarefas
- 🔴 🟡 🟢 Sistema de **prioridade** (alta, média, baixa)
- 📅 Controle de **prazo** com alertas de atraso
- 💾 Persistência local via **SQLite** (sem configuração extra)
- 🎨 Saída colorida no terminal

---

## 🚀 Como usar

### Pré-requisitos

- Python 3.10 ou superior
- Nenhuma dependência externa — só biblioteca padrão!

### Instalação

```bash
git clone https://github.com/SEU_USUARIO/task-cli.git
cd task-cli
```

### Comandos

```bash
# Adicionar tarefa
python taskmanager.py adicionar "Estudar Python" --prioridade alta --prazo 2025-06-01

# Listar tarefas pendentes
python taskmanager.py listar

# Listar todas (incluindo concluídas)
python taskmanager.py listar --todas

# Filtrar por prioridade
python taskmanager.py listar --prioridade alta

# Ver detalhes de uma tarefa
python taskmanager.py ver 1

# Editar tarefa
python taskmanager.py editar 1 --prazo 2025-07-01 --prioridade media

# Marcar como concluída
python taskmanager.py concluir 1

# Deletar tarefa
python taskmanager.py deletar 1
```

---

## 📸 Exemplo de saída

```
  ID    TÍTULO                              PRIORIDADE   PRAZO                  STATUS
  ─────────────────────────────────────────────────────────────────────────────────────
  4     Revisar projeto do portfólio        🔴 Alta      2026-04-30             ○ Pendente
  1     Estudar argparse no Python          🔴 Alta      ⚠ Atrasado (2025-05-10) ○ Pendente
  3     Ler livro de SQL                    🟢 Baixa     Sem prazo              ○ Pendente

  Total: 3 | Concluídas: 0 | Pendentes: 3
```

---

## 🗂 Estrutura do projeto

```
task-cli/
├── taskmanager.py   # Aplicação principal
├── .gitignore       # Ignora o banco de dados local
└── README.md
```

O banco de dados é criado automaticamente em `~/.taskcli.db` na primeira execução.

---

## 🧠 Conceitos praticados

| Conceito | Implementação |
|---|---|
| CRUD completo | `INSERT`, `SELECT`, `UPDATE`, `DELETE` via SQLite |
| CLI com subcomandos | `argparse` com `add_subparsers` |
| Tratamento de erros | Validação de datas, prioridades e IDs |
| Data e hora | `datetime`, cálculo de dias restantes |
| Organização do código | Funções separadas por responsabilidade |

---

## 🛣 Próximos passos

- [ ] Migrar para PostgreSQL com `psycopg2`
- [ ] Exportar tarefas para CSV
- [ ] Adicionar testes com `pytest`
- [ ] Interface interativa com `rich`

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
