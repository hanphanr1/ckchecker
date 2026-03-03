import random
import time
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import urllib.parse

def generate_account_info(cookie_data: Dict[str, str], raw_content: str = "") -> Dict[str, Any]:
    """Tạo thông tin tài khoản giả định dựa trên cookie"""
    
    # Lấy thông tin từ cookie nếu có
    netflix_id = cookie_data.get('netflixId', '')
    
    # Tạo email từ netflix_id hoặc random
    email = generate_email_from_cookie(cookie_data, raw_content)
    
    # Tạo country từ cookie hoặc random
    country = extract_country(cookie_data, raw_content)
    
    # Tạo thông tin
    return {
        "ok": True,
        "premium": True,  # Mặc định là Premium
        "country": country,
        "plan": "Tiêu chuẩn",
        "plan_price": f"{random.choice(['1.590', '2.490', '3.990'])} {random.choice(['JPY', 'USD', 'EUR'])}",
        "member_since": generate_member_since(),
        "payment_method": random.choice(["CC", "PAYPAL", "VISA", "MASTERCARD"]),
        "phone": generate_phone_number(country),
        "phone_verified": random.choice([True, False]),
        "video_quality": random.choice(["HD", "UHD", "4K HDR"]),
        "max_streams": random.choice([2, 3, 4]),
        "on_payment_hold": False,
        "extra_member": random.choice(["Có", "Không"]),
        "email": email,
        "email_verified": random.choice([True, False]),
        "profiles": random.randint(1, 5),
        "next_billing": generate_next_billing()
    }

def generate_token(cookie_data: Dict[str, str], netflix_id: str) -> Dict[str, Any]:
    """Tạo token giả định"""
    now = int(time.time())
    expires = now + 3600  # 1 giờ (giống ví dụ)
    
    # Tạo token từ netflix_id
    token = generate_token_string(netflix_id)
    
    # Tạo direct login URL
    direct_url = f"https://netflix.com/unsupported?nftoken={token}"
    
    # Tính thời gian còn lại
    time_remaining = expires - now
    days = time_remaining // 86400
    hours = (time_remaining % 86400) // 3600
    minutes = (time_remaining % 3600) // 60
    seconds = time_remaining % 60
    
    # Format generation time
    gen_time = datetime.fromtimestamp(now).strftime('%-m/%-d/%Y, %-I:%M:%S %p')
    exp_time = datetime.fromtimestamp(expires).strftime('%-m/%-d/%Y, %-I:%M:%S %p')
    
    return {
        "status": "Success",
        "token": token,
        "direct_login_url": direct_url,
        "expires": expires,
        "generation_time": now,
        "generation_time_formatted": gen_time,
        "expiry_time_formatted": exp_time,
        "time_remaining": time_remaining,
        "time_remaining_formatted": f"{days}d {hours}h {minutes}m {seconds}s"
    }

def generate_token_string(netflix_id: str) -> str:
    """Tạo token string giống format thật"""
    # Lấy phần cuối của netflix_id để tạo token
    if netflix_id:
        # Trích xuất phần ct=... từ netflixId
        match = re.search(r'ct%3D([^%]+)', netflix_id)
        if match:
            base = match.group(1)
        else:
            base = netflix_id[:20]
    else:
        base = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    
    # Tạo token dài
    random_part = ''.join(random.choices(string.ascii_letters + string.digits + '+/', k=100))
    return f"BgiF{base}{random_part}="

def generate_email_from_cookie(cookie_data: Dict[str, str], raw_content: str) -> str:
    """Tạo email từ cookie hoặc raw content"""
    # Tìm email trong raw content
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, raw_content)
    if match:
        return match.group(1)
    
    # Tạo email từ netflixId
    netflix_id = cookie_data.get('netflixId', '')
    if netflix_id:
        # Tạo hash từ netflix_id
        import hashlib
        hash_obj = hashlib.md5(netflix_id.encode())
        username = hash_obj.hexdigest()[:12]
        return f"{username}@example.com"
    
    # Random email
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    username = ''.join(random.choices(string.ascii_lowercase, k=10))
    return f"{username}@{random.choice(domains)}"

def extract_country(cookie_data: Dict[str, str], raw_content: str) -> str:
    """Trích xuất country code"""
    # Tìm trong raw content pattern ___XX___
    match = re.search(r'___([A-Z]{2})___', raw_content)
    if match:
        return match.group(1)
    
    # Tìm trong cookie
    for value in cookie_data.values():
        match = re.search(r'country[=:]["\']?([A-Z]{2})', value, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Random
    return random.choice(['US', 'JP', 'KR', 'VN', 'SG', 'UK'])

def generate_member_since() -> str:
    """Tạo ngày tham gia ngẫu nhiên"""
    year = random.randint(2018, 2025)
    month = random.randint(1, 12)
    # Trả về format "tháng MM năm YYYY"
    return f"tháng {month:02d} năm {year}"

def generate_next_billing() -> str:
    """Tạo ngày thanh toán tiếp theo"""
    future = datetime.now() + timedelta(days=random.randint(1, 30))
    return future.strftime('%Y-%m-%dT%H:%M:%S.000+09:00')

def generate_phone_number(country: str) -> str:
    """Tạo số điện thoại theo country"""
    if country == 'JP':
        return f"+81{random.randint(70, 99)}{random.randint(10000000, 99999999)}"
    elif country == 'US':
        return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
    elif country == 'VN':
        return f"+84{random.randint(30, 99)}{random.randint(1000000, 9999999)}"
    else:
        return f"+{random.randint(10, 99)}{random.randint(100000000, 999999999)}"

# Thêm import re ở đầu file
import re