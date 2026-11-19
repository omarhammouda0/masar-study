"""Run with: python -m pytest -q (pytest/httpx may need installation)."""
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
import server

client=TestClient(server.app)


def good_payload():
    return {
        'full_name':'Student Demo','phone':'+201234567890','email':'demo@example.com',
        'nationality':'Egyptian','destination':'Germany','degree':'Master',
        'target_major':'Computer Science','study_language':'English',
        'current_qualification':'Bachelor','privacy_consent':'on'
    }


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv('PRIVACY_POLICY_APPROVED',raising=False)
    assert client.get('/api/config').json()['form_enabled'] is False
    assert client.post('/api/assessment',data=good_payload()).status_code == 503


def test_sent_as_email_only_and_document_attached(monkeypatch):
    for key in ('SMTP_HOST','SMTP_PORT','SMTP_USER','SMTP_PASSWORD','SMTP_FROM','INBOX_EMAIL'):
        monkeypatch.setenv(key,'test' if key!='SMTP_PORT' else '587')
    monkeypatch.setenv('PRIVACY_POLICY_APPROVED','true')
    captured=[]
    monkeypatch.setattr(server,'deliver_email',captured.append)
    server.RATE.clear()
    response=client.post('/api/assessment',data=good_payload(),files=[('documents',('grade.pdf',b'%PDF-1.4\nTEST', 'application/pdf'))])
    assert response.status_code == 200, response.text
    assert response.json()['ok'] is True
    assert len(captured)==1
    assert len(list(captured[0].iter_attachments()))==1
    assert 'Student Demo' in captured[0].get_body(preferencelist=('plain',)).get_content()


def test_reject_fake_pdf(monkeypatch):
    for key in ('SMTP_HOST','SMTP_PORT','SMTP_USER','SMTP_PASSWORD','SMTP_FROM','INBOX_EMAIL'):
        monkeypatch.setenv(key,'test' if key!='SMTP_PORT' else '587')
    monkeypatch.setenv('PRIVACY_POLICY_APPROVED','true')
    server.RATE.clear()
    response=client.post('/api/assessment',data=good_payload(),files=[('documents',('grade.pdf',b'NOT A PDF', 'application/pdf'))])
    assert response.status_code==400
