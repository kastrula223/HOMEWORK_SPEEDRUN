from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Participants API")


@app.post("/participants/", response_model=schemas.ParticipantOut, status_code=201)
def create_participant(participant: schemas.ParticipantCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Participant).filter(
        models.Participant.email == participant.email
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=422,
            detail=f"Учасник з email '{participant.email}' вже зареєстрований.",
        )

    db_participant = models.Participant(
        name=participant.name,
        email=participant.email,
        event=participant.event,
        age=participant.age,
    )

    db.add(db_participant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=f"Учасник з email '{participant.email}' вже зареєстрований.",
        )

    db.refresh(db_participant)
    return db_participant


@app.get("/participants/event/{event_name}", response_model=list[schemas.ParticipantOut])
def get_participants_by_event(event_name: str, db: Session = Depends(get_db)):
    participants = db.query(models.Participant).filter(
        models.Participant.event == event_name
    ).all()

    return participants


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)