from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os

from app import models
from app.database import engine, get_db

os.makedirs("data", exist_ok=True)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cave à Vin")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PIN_CODE = os.getenv("PIN_CODE", "1234")

# ─── Auth ─────────────────────────────────────────────────────────────────────
def verify_pin(x_pin: str = Header(...)):
    if x_pin != PIN_CODE:
        raise HTTPException(status_code=401, detail="PIN invalide")

# ─── Schemas ──────────────────────────────────────────────────────────────────
class WineCreate(BaseModel):
    nom:         str
    couleur:     str
    domaine:     Optional[str]   = None
    annee:       Optional[int]   = None
    region:      Optional[str]   = None
    appellation: Optional[str]   = None
    qty:         int             = 1
    prix:        Optional[float] = None
    garde:       Optional[int]   = None
    rating:      int             = 0
    notes:       Optional[str]   = None
    emplacement: Optional[str]   = None

class WineOut(WineCreate):
    id:         int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj):
        d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        d["created_at"] = obj.created_at.isoformat() if obj.created_at else None
        return cls(**d)

# ─── Frontend ─────────────────────────────────────────────────────────────────
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ─── Auth endpoint ────────────────────────────────────────────────────────────
@app.post("/api/auth/verify")
def auth_verify(x_pin: str = Header(...)):
    if x_pin != PIN_CODE:
        raise HTTPException(status_code=401, detail="PIN invalide")
    return {"ok": True}

# ─── Wines CRUD ───────────────────────────────────────────────────────────────
@app.get("/api/wines", response_model=List[WineOut])
def get_wines(db: Session = Depends(get_db), _=Depends(verify_pin)):
    wines = db.query(models.Wine).order_by(models.Wine.created_at.desc()).all()
    return [WineOut.from_orm_custom(w) for w in wines]

@app.post("/api/wines", response_model=WineOut, status_code=201)
def create_wine(wine: WineCreate, db: Session = Depends(get_db), _=Depends(verify_pin)):
    db_wine = models.Wine(**wine.model_dump())
    db.add(db_wine)
    db.commit()
    db.refresh(db_wine)
    return WineOut.from_orm_custom(db_wine)

@app.put("/api/wines/{wine_id}", response_model=WineOut)
def update_wine(wine_id: int, wine: WineCreate, db: Session = Depends(get_db), _=Depends(verify_pin)):
    db_wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not db_wine:
        raise HTTPException(status_code=404, detail="Vin introuvable")
    for k, v in wine.model_dump().items():
        setattr(db_wine, k, v)
    db.commit()
    db.refresh(db_wine)
    return WineOut.from_orm_custom(db_wine)

@app.delete("/api/wines/{wine_id}")
def delete_wine(wine_id: int, db: Session = Depends(get_db), _=Depends(verify_pin)):
    db_wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not db_wine:
        raise HTTPException(status_code=404, detail="Vin introuvable")
    db.delete(db_wine)
    db.commit()
    return {"ok": True}

# ─── Boire une bouteille ──────────────────────────────────────────────────────
@app.patch("/api/wines/{wine_id}/boire", response_model=WineOut)
def boire_wine(wine_id: int, db: Session = Depends(get_db), _=Depends(verify_pin)):
    db_wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not db_wine:
        raise HTTPException(status_code=404, detail="Vin introuvable")
    if db_wine.qty <= 0:
        raise HTTPException(status_code=400, detail="Plus de bouteilles disponibles")
    db_wine.qty -= 1
    db.commit()
    db.refresh(db_wine)
    return WineOut.from_orm_custom(db_wine)

# ─── Stats ────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(verify_pin)):
    wines = db.query(models.Wine).all()

    total_bottles = sum(w.qty for w in wines)
    total_value   = sum((w.prix or 0) * w.qty for w in wines)
    years         = [w.annee for w in wines if w.annee]
    avg_year      = round(sum(years) / len(years)) if years else None

    color_counts   = {}
    region_counts  = {}
    vintage_counts = {}

    for w in wines:
        color_counts[w.couleur] = color_counts.get(w.couleur, 0) + w.qty
        if w.region:
            region_counts[w.region] = region_counts.get(w.region, 0) + w.qty
        if w.annee:
            k = str(w.annee)
            vintage_counts[k] = vintage_counts.get(k, 0) + w.qty

    return {
        "total_bottles": total_bottles,
        "total_refs":    len(wines),
        "total_value":   round(total_value, 2),
        "avg_year":      avg_year,
        "oldest_year":   min(years) if years else None,
        "color_counts":  color_counts,
        "region_counts": region_counts,
        "vintage_counts": dict(sorted(vintage_counts.items())),
    }

@app.get("/health")
def health():
    return {"status": "ok"}