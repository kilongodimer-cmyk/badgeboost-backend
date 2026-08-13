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

def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not url or not key:
        raise HTTPException(
            status_code=500, 
            detail="Variables d'environnement manquantes dans Render"
        )
    
    # Nettoyage rigoureux de l'URL Supabase
    url = url.strip().strip("'").strip('"')
    if "/rest/v1" in url:
        url = url.split("/rest/v1")[0]
    url = url.rstrip("/")
    
    return create_client(url, key)

@app.get("/")
def home():
    return {"status": "API BadgeBoost en ligne 🚀"}

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
