from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from typing import Any, Iterable


class StateStore:
    """Event-sourced durable state. Persistence does not imply persistent identity."""
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(
            "create table if not exists events(seq integer primary key autoincrement, kind text, payload text, created_ns integer)"
        )
        # Query acceleration only. The append-only event table remains the authority surface.
        # This index carries no ordering/currentness/semantic authority beyond exact SQL selection.
        self.conn.execute("create index if not exists idx_events_kind_seq on events(kind, seq desc)")
        self.conn.execute(
            "create table if not exists kv(k text primary key, value text, updated_ns integer)"
        )
        self.conn.commit()

    @staticmethod
    def _decode_event_row(row: tuple[Any, ...]) -> dict[str, Any]:
        return {"seq":row[0],"kind":row[1],"payload":json.loads(row[2]),"created_ns":row[3]}

    def append(self, kind: str, payload: dict[str, Any]) -> int:
        cur = self.conn.execute("insert into events(kind,payload,created_ns) values(?,?,?)",
                                (kind, json.dumps(payload, sort_keys=True), time.time_ns()))
        self.conn.commit()
        return int(cur.lastrowid)

    def events(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("select seq,kind,payload,created_ns from events order by seq").fetchall()
        return [self._decode_event_row(r) for r in rows]

    def latest_event_seq(self, kind: str) -> int | None:
        """Return the exact latest sequence for one event kind without materializing history."""
        row = self.conn.execute(
            "select seq from events where kind=? order by seq desc limit 1", (str(kind),)
        ).fetchone()
        return None if row is None else int(row[0])

    def events_after(
        self,
        seq: int,
        *,
        kinds: Iterable[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return an exact append-order suffix without decoding pre-suffix history.

        Optional kinds restrict rows at SQL selection time. ``limit`` bounds returned rows in
        ascending sequence order; omission means the full suffix. This is a query surface only:
        it does not alter append-only history or grant event/currentness authority.
        """
        params: list[Any] = [int(seq)]
        where = "seq>?"
        if kinds is not None:
            normalized = tuple(dict.fromkeys(str(kind) for kind in kinds))
            if not normalized:
                return []
            where += " and kind in (" + ",".join("?" for _ in normalized) + ")"
            params.extend(normalized)
        sql = f"select seq,kind,payload,created_ns from events where {where} order by seq"
        if limit is not None:
            bound = int(limit)
            if bound <= 0:
                return []
            sql += " limit ?"
            params.append(bound)
        rows = self.conn.execute(sql, tuple(params)).fetchall()
        return [self._decode_event_row(r) for r in rows]

    def set(self, key: str, value: Any) -> None:
        self.conn.execute(
            "insert into kv(k,value,updated_ns) values(?,?,?) on conflict(k) do update set value=excluded.value,updated_ns=excluded.updated_ns",
            (key, json.dumps(value, sort_keys=True), time.time_ns()),
        )
        self.conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        row = self.conn.execute("select value from kv where k=?", (key,)).fetchone()
        return default if row is None else json.loads(row[0])
