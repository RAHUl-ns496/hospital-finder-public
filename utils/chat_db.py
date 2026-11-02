from datetime import datetime
from utils.mongo import interactions_collection

def _load():
    data = interactions_collection().find_one({"_id": "app_state"})
    if not data:
        data = {"_id": "app_state", "assignments": {}, "messages": [],
                "pharmacy_orders": {}, "appointments": [], "medicine_orders": [],
                "doctor_slots": {}, "notifications": [], "shift_notes": {}}
        interactions_collection().insert_one(data)
    data.setdefault("assignments", {})
    data.setdefault("messages", [])
    data.setdefault("pharmacy_orders", {})
    data.setdefault("appointments", [])
    data.setdefault("medicine_orders", [])
    data.setdefault("doctor_slots", {})
    data.setdefault("notifications", [])
    data.setdefault("shift_notes", {})
    return data

def _save(data):
    interactions_collection().replace_one({"_id": "app_state"}, data, upsert=True)

def get_assignment(patient_email):
    return _load()["assignments"].get(patient_email)

def set_assignment(patient_email, doctor_email):
    d = _load()
    d["assignments"][patient_email] = doctor_email
    _save(d)

def get_patients_for_doctor(doctor_email):
    d = _load()
    return [p for p, doc in d["assignments"].items() if doc == doctor_email]

def get_messages(user1, user2):
    d = _load()
    msgs = []
    for m in d["messages"]:
        if (m["sender"] == user1 and m["receiver"] == user2) or \
           (m["sender"] == user2 and m["receiver"] == user1):
            msgs.append(m)
    return msgs

def get_prescriptions(user1, user2):
    return [message for message in get_messages(user1, user2)
            if message.get("is_prescription")]

def send_message(sender, receiver, text, is_prescription=False):
    d = _load()
    d["messages"].append({
        "sender": sender,
        "receiver": receiver,
        "text": text,
        "is_prescription": is_prescription,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    _save(d)

def get_pharmacy_interaction(patient_email, pharmacy_name):
    d = _load()
    key = f"{patient_email}_{pharmacy_name}"
    return d.get("pharmacy_orders", {}).get(key, [])

def add_pharmacy_interaction(patient_email, pharmacy_name, text, is_bot=False):
    d = _load()
    key = f"{patient_email}_{pharmacy_name}"
    if "pharmacy_orders" not in d: d["pharmacy_orders"] = {}
    if key not in d["pharmacy_orders"]: d["pharmacy_orders"][key] = []
    
    d["pharmacy_orders"][key].append({
        "sender": "Pharmacy" if is_bot else "Patient",
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    _save(d)

def create_appointment(patient_email, doctor_email, appointment_date, appointment_time,
                       reason, patient_name="", appointment_type="In-person visit"):
    d = _load()
    slot_key = f"{doctor_email}|{appointment_date}|{appointment_time}"
    if slot_key in d["doctor_slots"] and d["doctor_slots"][slot_key].get("booked"):
        return None
    appointment = {
        "id": f"apt_{len(d['appointments']) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "patient_email": patient_email,
        "patient_name": patient_name,
        "doctor_email": doctor_email,
        "date": appointment_date,
        "time": appointment_time,
        "appointment_type": appointment_type,
        "reason": reason.strip(),
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    d["appointments"].append(appointment)
    d["doctor_slots"][slot_key] = {"doctor_email": doctor_email, "date": appointment_date,
                                    "time": appointment_time, "booked": True}
    add_notification(d, doctor_email, "New appointment request", f"{patient_name} requested {appointment_date} at {appointment_time}.")
    _save(d)
    return appointment

def get_appointments(email, role=None):
    appointments = _load()["appointments"]
    if role == "doctor":
        return [a for a in appointments if a["doctor_email"] == email]
    return [a for a in appointments if a["patient_email"] == email]

def update_appointment_status(appointment_id, status):
    d = _load()
    for appointment in d["appointments"]:
        if appointment["id"] == appointment_id:
            appointment["status"] = status
            recipient = appointment["patient_email"]
            add_notification(d, recipient, f"Appointment {status.lower()}",
                             f"Your appointment on {appointment['date']} at {appointment['time']} is {status.lower()}.")
            _save(d)
            return True
    return False

def create_medicine_order(patient_email, patient_name, pharmacy_name, items,
                          delivery_address, notes=""):
    d = _load()
    order = {
        "id": f"med_{len(d['medicine_orders']) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "patient_email": patient_email,
        "patient_name": patient_name,
        "pharmacy_name": pharmacy_name,
        "items": items.strip(),
        "delivery_address": delivery_address.strip(),
        "notes": notes.strip(),
        "status": "Received",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    d["medicine_orders"].append(order)
    _save(d)
    return order

def get_medicine_orders(email):
    return [o for o in _load()["medicine_orders"] if o["patient_email"] == email]

def get_all_medicine_orders():
    return _load()["medicine_orders"]

def update_medicine_order_status(order_id, status):
    d = _load()
    for order in d["medicine_orders"]:
        if order["id"] == order_id:
            order["status"] = status
            add_notification(d, order["patient_email"], f"Medicine order {status.lower()}",
                             f"Order {order_id} is now {status.lower()}.")
            _save(d)
            return True
    return False

def get_doctor_slots(doctor_email):
    return [slot for slot in _load()["doctor_slots"].values()
            if slot["doctor_email"] == doctor_email and not slot.get("booked")]

def set_doctor_slots(doctor_email, slots):
    d = _load()
    for slot in slots:
        key = f"{doctor_email}|{slot['date']}|{slot['time']}"
        if key not in d["doctor_slots"]:
            d["doctor_slots"][key] = dict(slot, doctor_email=doctor_email, booked=False)
    _save(d)

def add_notification(data, user_email, title, message):
    data.setdefault("notifications", [])
    data["notifications"].append({
        "id": f"note_{len(data['notifications']) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "user_email": user_email, "title": title, "message": message,
        "read": False, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

def get_notifications(user_email):
    return [n for n in reversed(_load()["notifications"]) if n["user_email"] == user_email]

def mark_notifications_read(user_email):
    d = _load()
    for notification in d["notifications"]:
        if notification["user_email"] == user_email:
            notification["read"] = True
    _save(d)

def get_shift_notes(doctor_email):
    return _load()["shift_notes"].get(doctor_email, "")

def save_shift_notes(doctor_email, notes):
    d = _load()
    d.setdefault("shift_notes", {})
    d["shift_notes"][doctor_email] = notes.strip()
    _save(d)
