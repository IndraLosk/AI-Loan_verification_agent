# app/routers/checks.py
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Check
from app.schemas import CheckResponse, CheckListResponse, Issue, DocumentInfo
from app.services.check_service import validate_package
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/checks", tags=["checks"])

@router.post("/", response_model=CheckResponse)
async def create_check(
    program: str = Form(..., regex="^(federal|regional)$"),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Читаем содержимое в память (для реального проекта можно сохранять в хранилище)
    file_infos = []
    for f in files:
        content = await f.read()
        file_infos.append({
            'filename': f.filename,
            'size': len(content),
            'content': content  # сохраняем для дальнейшего использования (не требуется)
        })

    docs, issues, status, status_label, reason = validate_package(file_infos, program)

    # Создаём запись в БД
    check_id = uuid.uuid4()
    db_check = Check(
        id=check_id,
        program=program,
        status=status,
        status_label=status_label,
        reason=reason,
        issues=[issue.dict() for issue in issues],
        documents=[doc.dict() for doc in docs],
        extracted={},  # можно оставить пустым или заполнить заглушкой
        checked_at=datetime.utcnow()
    )
    db.add(db_check)
    db.commit()
    db.refresh(db_check)

    return CheckResponse(
        check_id=db_check.id,
        status=db_check.status,
        status_label=db_check.status_label,
        reason=db_check.reason,
        issues=issues,
        documents=docs,
        extracted={},
        checked_at=db_check.checked_at
    )

@router.get("/", response_model=List[CheckListResponse])
def list_checks(db: Session = Depends(get_db)):
    checks = db.query(Check).all()
    result = []
    for c in checks:
        result.append(CheckListResponse(
            id=c.id,
            program=c.program,
            status=c.status,
            checked_at=c.checked_at,
            documents_count=len(c.documents)
        ))
    return result

@router.get("/{check_id}", response_model=CheckResponse)
def get_check(check_id: uuid.UUID, db: Session = Depends(get_db)):
    check = db.query(Check).filter(Check.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Проверка не найдена")
    return CheckResponse(
        check_id=check.id,
        status=check.status,
        status_label=check.status_label,
        reason=check.reason,
        issues=[Issue(**i) for i in check.issues],
        documents=[DocumentInfo(**d) for d in check.documents],
        extracted=check.extracted,
        checked_at=check.checked_at
    )