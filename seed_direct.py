import uuid
import random
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://admin:secret@db:5432/claimsdb')
engine = create_engine(DATABASE_URL)

def hash_password(password):
    return bcrypt.hashpw(password[:72].encode(), bcrypt.gensalt()).decode()

users = [
    {"email": "requester@claims.com", "password": "123456", "full_name": "John Smith", "role": "admin"},
    {"email": "emilio@claims.com", "password": "123456", "full_name": "Emilio Natividad", "role": "admin"},
    {"email": "agent1@claims.com", "password": "123456", "full_name": "Maria Garcia", "role": "agent"},
    {"email": "agent2@claims.com", "password": "123456", "full_name": "Carlos Mendez", "role": "agent"},
    {"email": "manager@claims.com", "password": "123456", "full_name": "Ana Rodriguez", "role": "manager"},
]

cases = [
    {"title": "Mercado Libre — damaged packaging on 200 units", "description": "[E-commerce — Mercado Libre]\n\nCustomer received 200 units with damaged packaging.", "priority": "high"},
    {"title": "Amazon México — missing pallet on delivery route MX-042", "description": "[E-commerce — Amazon México]\n\nDriver confirmed 12 pallets dispatched. Client received only 11.", "priority": "high"},
    {"title": "Liverpool — wrong SKU delivered to CDMX warehouse", "description": "[E-commerce — Liverpool]\n\nSKU 4821-B delivered instead of 4821-A.", "priority": "medium"},
    {"title": "Pfizer México — temperature excursion on vaccine shipment", "description": "[Pharmaceutical — Pfizer México]\n\nCold chain breach detected. Vaccines exposed to temperatures outside 2-8°C.", "priority": "high"},
    {"title": "Laboratorios Pisa — missing documentation on controlled substances", "description": "[Pharmaceutical — Laboratorios Pisa]\n\nShipment arrived without required COFEPRIS documentation.", "priority": "high"},
    {"title": "Grupo Biopharma — damaged vials in transit", "description": "[Pharmaceutical — Grupo Biopharma]\n\n34 vials broken during transport.", "priority": "medium"},
    {"title": "General Motors México — engine parts delayed at Nuevo Laredo", "description": "[Automotive — General Motors México]\n\nCritical engine components held at border crossing.", "priority": "high"},
    {"title": "Toyota de México — scratched body panels on 40 units", "description": "[Automotive — Toyota de México]\n\n40 door panels arrived with surface scratches.", "priority": "high"},
    {"title": "Ford Motor México — incomplete shipment of transmission parts", "description": "[Automotive — Ford Motor México]\n\nOnly 80 of 120 ordered transmission units arrived.", "priority": "medium"},
    {"title": "Walmart de México — 500 units short on seasonal inventory", "description": "[Retail — Walmart de México]\n\nHoliday inventory shipment arrived 500 units short.", "priority": "high"},
    {"title": "FEMSA Comercio — expired products delivered to Guadalajara", "description": "[Retail — FEMSA Comercio]\n\n12 pallets of beverages delivered past expiration date.", "priority": "high"},
    {"title": "Grupo Coppel — water damage on appliance shipment", "description": "[Retail — Grupo Coppel]\n\nRain exposure during loading caused water damage to 28 washing machines.", "priority": "medium"},
    {"title": "Cemex Logística — cracked cement mixer components", "description": "[Industrial — Cemex Logística]\n\nHeavy machinery components cracked during unloading.", "priority": "high"},
    {"title": "Grupo Xignux — electrical cables delivered with wrong gauge", "description": "[Industrial — Grupo Xignux]\n\n10km of cable delivered at 16AWG instead of 12AWG.", "priority": "high"},
    {"title": "Vitro Packaging — glass panels broken in transit", "description": "[Industrial — Vitro Packaging]\n\n180 of 600 glass panels arrived broken.", "priority": "medium"},
    {"title": "Grupo Bimbo — refrigerated truck failure on bread delivery", "description": "[Food & Beverage — Grupo Bimbo]\n\nRefrigeration unit failed mid-route.", "priority": "high"},
    {"title": "Grupo Lala — dairy products delivered at wrong temperature", "description": "[Food & Beverage — Grupo Lala]\n\nMilk products arrived at 12°C instead of required 4°C.", "priority": "high"},
    {"title": "Sigma Alimentos — mislabeled meat products in export shipment", "description": "[Food & Beverage — Sigma Alimentos]\n\nProduct labels in Spanish only.", "priority": "medium"},
    {"title": "IMSS — medical supplies held at customs", "description": "[Government — IMSS]\n\nUrgent medical equipment shipment delayed at customs.", "priority": "high"},
    {"title": "SEP — school materials delivered to wrong state", "description": "[Government — SEP]\n\nBack to school supplies for Oaxaca delivered to Veracruz.", "priority": "high"},
    {"title": "Secretaría de Salud — cold chain failure on vaccine distribution", "description": "[Government — Secretaría de Salud]\n\nNational vaccination campaign vaccines stored at incorrect temperature.", "priority": "high"},
    {"title": "Mercado Libre — cold chain breach on electronics shipment", "description": "[E-commerce — Mercado Libre]\n\nTemperature logs show excursion above 35°C for 4 hours.", "priority": "high"},
    {"title": "Amazon México — late delivery impacting Prime SLA", "description": "[E-commerce — Amazon México]\n\nShipment arrived 3 days late.", "priority": "medium"},
    {"title": "Pfizer México — incorrect batch number on delivery note", "description": "[Pharmaceutical — Pfizer México]\n\nBatch number on physical shipment does not match delivery documentation.", "priority": "low"},
    {"title": "General Motors México — wrong torque specs on bolts delivered", "description": "[Automotive — General Motors México]\n\nBolt batch delivered with incorrect torque specifications.", "priority": "high"},
    {"title": "Walmart de México — delivery to wrong distribution center", "description": "[Retail — Walmart de México]\n\nShipment arrived at Monterrey DC instead of Tijuana DC.", "priority": "medium"},
]

statuses = ['open', 'open', 'in_review', 'in_review', 'pending_approval', 'escalated', 'resolved']

with engine.connect() as conn:
    print("Creating users...")
    user_ids = {}
    for u in users:
        uid = str(uuid.uuid4())
        user_ids[u['email']] = uid
        conn.execute(text("""
            INSERT INTO users (id, email, hashed_password, full_name, role, created_at)
            VALUES (:id, :email, :pwd, :name, :role, :now)
            ON CONFLICT (email) DO NOTHING
        """), {
            'id': uid,
            'email': u['email'],
            'pwd': hash_password(u['password']),
            'name': u['full_name'],
            'role': u['role'],
            'now': datetime.utcnow()
        })

    requester_id = user_ids.get('requester@claims.com')

    print("Creating cases...")
    for c in cases:
        status = random.choice(statuses)
        claimed = random.choice([None, None, None, random.uniform(10000, 500000)])
        conn.execute(text("""
            INSERT INTO cases (id, title, description, status, priority, claimed_amount, created_by, sla_deadline, created_at, updated_at)
            VALUES (:id, :title, :desc, :status, :priority, :claimed, :created_by, :sla, :now, :now)
        """), {
            'id': str(uuid.uuid4()),
            'title': c['title'],
            'desc': c['description'],
            'status': status,
            'priority': c['priority'],
            'claimed': claimed,
            'created_by': requester_id,
            'sla': datetime.utcnow() + timedelta(days=5),
            'now': datetime.utcnow()
        })

    conn.commit()
    print(f"Done! Seeded {len(users)} users and {len(cases)} cases.")
