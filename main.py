import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from supabase import create_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not url or not key:
        raise HTTPException(
            status_code=500, 
            detail="Variables d'environnement manquantes dans Render"
        )
    
    url = url.strip().strip("'").strip('"')
    if "/rest/v1" in url:
        url = url.split("/rest/v1")[0]
    url = url.rstrip("/")
    
    return create_client(url, key)

@app.get("/")
def home():
    return {"status": "API BadgeBoost en ligne 🚀"}

# Route pour distribuer le script JS
@app.get("/widget.js")
def get_widget_script():
    return FileResponse("widget.js", media_type="application/javascript")

@app.get("/api/v1/widget/{api_key}")
def get_widget(api_key: str):
    try:
        supabase = get_supabase_client()
        
        client_res = supabase.table("clients").select("id, plan").eq("api_key", api_key).execute()
        if not client_res.data:
            raise HTTPException(status_code=404, detail="Clé API invalide")
        
        client_id = client_res.data[0]["id"]
        widget_res = supabase.table("widgets").select("*").eq("client_id", client_id).execute()
        
        config = widget_res.data[0] if widget_res.data else {"badge_text": "Garantie Satisfait ou Remboursé", "show_branding": True}
        
        if client_res.data[0]["plan"] == "free":
            config["show_branding"] = True
            
        return config
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import stripe

# Clé secrète de test Stripe
stripe.api_key = "sk_test_51RbOriRpZzMm1tv8xMARRr5tN3HYRJ2ISXcRXCZPhYlAmveTS2ZhUBxsewJv52psLSBV30kKq7nPLGHxiLpjsG89006sUYnyYY"

@app.post("/api/v1/create-checkout-session")
def create_checkout_session(client_id: str):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Abonnement BadgeBoost Pro',
                            'description': 'Accès illimité aux badges de confiance pour votre boutique',
                        },
                        'unit_amount': 1500,  # 15.00$ USD / mois
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url='https://badgeboost-backend.onrender.com/docs',
            cancel_url='https://badgeboost-backend.onrender.com/docs',
            client_reference_id=client_id,
        )
        return {"url": checkout_session.url}
    except Exception as e:
        return {"error": str(e)}


# Route pour servir la page Dashboard HTML
@app.get("/dashboard")
def get_dashboard():
    return FileResponse("dashboard.html", media_type="text/html")
