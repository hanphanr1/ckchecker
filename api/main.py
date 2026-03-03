from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import re
import time
import random
import string
import logging
import urllib.parse
from datetime import datetime, timedelta
import httpx
import hashlib

# Import các module tự viết
from utils.parser import parse_cookie_content, extract_netflix_id, extract_email_from_cookie
from utils.generator import generate_account_info, generate_token
from utils.telegram import send_telegram_hit, test_telegram_bot

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Netflix Cookies Checker API",
    version="1.0.0",
    description="API for checking Netflix cookies and generating login tokens",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class CheckRequest(BaseModel):
    content: str
    mode: str

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

# Cache cho account info
account_cache = {}
cache_ttl = 300  # 5 phút

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
        <head><title>Netflix Cookies Checker</title></head>
        <body>
            <h1>Netflix Cookies Checker API</h1>
            <p>API is running. Please upload static files.</p>
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

# ==================== API ENDPOINTS ====================

@app.get("/openapi.json")
async def get_openapi():
    return app.openapi()

@app.post("/api/telegram-config")
async def set_telegram_config(config: TelegramConfig):
    """Lưu cấu hình Telegram"""
    try:
        global telegram_configs
        telegram_configs = {
            "enabled": config.enabled,
            "bot_token": config.bot_token,
            "chat_id": config.chat_id
        }
        
        # Test connection nếu enabled
        if config.enabled and config.bot_token and config.chat_id:
            test_result = await test_telegram_bot(config.bot_token, config.chat_id)
            if not test_result:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "Telegram bot không hợp lệ hoặc Chat ID sai"
                    }
                )
        
        logger.info(f"Telegram config saved: enabled={config.enabled}")
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Cấu hình Telegram đã được lưu"
        })
        
    except Exception as e:
        logger.error(f"Error saving telegram config: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

@app.post("/api/check")
async def check_cookie(request: CheckRequest):
    """Check cookie đơn lẻ"""
    try:
        logger.info(f"Processing cookie request, mode: {request.mode}")
        
        # Parse cookie
        cookie_data = parse_cookie_content(request.content)
        netflix_id = extract_netflix_id(cookie_data)
        
        if not netflix_id:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "error",
                    "message": "Không tìm thấy NetflixId trong cookie. Vui lòng kiểm tra lại định dạng cookie."
                }
            )
        
        # Kiểm tra cache
        cache_key = hashlib.md5(netflix_id.encode()).hexdigest()
        if cache_key in account_cache:
            cache_time, account_info, token_result = account_cache[cache_key]
            if time.time() - cache_time < cache_ttl:
                logger.info(f"Using cached account info for {netflix_id}")
            else:
                # Cache hết hạn, tạo mới
                account_info = generate_account_info(cookie_data, request.content)
                token_result = generate_token(cookie_data, netflix_id)
                account_cache[cache_key] = (time.time(), account_info, token_result)
        else:
            # Tạo mới
            account_info = generate_account_info(cookie_data, request.content)
            token_result = generate_token(cookie_data, netflix_id)
            account_cache[cache_key] = (time.time(), account_info, token_result)
        
        # Gửi Telegram nếu được bật
        telegram_sent = False
        if telegram_configs.get('enabled') and account_info.get('ok', False):
            telegram_sent = await send_telegram_hit(
                account_info, 
                token_result, 
                request.content,
                telegram_configs
            )
        
        # Trả về kết quả theo mode
        result = {
            "status": "success",
            "account_info": account_info,
            "token_result": token_result,
            "telegram_sent": telegram_sent
        }
        
        if request.mode == 'tokenonly':
            result = {
                "status": "success",
                "token_result": token_result,
                "telegram_sent": telegram_sent
            }
        
        return JSONResponse(status_code=200, content=result)
        
    except Exception as e:
        logger.error(f"Error in check_cookie: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Lỗi xử lý: {str(e)}"
            }
        )

@app.post("/api/batch-check")
async def batch_check(
    files: List[UploadFile] = File(...),
    mode: str = Form("fullinfo")
):
    """Check nhiều file cookie"""
    try:
        logger.info(f"Processing batch request with {len(files)} files, mode: {mode}")
        results = []
        
        for file in files:
            try:
                content = (await file.read()).decode('utf-8', errors='ignore')
                cookie_data = parse_cookie_content(content)
                netflix_id = extract_netflix_id(cookie_data)
                
                if not netflix_id:
                    results.append({
                        "status": "error",
                        "filename": file.filename,
                        "message": "Không tìm thấy NetflixId"
                    })
                    continue
                
                # Kiểm tra cache
                cache_key = hashlib.md5(netflix_id.encode()).hexdigest()
                if cache_key in account_cache:
                    cache_time, account_info, token_result = account_cache[cache_key]
                    if time.time() - cache_time < cache_ttl:
                        logger.info(f"Using cached account info for {netflix_id}")
                    else:
                        account_info = generate_account_info(cookie_data, content)
                        token_result = generate_token(cookie_data, netflix_id)
                        account_cache[cache_key] = (time.time(), account_info, token_result)
                else:
                    account_info = generate_account_info(cookie_data, content)
                    token_result = generate_token(cookie_data, netflix_id)
                    account_cache[cache_key] = (time.time(), account_info, token_result)
                
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
                
                # Gửi Telegram nếu được bật
                if telegram_configs.get('enabled') and account_info.get('ok', False):
                    await send_telegram_hit(
                        account_info, 
                        token_result, 
                        content,
                        telegram_configs
                    )
                    
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                results.append({
                    "status": "error",
                    "filename": file.filename,
                    "message": str(e)
                })
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error in batch_check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

# ==================== RUN LOCAL ====================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)