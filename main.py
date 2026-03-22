from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# -----------------------------
# DATA
# -----------------------------
plans = [
    {"id": 1, "name": "Basic", "duration_months": 1, "price": 1000, "includes_classes": False, "includes_trainer": False},
    {"id": 2, "name": "Standard", "duration_months": 3, "price": 2500, "includes_classes": True, "includes_trainer": False},
    {"id": 3, "name": "Premium", "duration_months": 6, "price": 5000, "includes_classes": True, "includes_trainer": True},
    {"id": 4, "name": "Elite", "duration_months": 12, "price": 9000, "includes_classes": True, "includes_trainer": True},
    {"id": 5, "name": "Student", "duration_months": 2, "price": 1500, "includes_classes": False, "includes_trainer": False}
]

memberships = []
membership_counter = 1

class_bookings = []
class_counter = 1

# -----------------------------
# HELPERS
# -----------------------------
def find_plan(plan_id):
    for p in plans:
        if p["id"] == plan_id:
            return p
    return None

def calculate_fee(price, duration, payment_mode, referral_code):
    discount = 0

    if duration >= 12:
        discount += 0.20
    elif duration >= 6:
        discount += 0.10

    total = price * (1 - discount)

    if referral_code:
        total *= 0.95

    if payment_mode == "emi":
        total += 200

    return total

# -----------------------------
# Q1
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to IronFit Gym"}

# -----------------------------
# Q2
# -----------------------------
@app.get("/plans")
def get_plans(min_price: Optional[int] = None, max_price: Optional[int] = None):
    result = plans
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    return {"total": len(result), "plans": result}

# -----------------------------
# Q5
# -----------------------------
@app.get("/plans/summary")
def summary():
    return {
        "total_plans": len(plans),
        "plans_with_classes": sum(p["includes_classes"] for p in plans),
        "plans_with_trainer": sum(p["includes_trainer"] for p in plans),
        "cheapest_plan": min(plans, key=lambda x: x["price"]),
        "most_expensive_plan": max(plans, key=lambda x: x["price"])
    }

# -----------------------------
# Q10
# -----------------------------
@app.get("/plans/filter")
def filter_plans(
    max_price: Optional[int] = None,
    max_duration: Optional[int] = None,
    includes_classes: Optional[bool] = None,
    includes_trainer: Optional[bool] = None
):
    result = plans

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if max_duration is not None:
        result = [p for p in result if p["duration_months"] <= max_duration]

    if includes_classes is not None:
        result = [p for p in result if p["includes_classes"] == includes_classes]

    if includes_trainer is not None:
        result = [p for p in result if p["includes_trainer"] == includes_trainer]

    return result

# -----------------------------
# Q16
# -----------------------------
@app.get("/plans/search")
def search_plans(keyword: str):
    result = []

    for p in plans:
        if keyword.lower() in p["name"].lower():
            result.append(p)
        elif keyword.lower() == "classes" and p["includes_classes"]:
            result.append(p)
        elif keyword.lower() == "trainer" and p["includes_trainer"]:
            result.append(p)

    return {"total_found": len(result), "matches": result}

# -----------------------------
# Q17
# -----------------------------
@app.get("/plans/sort")
def sort_plans(sort_by: str = "price"):
    allowed = ["price", "name", "duration_months"]
    if sort_by not in allowed:
        raise HTTPException(status_code=400)
    return sorted(plans, key=lambda x: x[sort_by])

# -----------------------------
# Q18
# -----------------------------
@app.get("/plans/page")
def paginate_plans(page: int = 1, limit: int = 2):
    total_pages = math.ceil(len(plans) / limit)
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": plans[start:end]
    }

# -----------------------------
# Q20
# -----------------------------
@app.get("/plans/browse")
def browse_plans(
    keyword: Optional[str] = None,
    includes_classes: Optional[bool] = None,
    includes_trainer: Optional[bool] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 2
):
    result = plans

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    if includes_classes is not None:
        result = [p for p in result if p["includes_classes"] == includes_classes]

    if includes_trainer is not None:
        result = [p for p in result if p["includes_trainer"] == includes_trainer]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return {"total": len(result), "data": result[start:end]}

# -----------------------------
# Q3 (ALWAYS LAST)
# -----------------------------
@app.get("/plans/{plan_id}")
def get_plan(plan_id: int):
    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

