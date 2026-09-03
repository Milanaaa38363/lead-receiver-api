from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import List

from app.config import API_TOKEN
from app.database import Base, engine, get_db
from app.models import Client, Deal, LeadHistory, DealStatus
from app.schemas import CreateLeadRequest, CreateLeadResponse, DealResponse
from app.utils import normalize_phone

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Receiver API")

def verify_token(x_token: str = Header(None, alias="X-Token")):
    if not x_token or x_token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или отсутствует заголовок X-Token"
        )

@app.post("/leads", response_model=CreateLeadResponse, dependencies=[Depends(verify_token)])
def create_lead(request: CreateLeadRequest, db: Session = Depends(get_db)):
    norm_phone = normalize_phone(request.phone)
    
    client = db.query(Client).filter(Client.phone_normalized == norm_phone).first()
    is_new = False

    if not client:
        is_new = True
        client = Client(name=request.name, phone_normalized=norm_phone)
        db.add(client)
        db.flush()

        deal = Deal(client_id=client.id, status=DealStatus.NEW)
        db.add(deal)
        db.flush()
    else:
        deal = db.query(Deal).filter(Deal.client_id == client.id).order_by(Deal.created_at.desc()).first()
        if not deal:
            deal = Deal(client_id=client.id, status=DealStatus.NEW)
            db.add(deal)
            db.flush()

    history_entry = LeadHistory(
        deal_id=deal.id,
        source=request.source,
        raw_phone=request.phone
    )
    db.add(history_entry)
    db.commit()

    message = "Создан новый клиент и сделка" if is_new else "Заявка добавлена в историю существующей сделки"

    return CreateLeadResponse(
        is_new_client=is_new,
        client_id=client.id,
        deal_id=deal.id,
        message=message
    )

@app.get("/deals", response_model=List[DealResponse], dependencies=[Depends(verify_token)])
def get_deals(db: Session = Depends(get_db)):
    return db.query(Deal).order_by(Deal.created_at.desc()).all()