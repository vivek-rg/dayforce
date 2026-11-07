import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "backend"))

from app.actions.service import _active_or_manual_case, save_proposal  # noqa: E402
from app.auth.service import load_user  # noqa: E402
from app.evidence.service import check_hire  # noqa: E402
from app.planning.service import apply_location_change, refresh_completion  # noqa: E402
from app.shared.contracts import InvestigationContext, ReservationAction  # noqa: E402
from app.shared.db import connect  # noqa: E402


def set_state(mode: str):
    with connect() as conn:
        priya = conn.execute("SELECT id FROM hires WHERE display_name LIKE '%Priya%'").fetchone()
        if not priya:
            print("Priya not found in database.")
            return
        priya_id = priya["id"]

        if mode == "conflict":
            conn.execute(
                "UPDATE hires SET location_id='HYD-DEMO', profile_version=profile_version+1, "
                "employment_status='PRE_JOINING' WHERE id=?",
                (priya_id,),
            )
            # Remove any unapproved equipment proposal for EQ_BLR_23
            conn.execute("DELETE FROM proposals WHERE payload_json LIKE '%EQ_BLR_23%'")
            check_hire(conn, priya_id)
            refresh_completion(conn, priya_id)
            print("Priya set to CONFLICT mode:")
            print("  Location: Hyderabad (HYD-DEMO)")
            print("  Document: Bengaluru (BLR-DEMO)")
            print("  Check: BLOCKED: PROFILE_DOCUMENT_LOCATION_CONFLICT")
            print("  Status: BLOCKED")

        elif mode == "resolve":
            apply_location_change(conn, priya_id, "BLR-DEMO", "U_HR")
            check_hire(conn, priya_id)
            refresh_completion(conn, priya_id)

            it_user = load_user(conn, "U_IT")
            existing_prop = conn.execute(
                "SELECT p.id FROM proposals p LEFT JOIN decisions d ON d.proposal_id=p.id "
                "WHERE p.action_type='RESERVE_EQUIPMENT' AND p.payload_json LIKE '%EQ_BLR_23%' "
                "AND d.proposal_id IS NULL"
            ).fetchone()
            if not existing_prop:
                case_id = _active_or_manual_case(conn, priya_id, it_user)
                ctx = InvestigationContext(case_id=case_id, hire_id=priya_id, user=it_user)
                payload = ReservationAction(
                    action_type="RESERVE_EQUIPMENT", equipment_record_id="EQ_BLR_23"
                )
                prop = save_proposal(conn, ctx, payload, [])
                print("  IT Proposal created:", prop.id)

            print("Priya set to RESOLVED mode:")
            print("  Location: Bengaluru (BLR-DEMO)")
            print("  Check: VERIFIED: LOCATION_MATCHES")
            print("  IT Review Inbox: Awaiting decision for EQ_BLR_23")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "conflict"
    set_state(mode)
