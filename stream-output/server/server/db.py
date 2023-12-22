from typing import Dict
import sqlite3
import json

con = sqlite3.connect("sandbox_sessions.sqlite")
cur = con.cursor()

sessions_table = "sessions"
outputs_table = "outputs"


def create_outputs_table():
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {outputs_table} (session_id TEXT PRIMARY KEY, outputs TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    con.commit()
    print("[DB] Table outputs created")


def create_sessions_table():
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {sessions_table} (id TEXT PRIMARY KEY, user_id TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    con.commit()
    print("[DB] Table sessions created")


def create_session(user_id: str, session_id: str):
    cur.execute(
        f'INSERT INTO {sessions_table} (id, user_id) VALUES ("{session_id}", "{user_id}")'
    )
    con.commit()


def get_user_sessions(user_id: str):
    cur.execute(f'SELECT * FROM {sessions_table} WHERE user_id = "{user_id}"')
    return cur.fetchall()


def get_session_outputs(session_id: str):
    cur.execute(f'SELECT * FROM {outputs_table} WHERE session_id = "{session_id}"')
    return cur.fetchall()


def insert_outputs(session_id: str, outputs: list[Dict[str, any]]):
    serialized = json.dumps(outputs)

    # Concat line to `output` in table
    cur.execute(
        f"INSERT OR REPLACE INTO {outputs_table} (session_id, outputs) VALUES (\"{session_id}\", '{serialized}')",
    )
    con.commit()
