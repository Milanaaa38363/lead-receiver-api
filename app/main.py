@"
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import Base, engine, get_db
from app.schemas import CreateLeadRequest, CreateLeadResponse, DealResponse
from app.models import Client, Deal, LeadHistory
from app.utils import normalize_phone, InvalidPhoneError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Management API")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/leads/", response_model=CreateLeadResponse)
def create_lead(request: CreateLeadRequest, db: Session = Depends(get_db)):
    try:
        norm_phone = normalize_phone(request.phone)
    except InvalidPhoneError as e:
        raise HTTPException(status_code=400, detail=str(e))

    client = db.query(Client).filter(Client.phone_normalized == norm_phone).first()
    is_new = False

    if not client:
        client = Client(name=request.name, phone_normalized=norm_phone)
        db.add(client)
        db.commit()
        db.refresh(client)
        is_new = True

    deal = db.query(Deal).filter(Deal.client_id == client.id, Deal.status == "NEW").first()
    if not deal:
        deal = Deal(client_id=client.id, status="NEW")
        db.add(deal)
        db.commit()
        db.refresh(deal)

    history = LeadHistory(
        deal_id=deal.id,
        source=request.source,
        raw_phone=request.phone
    )
    db.add(history)
    db.commit()

    msg = "Создан новый клиент и сделка" if is_new else "Заявка привязана к существующему клиенту"
    return CreateLeadResponse(
        is_new_client=is_new,
        client_id=client.id,
        deal_id=deal.id,
        message=msg
    )

@app.get("/deals/", response_model=List[DealResponse])
def get_deals(db: Session = Depends(get_db)):
    return db.query(Deal).all()
