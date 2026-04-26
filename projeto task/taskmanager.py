#!/usr/bin/env python3
"""
TaskCLI - Gerenciador de Tarefas via Linha de Comando
Banco de dados: SQLite | Funcionalidades: CRUD, prioridade, prazo
Uso: python taskmanager.py <comando> [opções]
"""

import argparse
import sqlite3
import sys
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path.home() / ".taskcli.db"

CORES = {
    "vermelho":  "\033[91m",
    "amarelo":   "\033[93m",
    "verde":     "\033[92m",
    "azul":      "\033[94m",
    "cinza":     "\033[90m",
    "negrito":   "\033[1m",
    "reset":     "\033[0m",
}

PRIORIDADES = {"alta": 1, "media": 2, "baixa": 3}
COR_PRIORIDADE = {"alta": "vermelho", "media": "amarelo", "baixa": "verde"}
LABEL_PRIORIDADE = {"alta": "🔴 Alta", "media": "🟡 Média", "baixa": "🟢 Baixa"}


def cor(texto: str, nome: str) -> str:
    return f"{CORES.get(nome, '')}{texto}{CORES['reset']}"


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco() -> None:
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo    TEXT    NOT NULL,
                descricao TEXT    DEFAULT '',
                prioridade TEXT   NOT NULL DEFAULT 'media'
                          CHECK(prioridade IN ('alta','media','baixa')),
                prazo     TEXT,
                concluida INTEGER NOT NULL DEFAULT 0,
                criada_em TEXT    NOT NULL
            )
        """)


def formatar_prazo(prazo_str: str | None) -> str:
    if not prazo_str:
        return cor("Sem prazo", "cinza")
    try:
        prazo = date.fromisoformat(prazo_str)
        hoje = date.today()
        delta = (prazo - hoje).days
        if delta < 0:
            return cor(f"⚠ Atrasado ({prazo_str})", "vermelho")
        elif delta == 0:
            return cor(f"Hoje ({prazo_str})", "amarelo")
        elif delta <= 3:
            return cor(f"Em {delta}d ({prazo_str})", "amarelo")
        return cor(prazo_str, "azul")
    except ValueError:
        return prazo_str


def cmd_adicionar(args: argparse.Namespace) -> None:
    """Adiciona uma nova tarefa."""
    prazo = None
    if args.prazo:
        try:
            date.fromisoformat(args.prazo)
            prazo = args.prazo
        except ValueError:
            print(cor("Erro: prazo deve estar no formato AAAA-MM-DD.", "vermelho"))
            sys.exit(1)

    prioridade = args.prioridade.lower()
    if prioridade not in PRIORIDADES:
        print(cor(f"Erro: prioridade deve ser alta, media ou baixa.", "vermelho"))
        sys.exit(1)

    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO tarefas (titulo, descricao, prioridade, prazo, criada_em) VALUES (?,?,?,?,?)",
            (args.titulo, args.descricao or "", prioridade, prazo, datetime.now().isoformat()),
        )
        task_id = cursor.lastrowid

    print(cor(f"✓ Tarefa #{task_id} adicionada: ", "verde") + cor(args.titulo, "negrito"))


def cmd_listar(args: argparse.Namespace) -> None:
    """Lista tarefas com filtros opcionais."""
    filtros = []
    params = []

    if not args.todas:
        filtros.append("concluida = 0")

    if args.prioridade:
        filtros.append("prioridade = ?")
        params.append(args.prioridade.lower())

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
    ordem = "ORDER BY prioridade_ordem, prazo ASC NULLS LAST, id"

    query = f"""
        SELECT *, CASE prioridade
            WHEN 'alta'  THEN 1
            WHEN 'media' THEN 2
            WHEN 'baixa' THEN 3
        END AS prioridade_ordem
        FROM tarefas {where} {ordem}
    """

    with conectar() as conn:
        tarefas = conn.execute(query, params).fetchall()

    if not tarefas:
        print(cor("Nenhuma tarefa encontrada.", "cinza"))
        return

    print()
    print(cor(f"  {'ID':<5} {'TÍTULO':<35} {'PRIORIDADE':<12} {'PRAZO':<22} STATUS", "negrito"))
    print("  " + "─" * 85)

    for t in tarefas:
        status = cor("✓ Feita", "cinza") if t["concluida"] else cor("○ Pendente", "azul")
        prioridade_label = LABEL_PRIORIDADE.get(t["prioridade"], t["prioridade"])
        titulo = (t["titulo"][:33] + "..") if len(t["titulo"]) > 35 else t["titulo"]
        print(f"  {t['id']:<5} {titulo:<35} {prioridade_label:<20} {formatar_prazo(t['prazo']):<30} {status}")

    print()
    total = len(tarefas)
    concluidas = sum(1 for t in tarefas if t["concluida"])
    print(cor(f"  Total: {total} | Concluídas: {concluidas} | Pendentes: {total - concluidas}", "cinza"))
    print()


def cmd_concluir(args: argparse.Namespace) -> None:
    """Marca uma tarefa como concluída."""
    with conectar() as conn:
        cursor = conn.execute(
            "UPDATE tarefas SET concluida = 1 WHERE id = ? AND concluida = 0", (args.id,)
        )
        if cursor.rowcount == 0:
            tarefa = conn.execute("SELECT id FROM tarefas WHERE id = ?", (args.id,)).fetchone()
            if tarefa:
                print(cor(f"Tarefa #{args.id} já estava concluída.", "amarelo"))
            else:
                print(cor(f"Tarefa #{args.id} não encontrada.", "vermelho"))
            return

    print(cor(f"✓ Tarefa #{args.id} marcada como concluída!", "verde"))


def cmd_editar(args: argparse.Namespace) -> None:
    """Edita campos de uma tarefa existente."""
    with conectar() as conn:
        tarefa = conn.execute("SELECT * FROM tarefas WHERE id = ?", (args.id,)).fetchone()
        if not tarefa:
            print(cor(f"Tarefa #{args.id} não encontrada.", "vermelho"))
            sys.exit(1)

        campos = {}
        if args.titulo:
            campos["titulo"] = args.titulo
        if args.descricao is not None:
            campos["descricao"] = args.descricao
        if args.prioridade:
            if args.prioridade.lower() not in PRIORIDADES:
                print(cor("Erro: prioridade deve ser alta, media ou baixa.", "vermelho"))
                sys.exit(1)
            campos["prioridade"] = args.prioridade.lower()
        if args.prazo:
            try:
                date.fromisoformat(args.prazo)
                campos["prazo"] = args.prazo
            except ValueError:
                print(cor("Erro: prazo deve estar no formato AAAA-MM-DD.", "vermelho"))
                sys.exit(1)

        if not campos:
            print(cor("Nenhum campo para atualizar. Use --titulo, --prioridade ou --prazo.", "amarelo"))
            return

        set_clause = ", ".join(f"{k} = ?" for k in campos)
        conn.execute(f"UPDATE tarefas SET {set_clause} WHERE id = ?", (*campos.values(), args.id))

    print(cor(f"✓ Tarefa #{args.id} atualizada com sucesso.", "verde"))


def cmd_deletar(args: argparse.Namespace) -> None:
    """Remove uma tarefa permanentemente."""
    with conectar() as conn:
        tarefa = conn.execute("SELECT titulo FROM tarefas WHERE id = ?", (args.id,)).fetchone()
        if not tarefa:
            print(cor(f"Tarefa #{args.id} não encontrada.", "vermelho"))
            sys.exit(1)

        if not args.forcar:
            confirmacao = input(
                f"Deletar '{tarefa['titulo']}'? {cor('[s/N]', 'amarelo')} "
            ).strip().lower()
            if confirmacao not in ("s", "sim"):
                print(cor("Operação cancelada.", "cinza"))
                return

        conn.execute("DELETE FROM tarefas WHERE id = ?", (args.id,))

    print(cor(f"✓ Tarefa #{args.id} removida.", "verde"))


def cmd_ver(args: argparse.Namespace) -> None:
    """Exibe detalhes de uma tarefa específica."""
    with conectar() as conn:
        t = conn.execute("SELECT * FROM tarefas WHERE id = ?", (args.id,)).fetchone()

    if not t:
        print(cor(f"Tarefa #{args.id} não encontrada.", "vermelho"))
        sys.exit(1)

    status = cor("✓ Concluída", "verde") if t["concluida"] else cor("○ Pendente", "azul")
    print()
    print(cor(f"  Tarefa #{t['id']}", "negrito"))
    print(f"  {'Título:':<14} {t['titulo']}")
    print(f"  {'Descrição:':<14} {t['descricao'] or cor('(sem descrição)', 'cinza')}")
    print(f"  {'Prioridade:':<14} {LABEL_PRIORIDADE.get(t['prioridade'], t['prioridade'])}")
    print(f"  {'Prazo:':<14} {formatar_prazo(t['prazo'])}")
    print(f"  {'Status:':<14} {status}")
    print(f"  {'Criada em:':<14} {cor(t['criada_em'][:16], 'cinza')}")
    print()


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskmanager",
        description=cor("TaskCLI — Gerenciador de Tarefas", "negrito"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python taskmanager.py adicionar "Estudar Python" --prioridade alta --prazo 2025-06-01
  python taskmanager.py listar
  python taskmanager.py listar --prioridade alta --todas
  python taskmanager.py concluir 3
  python taskmanager.py editar 3 --prazo 2025-07-01 --prioridade media
  python taskmanager.py deletar 3
  python taskmanager.py ver 1
        """,
    )

    sub = parser.add_subparsers(dest="comando", metavar="comando")
    sub.required = True

    # --- adicionar ---
    p_add = sub.add_parser("adicionar", aliases=["add", "a"], help="Adiciona nova tarefa")
    p_add.add_argument("titulo", help="Título da tarefa")
    p_add.add_argument("-d", "--descricao", help="Descrição detalhada")
    p_add.add_argument(
        "-p", "--prioridade",
        choices=["alta", "media", "baixa"],
        default="media",
        help="Prioridade (padrão: media)",
    )
    p_add.add_argument("--prazo", help="Prazo no formato AAAA-MM-DD")
    p_add.set_defaults(func=cmd_adicionar)

    # --- listar ---
    p_list = sub.add_parser("listar", aliases=["ls", "l"], help="Lista tarefas")
    p_list.add_argument("-t", "--todas", action="store_true", help="Inclui tarefas concluídas")
    p_list.add_argument(
        "-p", "--prioridade",
        choices=["alta", "media", "baixa"],
        help="Filtra por prioridade",
    )
    p_list.set_defaults(func=cmd_listar)

    # --- concluir ---
    p_done = sub.add_parser("concluir", aliases=["done", "c"], help="Marca tarefa como concluída")
    p_done.add_argument("id", type=int, help="ID da tarefa")
    p_done.set_defaults(func=cmd_concluir)

    # --- editar ---
    p_edit = sub.add_parser("editar", aliases=["edit", "e"], help="Edita uma tarefa")
    p_edit.add_argument("id", type=int, help="ID da tarefa")
    p_edit.add_argument("--titulo", help="Novo título")
    p_edit.add_argument("--descricao", help="Nova descrição")
    p_edit.add_argument("--prioridade", choices=["alta", "media", "baixa"], help="Nova prioridade")
    p_edit.add_argument("--prazo", help="Novo prazo AAAA-MM-DD")
    p_edit.set_defaults(func=cmd_editar)

    # --- deletar ---
    p_del = sub.add_parser("deletar", aliases=["del", "rm"], help="Remove uma tarefa")
    p_del.add_argument("id", type=int, help="ID da tarefa")
    p_del.add_argument("-f", "--forcar", action="store_true", help="Sem confirmação")
    p_del.set_defaults(func=cmd_deletar)

    # --- ver ---
    p_ver = sub.add_parser("ver", aliases=["show", "v"], help="Exibe detalhes de uma tarefa")
    p_ver.add_argument("id", type=int, help="ID da tarefa")
    p_ver.set_defaults(func=cmd_ver)

    return parser


def main() -> None:
    inicializar_banco()
    parser = construir_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
