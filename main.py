import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Correction de l'initialisation du client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def home():
    return {"status": "API BadgeBoost en ligne 🚀"}

@app.get("/api/v1/widget/{api_key}")
def get_widget(api_key: str):
    try:
        client_res = supabase.table("clients").select("id, plan").eq("api_key", api_key).execute()
        if not client_res.data:
            raise HTTPException(status_code=404, detail="Clé API invalide")
        
        client_id = client_res.data[0]["id"]
        widget_res = supabase.table("widgets").select("*").eq("client_id", client_id).execute()
        
        config = widget_res.data[0] if widget_res.data else {"badge_text": "Garantie Satisfait ou Remboursé", "show_branding": True}
        
        if client_res.data[0]["plan"] == "free":
            config["show_branding"] = True
            
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
