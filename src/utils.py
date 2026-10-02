"""Shared helpers: DuckDB connection and a runner for .sql files."""
from pathlib import Path
import duckdb

DB_PATH = "data/warehouse.duckdb"


def get_con():
    Path("data").mkdir(exist_ok=True)
    return duckdb.connect(DB_PATH)


def run_sql_file(con, path):
    """Run every statement in a .sql file (comment lines are ignored)."""
    text = Path(path).read_text()
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    for stmt in text.split(";"):
        if stmt.strip():
            con.execute(stmt)