# tests/test_file_processor.py
import pytest
from app.services.file_processor import detect_document_type
from app.services.check_service import validate_package

def test_detect_contract():
    assert detect_document_type("договор_123.pdf") == "contract"
    assert detect_document_type("contract_1.docx") == "contract"

def test_detect_specification():
    assert detect_document_type("спецификация_к_договору.pdf") == "specification"
    assert detect_document_type("specification.xlsx") == "specification"  # хотя формат не разрешён, но тип определится

def test_detect_invoice():
    assert detect_document_type("счет_45.pdf") == "invoice"
    assert detect_document_type("invoice_2.jpg") == "invoice"

def test_detect_act():
    assert detect_document_type("акт_выполненных_работ.pdf") == "act"
    assert detect_document_type("УПД_123.docx") == "act"

def test_unknown_type():
    assert detect_document_type("scan_0041.jpg") is None

def test_validate_federal_missing_spec():
    files = [
        {'filename': 'договор.pdf', 'size': 1000},
        {'filename': 'счет.pdf', 'size': 1000},
        {'filename': 'акт.pdf', 'size': 1000},
    ]
    docs, issues, status, label, reason = validate_package(files, 'federal')
    assert status == 'rejected'
    assert any('спецификация' in i.message for i in issues if i.level == 'error')

def test_validate_regional_complete():
    files = [
        {'filename': 'contract.pdf', 'size': 1000},
        {'filename': 'invoice.pdf', 'size': 1000},
        {'filename': 'act.pdf', 'size': 1000},
    ]
    docs, issues, status, label, reason = validate_package(files, 'regional')
    assert status == 'approved'
    assert len([i for i in issues if i.level == 'error']) == 0

def test_validate_wrong_extension():
    files = [
        {'filename': 'договор.txt', 'size': 1000},
        {'filename': 'счет.pdf', 'size': 1000},
        {'filename': 'акт.pdf', 'size': 1000},
    ]
    docs, issues, status, label, reason = validate_package(files, 'regional')
    assert status == 'rejected'
    assert any('Недопустимый формат' in i.message for i in issues)

def test_validate_file_too_large():
    files = [
        {'filename': 'договор.pdf', 'size': 25*1024*1024},  # 25 МБ
    ]
    docs, issues, status, label, reason = validate_package(files, 'regional')
    assert status == 'rejected'
    assert any('превышает 20 МБ' in i.message for i in issues)