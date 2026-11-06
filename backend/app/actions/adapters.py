"""Simulated provisioning. No real directory, email or VPN system is contacted."""

from typing import Protocol


class ProvisioningAdapter(Protocol):
    def request_access(self, hire_id: str, item: str, detail: str) -> dict: ...


class SimulatedProvisioningAdapter:
    """Returns the record a real IT system might hold. It is always labelled simulated."""

    def request_access(self, hire_id: str, item: str, detail: str) -> dict:
        return {
            "category": "it_access",
            "item": item,
            "detail": detail,
            "state": "REQUESTED",
            "simulated": True,
        }


provisioning: ProvisioningAdapter = SimulatedProvisioningAdapter()
