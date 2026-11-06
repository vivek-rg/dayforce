"""Track 4/P03 owns checks; source writes never imply a legally/physically proven event."""

from sqlite3 import Connection

from app.shared.contracts import Evidence


def check_hire(connection: Connection, hire_id: str) -> list[Evidence]:
    # TODO P03: compare approved predicates to independent sources and persist scoped receipts.
    raise NotImplementedError("P03: check_hire")
