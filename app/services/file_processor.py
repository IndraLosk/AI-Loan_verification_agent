# app/services/file_processor.py
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from typing import Optional

def detect_document_type(filename: str) -> Optional[str]:
    """Определяет тип документа по имени файла (регистронезависимо)."""
    name_lower = filename.lower()
    # Паттерны (можно расширить)
    patterns = {
        'contract': r'договор|contract',
        'specification': r'спецификация|specification|спец',
        'invoice': r'счет|счёт|invoice',
        'act': r'акт|упд|act|acceptance',
    }
    for doc_type, pattern in patterns.items():
        if re.search(pattern, name_lower):
            return doc_type
    return None