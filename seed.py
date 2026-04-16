import requests
import random

BASE = "http://localhost:8000"

users = [
    {"email": "requester@claims.com", "password": "123456", "full_name": "John Smith", "role": "requester"},
    {"email": "agent1@claims.com", "password": "123456", "full_name": "Maria Garcia", "role": "agent"},
    {"email": "agent2@claims.com", "password": "123456", "full_name": "Carlos Mendez", "role": "agent"},
    {"email": "manager@claims.com", "password": "123456", "full_name": "Ana Rodriguez", "role": "manager"},
    {"email": "emilio@claims.com", "password": "123456", "full_name": "Emilio Guerrero", "role": "requester"},
]

cases = [
    # E-commerce
    {"title": "Mercado Libre — damaged packaging on 200 units", "description": "[E-commerce — Mercado Libre]\n\nCustomer received 200 units with damaged packaging. Products inside intact but unacceptable for resale.", "priority": "high"},
    {"title": "Amazon México — missing pallet on delivery route MX-042", "description": "[E-commerce — Amazon México]\n\nDriver confirmed 12 pallets dispatched. Client received only 11. One pallet unaccounted for.", "priority": "high"},
    {"title": "Liverpool — wrong SKU delivered to CDMX warehouse", "description": "[E-commerce — Liverpool]\n\nSKU 4821-B delivered instead of 4821-A. Full batch of 500 units needs return and redelivery.", "priority": "medium"},
    {"title": "Mercado Libre — cold chain breach on electronics shipment", "description": "[E-commerce — Mercado Libre]\n\nTemperature logs show excursion above 35°C for 4 hours during transit. Client requesting full replacement.", "priority": "high"},
    {"title": "Amazon México — late delivery impacting Prime SLA", "description": "[E-commerce — Amazon México]\n\nShipment arrived 3 days late. Client requesting compensation per SLA agreement.", "priority": "medium"},

    # Pharmaceutical
    {"title": "Pfizer México — temperature excursion on vaccine shipment", "description": "[Pharmaceutical — Pfizer México]\n\nCold chain breach detected. Vaccines exposed to temperatures outside 2-8°C range for 6 hours.", "priority": "high"},
    {"title": "Laboratorios Pisa — missing documentation on controlled substances", "description": "[Pharmaceutical — Laboratorios Pisa]\n\nShipment arrived without required COFEPRIS documentation. Batch held at customs.", "priority": "high"},
    {"title": "Grupo Biopharma — damaged vials in transit", "description": "[Pharmaceutical — Grupo Biopharma]\n\n34 vials broken during transport. Client requesting replacement and incident report.", "priority": "medium"},
    {"title": "Pfizer México — incorrect batch number on delivery note", "description": "[Pharmaceutical — Pfizer México]\n\nBatch number on physical shipment does not match delivery documentation.", "priority": "low"},

    # Automotive
    {"title": "General Motors México — engine parts delayed at Nuevo Laredo", "description": "[Automotive — General Motors México]\n\nCritical engine components held at border crossing. Production line at risk of stopping in 48hrs.", "priority": "high"},
    {"title": "Toyota de México — scratched body panels on 40 units", "description": "[Automotive — Toyota de México]\n\n40 door panels arrived with surface scratches. Client rejecting full batch.", "priority": "high"},
    {"title": "Ford Motor México — incomplete shipment of transmission parts", "description": "[Automotive — Ford Motor México]\n\nOnly 80 of 120 ordered transmission units arrived. 40 units missing from manifest.", "priority": "medium"},
    {"title": "General Motors México — wrong torque specs on bolts delivered", "description": "[Automotive — General Motors México]\n\nBolt batch delivered with incorrect torque specifications. Cannot be used on production line.", "priority": "high"},

    # Retail
    {"title": "Walmart de México — 500 units short on seasonal inventory", "description": "[Retail — Walmart de México]\n\nHoliday inventory shipment arrived 500 units short. Peak season starting in 3 days.", "priority": "high"},
    {"title": "FEMSA Comercio — expired products delivered to Guadalajara stores", "description": "[Retail — FEMSA Comercio]\n\n12 pallets of beverages delivered past expiration date. Full return requested.", "priority": "high"},
    {"title": "Grupo Coppel — water damage on appliance shipment", "description": "[Retail — Grupo Coppel]\n\nRain exposure during loading caused water damage to 28 washing machines.", "priority": "medium"},
    {"title": "Walmart de México — delivery to wrong distribution center", "description": "[Retail — Walmart de México]\n\nShipment arrived at Monterrey DC instead of Tijuana DC. Rerouting required.", "priority": "medium"},

    # Industrial
    {"title": "Cemex Logística — cracked cement mixer components", "description": "[Industrial — Cemex Logística]\n\nHeavy machinery components cracked during unloading. Inadequate packaging identified as cause.", "priority": "high"},
    {"title": "Grupo Xignux — electrical cables delivered with wrong gauge", "description": "[Industrial — Grupo Xignux]\n\n10km of cable delivered at 16AWG instead of 12AWG. Full batch unusable for project.", "priority": "high"},
    {"title": "Vitro Packaging — glass panels broken in transit", "description": "[Industrial — Vitro Packaging]\n\n180 of 600 glass panels arrived broken. Inadequate cushioning in packaging.", "priority": "medium"},

    # Food & Beverage
    {"title": "Grupo Bimbo — refrigerated truck failure on bread delivery", "description": "[Food & Beverage — Grupo Bimbo]\n\nRefrigeration unit failed mid-route. Full perishable load of 8 tons compromised.", "priority": "high"},
    {"title": "Grupo Lala — dairy products delivered at wrong temperature", "description": "[Food & Beverage — Grupo Lala]\n\nMilk products arrived at 12°C instead of required 4°C. Full batch rejected by client.", "priority": "high"},
    {"title": "Sigma Alimentos — mislabeled meat products in export shipment", "description": "[Food & Beverage — Sigma Alimentos]\n\nProduct labels in Spanish only. Export shipment to US requires bilingual labeling.", "priority": "medium"},

    # Government
    {"title": "IMSS — medical supplies held at customs", "description": "[Government — IMSS]\n\nUrgent medical equipment shipment delayed at customs due to missing import permits.", "priority": "high"},
    {"title": "SEP — school materials delivered to wrong state", "description": "[Government — SEP]\n\nBack to school supplies for Oaxaca delivered to Veracruz. 2000 students affected.", "priority": "high"},
    {"title": "Secretaría de Salud — cold chain failure on vaccine distribution", "description": "[Government — Secretaría de Salud]\n\nNational vaccination campaign vaccines stored at incorrect temperature for 8 hours.", "priority": "high"},
]

