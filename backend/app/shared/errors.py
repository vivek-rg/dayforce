from fastapi import HTTPException


def not_implemented() -> None:
    raise HTTPException(
        status_code=501,
        detail={
            "code": "FEATURE_NOT_IMPLEMENTED",
            "message": "Contract reserved. Feature phase is not implemented.",
            "details": [],
        },
    )
