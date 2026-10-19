"""Real browser and HTTP smoke tests against an isolated, unmocked application."""
import json
import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deliverables/browser_tools'))
from playwright.sync_api import sync_playwright
import requests

rows = []
base = 'http://127.0.0.1:18019'
with tempfile.TemporaryDirectory(prefix='expense-live-test-') as folder:
    env = os.environ.copy()
    env.update(DATABASE_URL='sqlite:///'+(Path(folder)/'test.db').as_posix(),
               AUTO_CREATE_SCHEMA='true', TRUSTED_HOSTS='', APP_ENV='development')
    process = subprocess.Popen([str(ROOT/'venv/Scripts/python.exe'), '-m', 'uvicorn',
                                'app.main:app', '--host', '127.0.0.1', '--port', '18019'],
                               cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            if process.poll() is not None:
                raise RuntimeError('Isolated server exited')
            try:
                if requests.get(base+'/api/ready', timeout=1).status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(.5)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='msedge', headless=True)
            context = browser.new_context(service_workers='block', locale='vi-VN')
            page = context.new_page()
            page.set_default_timeout(15000)
            password = 'Test!'+secrets.token_hex(12)
            user = 'live_'+secrets.token_hex(5)
            page.goto(base+'/register')
            page.locator('#register-username').fill(user)
            page.locator('#register-email').fill(user+'@example.com')
            page.locator('#register-password').fill(password)
            page.locator('#register-confirm-password').fill(password)
            page.get_by_role('button', name='Tạo tài khoản', exact=True).click()
            page.wait_for_url('**/login')
            rows.append(dict(service='Browser registration', status='PASS'))
            page.locator('#identifier').fill(user)
            page.locator('#login-password').fill(password)
            page.get_by_role('button', name='Đăng nhập', exact=True).click()
            page.wait_for_url('**/dashboard')
            rows.append(dict(service='Browser login', status='PASS'))
            for route in ['dashboard','transactions','categories','budgets','goals','reports','assistant']:
                failures=[]
                errors=[]
                def on_response(response):
                    if '/api/' in response.url and response.status >= 400:
                        failures.append(response.status)
                def on_error(error):
                    errors.append(type(error).__name__)
                page.on('response',on_response)
                page.on('pageerror',on_error)
                page.goto(base+'/'+route)
                page.wait_for_load_state('networkidle')
                visible = page.locator('.page').first.is_visible()
                rows.append(dict(service='Browser '+route, status='PASS' if visible and not failures and not errors else 'FAIL',
                                 api_errors=failures, js_errors=errors))
                page.remove_listener('response',on_response)
                page.remove_listener('pageerror',on_error)
            page.screenshot(path=str(ROOT/'deliverables/live-browser-20260919.png'), full_page=True)
            context.close()
            browser.close()
    except Exception as error:
        rows.append(dict(service='Browser smoke', status='FAIL', error=type(error).__name__))
    finally:
        process.terminate()
        process.wait(timeout=15)
    (ROOT/'deliverables/live-browser-results-20260919.json').write_text(json.dumps(rows,indent=2), encoding='utf-8')
    print(json.dumps(rows),flush=True)