# -----------------------------
# Q4
# -----------------------------
@app.get("/memberships")
def get_memberships():
    return {"total": len(memberships), "memberships": memberships}

# -----------------------------
# Q6
# -----------------------------
class EnrollRequest(BaseModel):
    member_name: str = Field(min_length=2)
    plan_id: int = Field(gt=0)
    phone: str = Field(min_length=10)
    start_month: str = Field(min_length=3)
    payment_mode: str = "cash"
    referral_code: str = ""

# -----------------------------
# Q8 & Q9
# -----------------------------
@app.post("/memberships")
def create_membership(data: EnrollRequest):
    global membership_counter

    plan = find_plan(data.plan_id)
    if not plan:
        raise HTTPException(status_code=404)

    total_fee = calculate_fee(
        plan["price"],
        plan["duration_months"],
        data.payment_mode,
        data.referral_code
    )

    membership = {
        "membership_id": membership_counter,
        "member_name": data.member_name,
        "plan_name": plan["name"],
        "duration": plan["duration_months"],
        "monthly_cost": round(total_fee / plan["duration_months"], 2),
        "total_fee": total_fee,
        "status": "active"
    }

    memberships.append(membership)
    membership_counter += 1

    return membership

# -----------------------------
# Q11
# -----------------------------
class NewPlan(BaseModel):
    name: str = Field(min_length=2)
    duration_months: int = Field(gt=0)
    price: int = Field(gt=0)
    includes_classes: bool = False
    includes_trainer: bool = False

@app.post("/plans")
def add_plan(plan: NewPlan):
    for p in plans:
        if p["name"].lower() == plan.name.lower():
            raise HTTPException(status_code=400, detail="Duplicate plan")

    new = plan.dict()
    new["id"] = len(plans) + 1
    plans.append(new)
    return new

# -----------------------------
# Q12
# -----------------------------
@app.put("/plans/{plan_id}")
def update_plan(
    plan_id: int,
    price: Optional[int] = None,
    includes_classes: Optional[bool] = None,
    includes_trainer: Optional[bool] = None
):
    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404)

    if price is not None:
        plan["price"] = price
    if includes_classes is not None:
        plan["includes_classes"] = includes_classes
    if includes_trainer is not None:
        plan["includes_trainer"] = includes_trainer

    return plan

# -----------------------------
# Q13
# -----------------------------
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int):
    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404)

    for m in memberships:
        if m["plan_name"] == plan["name"]:
            raise HTTPException(status_code=400, detail="Active memberships exist")

    plans.remove(plan)
    return {"message": "Deleted"}

# -----------------------------
# Q14
# -----------------------------
class ClassBooking(BaseModel):
    member_name: str
    class_name: str
    class_date: str

@app.post("/classes/book")
def book_class(data: ClassBooking):
    global class_counter

    valid = any(m["member_name"] == data.member_name for m in memberships)
    if not valid:
        raise HTTPException(status_code=400, detail="No active membership")

    booking = data.dict()
    booking["id"] = class_counter
    class_bookings.append(booking)
    class_counter += 1

    return booking

@app.get("/classes/bookings")
def get_bookings():
    return class_bookings

# -----------------------------
# Q15
# -----------------------------
@app.delete("/classes/cancel/{booking_id}")
def cancel_booking(booking_id: int):
    for b in class_bookings:
        if b["id"] == booking_id:
            class_bookings.remove(b)
            return {"message": "Cancelled"}
    raise HTTPException(status_code=404)

@app.put("/memberships/{id}/freeze")
def freeze_membership(id: int):
    for m in memberships:
        if m["membership_id"] == id:
            m["status"] = "frozen"
            return m
    raise HTTPException(status_code=404)

@app.put("/memberships/{id}/reactivate")
def reactivate_membership(id: int):
    for m in memberships:
        if m["membership_id"] == id:
            m["status"] = "active"
            return m
    raise HTTPException(status_code=404)

# -----------------------------
# Q19
# -----------------------------
@app.get("/memberships/search")
def search_memberships(member_name: str):
    return [m for m in memberships if member_name.lower() in m["member_name"].lower()]

@app.get("/memberships/sort")
def sort_memberships(sort_by: str):
    return sorted(memberships, key=lambda x: x.get(sort_by, 0))

@app.get("/memberships/page")
def paginate_memberships(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return memberships[start:end]