statuses = ['open', 'in_review', 'in_review', 'pending_approval', 'escalated', 'resolved']

print("Seeding users...")
tokens = {}
for u in users:
    r = requests.post(f"{BASE}/auth/register", json=u)
    if r.status_code in [200, 201]:
        print(f"  Created {u['email']}")
    else:
        print(f"  Skipped {u['email']} (already exists)")
    login = requests.post(f"{BASE}/auth/login", json={"email": u["email"], "password": u["password"]})
    if login.status_code == 200:
        tokens[u["email"]] = login.json()["access_token"]

requester_token = tokens.get("requester@claims.com")
if not requester_token:
    print("Could not get requester token. Exiting.")
    exit()

print("Seeding cases...")
for c in cases:
    status = random.choice(statuses)
    r = requests.post(f"{BASE}/cases/?token={requester_token}", json={
        "title": c["title"],
        "description": c["description"],
        "priority": c["priority"],
    })
    if r.status_code in [200, 201]:
        case_id = r.json()["id"]
        if status != "open":
            transitions = {
                "in_review": ["in_review"],
                "pending_approval": ["in_review", "pending_approval"],
                "escalated": ["in_review", "escalated"],
                "resolved": ["in_review", "pending_approval", "approved", "resolved"],
            }
            for to_status in transitions.get(status, []):
                requests.post(f"{BASE}/cases/{case_id}/transition?token={requester_token}&to_status={to_status}")
        print(f"  Created: {c['title'][:50]}... [{status}]")

# Set admin role
print("Setting admin role...")
import subprocess
subprocess.run([
    "docker", "exec", "-it", "claims-platform-db-1",
    "psql", "-U", "admin", "-d", "claimsdb",
    "-c", "UPDATE users SET role='admin' WHERE email IN ('requester@claims.com', 'emilio@claims.com');"
], capture_output=True)
 

print("\nDone! Database seeded.")
