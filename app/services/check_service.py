# app/services/check_service.py
from app.services.file_processor import detect_document_type
from app.schemas import Issue, DocumentInfo
from typing import List, Dict, Tuple
from pathlib import Path

REQUIRED_FILES = {
    'federal': ['contract', 'specification', 'invoice', 'act'],
    'regional': ['contract', 'invoice', 'act']
}
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.jpeg', '.png'}
MAX_SIZE_MB = 20

def validate_package(files: List[Dict], program: str):
    """Возвращает (documents, issues, status, reason)."""
    docs = []
    issues = []
    detected_types = set()
    unknown_files = []

    for file in files:
        filename = file['filename']
        size_bytes = file['size']
        ext = Path(filename).suffix.lower()
        size_mb = size_bytes / (1024 * 1024)

        # Проверка формата
        if ext not in ALLOWED_EXTENSIONS:
            issues.append(Issue(level='error', message=f'Недопустимый формат файла: {filename}'))
        # Проверка размера
        if size_mb > MAX_SIZE_MB:
            issues.append(Issue(level='error', message=f'Файл превышает 20 МБ: {filename}'))

        doc_type = detect_document_type(filename)
        if doc_type is None:
            issues.append(Issue(level='warning', message=f'Не удалось определить тип документа: {filename}'))
            unknown_files.append(filename)
        else:
            detected_types.add(doc_type)

        docs.append(DocumentInfo(
            name=filename,
            detected_type=doc_type,
            size_kb=round(size_bytes / 1024, 1)
        ))

    # Проверка комплектности
    required = set(REQUIRED_FILES.get(program, []))
    missing = required - detected_types

    # Если есть ошибки (формат, размер, отсутствие обязательных) -> rejected
    has_errors = any(issue.level == 'error' for issue in issues)
    if missing:
        for doc in missing:
            issues.append(Issue(level='error', message=f'Отсутствует обязательный документ: {doc}'))
        has_errors = True

    if has_errors:
        status = 'rejected'
        status_label = 'Нельзя заявлять в банк'
        reason = f'Отсутствуют обязательные документы: {", ".join(missing)}' if missing else 'Нарушены требования к файлам'
    else:
        status = 'approved'
        status_label = 'Можно заявлять в банк'
        reason = None

    # Если были только warning, статус approved
    return docs, issues, status, status_label, reason