from __future__ import annotations

from collections import defaultdict

from app.schemas.plans import PlanDefinition, PlanStatus


PLAN_CATALOG = {
    "FREE": {
        "name": "Free",
        "monthly_price_usd": 0.0,
        "max_ai_requests_per_day": 20,
        "max_meetings_per_month": 3,
        "features": ["basic_meeting_summary", "basic_search"],
    },
    "PRO": {
        "name": "Pro",
        "monthly_price_usd": 29.0,
        "max_ai_requests_per_day": 5000,
        "max_meetings_per_month": 50,
        "features": ["basic_meeting_summary", "basic_search", "meeting_memory", "integrations"],
    },
    "TEAM": {
        "name": "Team",
        "monthly_price_usd": 99.0,
        "max_ai_requests_per_day": 20000,
        "max_meetings_per_month": 200,
        "features": ["basic_meeting_summary", "basic_search", "meeting_memory", "integrations", "shared_workspaces", "analytics"],
    },
}

USAGE_KEYS = {
    "ai_requests": "max_ai_requests_per_day",
    "meetings": "max_meetings_per_month",
}


class PlanService:
    def __init__(self) -> None:
        self._usage_by_user: dict[str, dict[str, int]] = defaultdict(dict)

    def list_plans(self) -> list[PlanDefinition]:
        return [
            PlanDefinition(
                key=key,
                name=definition["name"],
                monthly_price_usd=definition["monthly_price_usd"],
                max_ai_requests_per_day=definition["max_ai_requests_per_day"],
                max_meetings_per_month=definition["max_meetings_per_month"],
                features=definition["features"],
            )
            for key, definition in PLAN_CATALOG.items()
        ]

    def get_status(self, user) -> PlanStatus:
        plan_key = (user.plan or "FREE").upper()
        plan = PLAN_CATALOG.get(plan_key, PLAN_CATALOG["FREE"])
        usage = self._usage_by_user.get(user.id, {})
        limits = {
            "ai_requests": plan["max_ai_requests_per_day"],
            "meetings": plan["max_meetings_per_month"],
        }
        remaining = {
            key: max(limit - usage.get(key, 0), 0)
            for key, limit in limits.items()
        }
        return PlanStatus(
            plan=plan_key,
            plan_name=plan["name"],
            features=plan["features"],
            usage={key: usage.get(key, 0) for key in limits},
            limits=limits,
            remaining=remaining,
            is_over_limit=any(usage.get(key, 0) > limit for key, limit in limits.items()),
        )

    def set_plan(self, user, plan_key: str) -> PlanStatus:
        normalized = (plan_key or "FREE").upper()
        if normalized not in PLAN_CATALOG:
            raise ValueError(f"Unsupported plan: {plan_key}")
        user.plan = normalized
        return self.get_status(user)

    def record_usage(self, user, feature: str, amount: int = 1) -> PlanStatus:
        normalized_feature = (feature or "ai_requests").lower()
        if normalized_feature not in USAGE_KEYS:
            raise ValueError(f"Unsupported usage feature: {feature}")

        plan_key = (user.plan or "FREE").upper()
        plan = PLAN_CATALOG.get(plan_key, PLAN_CATALOG["FREE"])
        limit = plan[USAGE_KEYS[normalized_feature]]
        usage = self._usage_by_user.setdefault(user.id, {})
        current = usage.get(normalized_feature, 0)
        next_total = current + amount
        if next_total > limit:
            raise ValueError(f"Usage limit exceeded for {normalized_feature} on the {plan_key} plan.")
        usage[normalized_feature] = next_total
        return self.get_status(user)


service = PlanService()
