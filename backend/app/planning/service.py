"""Track 4/P03: deterministic policies, tasks, deadlines and location impact preview."""

from sqlite3 import Connection

from app.shared.contracts import Hire, Location, Plan, PlanDiff


def create_plan(connection: Connection, hire: Hire) -> Plan:
    # TODO P03: supported approved rules only, unique logical keys, resolved owners, cycle checks.
    raise NotImplementedError("P03: create_plan")


def preview_location_change(
    connection: Connection, hire_id: str, location_id: Location
) -> PlanDiff:
    # TODO P03: exact create/cancel/preserve/invalidate diff; no mutation here.
    raise NotImplementedError("P03: preview_location_change")
