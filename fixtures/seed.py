"""Safe synthetic seed. Refuses a database that already has business data; it never resets one.

Run from the repository root with a private DEMO_PASSWORD of at least 12 characters:
    node scripts/python.mjs fixtures/seed.py
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.auth.service import hash_password, load_user  # noqa: E402
from app.knowledge.service import approve, create_draft  # noqa: E402
from app.planning.service import create_hire  # noqa: E402
from app.shared.contracts import HireCreate  # noqa: E402
from app.shared.db import connect, initialize  # noqa: E402
from app.shared.util import now_iso  # noqa: E402

FIXTURES = Path(__file__).resolve().parent
USERS = [
    ("U_HR", "Hema Rao (HR)", "HR"),
    ("U_IT", "Imran Shah (IT)", "IT"),
    ("U_PAYROLL", "Padma Iyer (Payroll)", "PAYROLL"),
    ("U_BENEFITS", "Ben Thomas (Benefits)", "BENEFITS"),
    ("U_TRAINING", "Tara Nair (Training)", "TRAINING"),
    ("U_MANAGER", "Manoj Verma (Manager)", "MANAGER"),
    ("U_MANAGER2", "Meena Das (Manager)", "MANAGER"),
    ("U_PRIYA", "Priya Sharma", "EMPLOYEE"),
    ("U_ARJUN", "Arjun Menon", "EMPLOYEE"),
    ("U_LEELA", "Leela Pillai", "EMPLOYEE"),
    ("U_RAVI", "Ravi Kumar", "EMPLOYEE"),
]
DEPARTMENTS = [
    ("DEP_ENG", "Engineering"),
    ("DEP_SALES", "Sales"),
    ("DEP_OPS", "Operations"),
]
INVENTORY = [
    ("EQ_BLR_22", "LAPTOP_22", "BLR-DEMO", "Dell Latitude 7450", "Laptop", "SYN-BLR-0022"),
    ("EQ_BLR_23", "LAPTOP_23", "BLR-DEMO", "Dell Latitude 7450", "Laptop", "SYN-BLR-0023"),
    ("EQ_HYD_07", "LAPTOP_07", "HYD-DEMO", "Lenovo ThinkPad T14", "Laptop", "SYN-HYD-0007"),
    ("EQ_HYD_08", "LAPTOP_08", "HYD-DEMO", "Lenovo ThinkPad T14", "Laptop", "SYN-HYD-0008"),
    ("EQ_BLR_M1", "MONITOR_11", "BLR-DEMO", "27-inch monitor", "Monitor", "SYN-BLR-M011"),
]
KNOWLEDGE = [
    ("Leave Policy", "GENERAL", "leave_policy.md"),
    ("Reimbursement Policy", "GENERAL", "reimbursement_policy.md"),
    ("Onboarding Documents Guide", "GENERAL", "onboarding_documents.md"),
    ("Benefits Overview", "GENERAL", "benefits_overview.md"),
    ("Equipment Guide", "GENERAL", "equipment_guide.md"),
    ("Remote Work Policy", "GENERAL", "remote_work_policy.md"),
    ("Manager Onboarding Handbook", "MANAGER", "manager_handbook.md"),
    ("IT Provisioning Runbook", "IT", "it_runbook.md"),
    ("HR Compensation Bands", "HR", "hr_compensation.md"),
]


def _hire(name, role, location, mode, start, manager, employee, department, designation, worker):
    return HireCreate(
        display_name=name,
        worker_type=worker,
        role=role,
        location_id=location,
        work_mode=mode,
        start_date=start,
        manager_user_id=manager,
        employee_user_id=employee,
        department_id=department,
        designation=designation,
        work_email=f"{name.split()[0].lower()}@northstar.example",
    )


def seed_reference(connection, password: str) -> None:
    password_hash = hash_password(password)
    for user_id, name, role in USERS:
        connection.execute(
            "INSERT INTO users (id, display_name, role, password_hash) VALUES (?,?,?,?)",
            (user_id, name, role, password_hash),
        )
    connection.executemany("INSERT INTO departments VALUES (?,?)", DEPARTMENTS)
    pack = json.loads((FIXTURES / "policy_pack.json").read_text(encoding="utf-8"))
    connection.execute(
        "INSERT INTO policies (id, version, approved_by, effective_from, effective_to, scope_json, "
        "sections_json, rules_json) VALUES (?,?,?,?,?,?,?,?)",
        (
            pack["id"],
            pack["version"],
            "U_HR",
            pack["effective_from"],
            pack["effective_to"],
            json.dumps(pack["scope"]),
            json.dumps(pack["sections"]),
            json.dumps(pack["rules"]),
        ),
    )
    for record_id, tag, location, name, kind, serial in INVENTORY:
        payload = {
            "category": "equipment",
            "asset_tag": tag,
            "location_id": location,
            "state": "AVAILABLE",
            "assignee_hire_id": None,
            "handover_at": None,
            "asset_name": name,
            "asset_type": kind,
            "serial_number": serial,
        }
        connection.execute(
            "INSERT INTO source_records (id, hire_id, category, source_system, external_id, "
            "version, payload_json, observed_at, updated_by) "
            "VALUES (?,NULL,'equipment','demo',?,1,?,?,'U_IT')",
            (record_id, record_id, json.dumps(payload), now_iso()),
        )
    for title, access, filename in KNOWLEDGE:
        body = (FIXTURES / "knowledge" / filename).read_text(encoding="utf-8")
        document = create_draft(connection, title, access, body, "U_HR")
        approve(connection, document.id, document.version, "U_HR")


def seed_demo_hires(connection) -> None:
    """Three people already in progress, so dashboards have real data before the live story.

    Priya's account is left free on purpose: HR creates her during the recorded journey.
    """
    today = date.today()
    hr = load_user(connection, "U_HR")
    arjun = create_hire(
        connection,
        _hire(
            "Arjun Menon",
            "sales_associate",
            "BLR-DEMO",
            "remote",
            today + timedelta(days=2),
            "U_MANAGER2",
            "U_ARJUN",
            "DEP_SALES",
            "Account Executive",
            "employee",
        ),
        hr,
    )
    create_hire(
        connection,
        _hire(
            "Leela Pillai",
            "operations_associate",
            "HYD-DEMO",
            "office",
            today + timedelta(days=12),
            "U_MANAGER2",
            "U_LEELA",
            "DEP_OPS",
            "Operations Associate",
            "contractor",
        ),
        hr,
    )
    create_hire(
        connection,
        _hire(
            "Ravi Kumar",
            "engineer",
            "HYD-DEMO",
            "office",
            today + timedelta(days=20),
            "U_MANAGER",
            "U_RAVI",
            "DEP_ENG",
            "Backend Engineer",
            "employee",
        ),
        hr,
    )
    # Arjun starts in two days, so some of his tasks are genuinely past due. Nothing is faked.
    connection.execute(
        "UPDATE tasks SET due_date=? WHERE hire_id=? AND logical_key='ACCOUNT_EMAIL'",
        ((today - timedelta(days=2)).isoformat(), arjun.id),
    )


def seed(password: str, *, demo_hires: bool = True) -> None:
    if len(password) < 12:
        raise SystemExit("Set DEMO_PASSWORD to at least 12 characters before seeding.")
    initialize()
    with connect() as connection:
        if connection.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            raise SystemExit("This database already has data. Seeding refuses to overwrite it.")
        seed_reference(connection, password)
        if demo_hires:
            seed_demo_hires(connection)


if __name__ == "__main__":
    seed(os.getenv("DEMO_PASSWORD", ""))
    print("Synthetic demo data created. Sign in with your private DEMO_PASSWORD.")
