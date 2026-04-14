import requests

BASE = "http://localhost:8000"

users = [
    {"email": "agent1@claims.com", "password": "123456", "full_name": "Maria Rodriguez"},
    {"email": "agent2@claims.com", "password": "123456", "full_name": "Carlos Mendez"},
    {"email": "manager@claims.com", "password": "123456", "full_name": "Sara Kim"},
    {"email": "requester@claims.com", "password": "123456", "full_name": "John Smith"},
]

print("Creating users...")
for user in users:
    r = requests.post(f"{BASE}/auth/register", json=user)
    print(f"  {user['full_name']}: {r.status_code}")

token = requests.post(f"{BASE}/auth/login", json={
    "email": "requester@claims.com",
    "password": "123456"
}).json()["access_token"]

cases = [
    {"title": "Shipment #4821 — cargo damaged in transit", "description": "Pallet arrived with visible forklift damage. 3 of 12 boxes destroyed. Client requesting full replacement or credit.", "priority": "high"},
    {"title": "Lost package — tracking shows delivered but not received", "description": "Order #7743 marked as delivered 5 days ago. Recipient confirms nothing arrived. Driver GPS data requested.", "priority": "high"},
    {"title": "Wrong delivery address — shipment rerouted", "description": "Shipment sent to old client address despite updated records. Currently sitting at wrong warehouse.", "priority": "high"},
    {"title": "Refrigerated cargo — cold chain breach detected", "description": "Temperature logger shows breach during last mile. Pharmaceutical client threatening chargeback.", "priority": "high"},
    {"title": "Partial delivery — 4 of 10 pallets missing", "description": "Client received 6 pallets, invoice was for 10. Warehouse dispatch records unclear.", "priority": "medium"},
    {"title": "Duplicate billing — invoice sent twice for same route", "description": "Client charged twice for route MX-089 on March 3rd and March 4th. Finance review needed.", "priority": "medium"},
    {"title": "Shipment delay — 8 days over estimated delivery", "description": "Cross-border shipment held at customs. Client requesting compensation per SLA agreement.", "priority": "medium"},
    {"title": "Fragile items — improper packaging by warehouse", "description": "Client reported glassware arrived broken. Packaging photos show no bubble wrap used.", "priority": "medium"},
    {"title": "Driver incident — minor collision during delivery", "description": "Unit 14 reported minor collision on route. No injuries. Vehicle damage assessment pending.", "priority": "low"},
    {"title": "Client signature missing — proof of delivery disputed", "description": "Client denies receiving shipment. POD form has no signature. CCTV footage requested.", "priority": "low"},
]

print("\nCreating cases...")
case_ids = []
for case in cases:
    r = requests.post(f"{BASE}/cases/?token={token}", json=case)
    if r.status_code == 200:
        case_ids.append(r.json()["id"])
        print(f"  Created: {case['title'][:50]}")

print("\nMoving cases through workflow...")
transitions = [
    (0, "in_review", "Damage confirmed by warehouse team. Replacement order initiated."),
    (1, "in_review", "Driver contacted. GPS data pulled for review."),
    (2, "escalated", "Rerouting failed. Client escalating to account manager."),
    (3, "in_review", "Cold chain report requested from logistics provider."),
    (4, "in_review", "Dispatch records under review by warehouse supervisor."),
    (5, "in_review", "Finance team reviewing billing records."),
]

for idx, status, note in transitions:
    if idx < len(case_ids):
        r = requests.post(
            f"{BASE}/cases/{case_ids[idx]}/transition",
            params={"token": token, "to_status": status, "note": note}
        )
        print(f"  Case {idx+1} → {status}: {r.status_code}")

print("\nAdding comments...")
comments = [
    (0, "Warehouse confirmed 3 boxes total loss. Replacement shipment scheduled for tomorrow."),
    (1, "GPS shows driver stopped 2 blocks from destination. Investigating."),
    (2, "Client notified of delay. Expedited reroute in progress."),
    (3, "Pharmaceutical client legal team involved. Urgent resolution required."),
    (4, "2 missing pallets located at partner warehouse. Delivery rescheduled."),
]

for idx, body in comments:
    if idx < len(case_ids):
        r = requests.post(
            f"{BASE}/cases/{case_ids[idx]}/comments",
            params={"token": token},
            json={"body": body}
        )
        print(f"  Comment on case {idx+1}: {r.status_code}")

print("\nDone! Database seeded.")
