from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

app = FastAPI()
@app.get("/health")
def health_check():
    return {"status": "ok"}

# PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://{{ lookup('env', 'DB_USER') }}:{{ lookup('env', 'DB_PASS') }}@prod-rmm-db.cluster-c0rcwo8m2en7.us-east-1.rds.amazonaws.com/postgres"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SystemInfo(Base):
    __tablename__ = "system_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    hostname = Column(String, index=True)
    os = Column(String)
    os_version = Column(String)
    cpu = Column(String)
    memory_gb = Column(Float)
    ip = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ManualInventory(Base):
    __tablename__ = "manual_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    hostname = Column(String, index=True)
    os = Column(String)
    cpu = Column(String)
    ram_gb = Column(String)
    storage_gb = Column(String)
    mac_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class SystemInfoIn(BaseModel):
    user_id: str
    hostname: str
    os: str
    os_version: str
    cpu: str
    memory_gb: float
    ip: str

class ManualInventoryIn(BaseModel):
    user_id: str
    hostname: str
    os: str
    cpu: str
    ram_gb: str
    storage_gb: str
    mac_address: str

### Routes ###
@app.post("/api/report")
def receive_system_info(data: SystemInfoIn):
    db = SessionLocal()
    try:
        info = SystemInfo(**data.dict())
        db.add(info)
        db.commit()
        db.refresh(info)
        return {"status": "success", "id": info.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/manual_inventory")
def receive_manual_inventory(data: ManualInventoryIn):
    db = SessionLocal()
    try:
        item = ManualInventory(**data.dict())
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"status": "success", "id": item.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
