"""Explicit live-service smoke checks; never print credentials or provider bodies."""
import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
import requests
load_dotenv(ROOT / '.env')

def web():
    base = os.environ['FRONTEND_URL'].rstrip('/')
    rows = []
    for path in ['/', '/login', '/api/health', '/api/ready', '/api/unknown-live-test']:
        start = time.monotonic()
        try:
            r = requests.get(base + path, timeout=(10, 25))
            expected = 404 if 'unknown' in path else 200
            content_type = r.headers.get('Content-Type', '')
            passed = r.status_code == expected and r.url.startswith('https://')
            if path in ['/api/health', '/api/ready']:
                passed = passed and 'application/json' in content_type
            if 'unknown' in path:
                passed = passed and 'text/html' not in content_type
            rows.append(dict(service='production'+path, status='PASS' if passed else 'FAIL',
                             http=r.status_code, content_type=content_type,
                             seconds=round(time.monotonic()-start, 2)))
        except requests.RequestException as e:
            rows.append(dict(service='production'+path, status='BLOCKED', error=type(e).__name__))
    return rows

def gemini():
    from app.core.gemini import generate_financial_advice, configured_model
    start = time.monotonic()
    try:
        answer = generate_financial_advice(
            'Đây là dữ liệu kiểm thử giả lập. Hãy nêu ngắn gọn số tiền còn lại từ tổng thu trừ tổng chi.',
            {'period': '2026-09', 'income': 1000000, 'expense': 200000, 'net': 800000}, [])
        return [dict(service='Gemini live adapter', status='PASS' if answer.strip() else 'FAIL',
                     model=configured_model(), answer_chars=len(answer), seconds=round(time.monotonic()-start, 2),
                     scope='Real provider request, synthetic aggregates, non-empty response; semantic accuracy not certified')]
    except Exception as e:
        return [dict(service='Gemini live adapter', status='FAIL', model=configured_model(),
                     error=type(e).__name__, seconds=round(time.monotonic()-start, 2))]

def resend():
    try:
        r = requests.get('https://api.resend.com/domains', headers={
            'Authorization': 'Bearer '+os.environ.get('RESEND_API_KEY','')}, timeout=(10,20))
        return [dict(service='Resend domains read-only', status='PASS' if r.status_code == 200 else 'INCONCLUSIVE',
                     http=r.status_code, scope='Connectivity/API access only; 403 may mean send-only key; no email sent')]
    except requests.RequestException as e:
        return [dict(service='Resend domains read-only', status='BLOCKED', error=type(e).__name__)]

if __name__ == '__main__':
    rows = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(lambda fn: fn(), [web, gemini, resend]):
            rows.extend(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    output = ROOT / 'deliverables/live-service-results-20260919.json'
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
