import uuid
from datetime import datetime, timedelta, timezone

from app.models.payment_plan import PaymentPlan, PlanType, PaymentStatus
from sqlalchemy.orm import Session


PAY_BASE_URL = "https://pay.nammaopen.in/upi"


def init_payment(db: Session, shop_id, plan: PlanType):
    plan_value = plan.value if hasattr(plan, "value") else str(plan)
    payment_link = f"{PAY_BASE_URL}?shop={shop_id}&plan={plan_value}"
    due_at = datetime.now(timezone.utc) + timedelta(days=30)

    record = (
        db.query(PaymentPlan)
        .filter(PaymentPlan.shop_id == shop_id)
        .one_or_none()
    )
    if record:
        record.plan = PlanType(plan_value)
        record.status = PaymentStatus.active
        record.payment_link = payment_link
        record.next_due_at = due_at
        record.updated_at = datetime.now(timezone.utc)
    else:
        record = PaymentPlan(
            id=uuid.uuid4(),
            shop_id=shop_id,
            plan=PlanType(plan_value),
            status=PaymentStatus.active,
            payment_link=payment_link,
            next_due_at=due_at,
        )
        db.add(record)
    db.commit()
    db.refresh(record)
    return record
