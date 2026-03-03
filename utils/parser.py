import json
import re
import urllib.parse
from typing import Dict, Optional, List, Any

def parse_cookie_content(content: str) -> Dict[str, str]:
    """Parse cookie từ nhiều định dạng khác nhau"""
    cookies = {}
    
    # Format 1: JSON array (từ extension)
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'name' in item and 'value' in item:
                    cookies[item['name']] = item['value']
            return cookies
    except:
        pass
    
    # Format 2: JSON object
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # Nếu là dict chứa cookies
            for key in ['cookies', 'cookie', 'data']:
                if key in data and isinstance(data[key], dict):
                    cookies.update(data[key])
                    return cookies
            
            # Nếu là dict trực tiếp
            for key in ['netflixId', 'NetflixId', 'SecureNetflixId']:
                if key in data:
                    cookies[key] = data[key]
            return cookies
    except:
        pass
    
    # Format 3: Netscape format (domain\tflag\tpath\tsecure\texpiry\tname\tvalue)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        parts = line.split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            cookies[name] = value
        else:
            # Format key=value
            if '=' in line:
                # Tách theo dấu ; nếu có
                cookie_parts = line.split(';')
                for part in cookie_parts:
                    if '=' in part:
                        k, v = part.strip().split('=', 1)
                        cookies[k] = v
    
    return cookies

def extract_netflix_id(cookie_data: Dict[str, str]) -> Optional[str]:
    """Trích xuất NetflixId từ cookie data"""
    # Tìm trong các tên phổ biến
    for name in ['netflixId', 'NetflixId', 'netflix_id']:
        if name in cookie_data:
            value = cookie_data[name]
            # Decode URL encoding nếu cần
            if value.startswith('v%3D') or '%' in value:
                try:
                    value = urllib.parse.unquote(value)
                except:
                    pass
            return value
    
    # Tìm bằng regex trong toàn bộ cookie string
    all_cookies = ' '.join([f"{k}={v}" for k, v in cookie_data.items()])
    match = re.search(r'netflixId[=:]\s*["\']?([a-f0-9%-]+)["\']?', all_cookies, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None

def extract_email_from_cookie(content: str) -> Optional[str]:
    """Trích xuất email từ nội dung cookie (từ filename hoặc nội dung)"""
    # Tìm trong filename pattern: ___something@email.com_.txt
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, content)
    if match:
        return match.group(1)
    return None

def extract_country_from_filename(filename: str) -> str:
    """Trích xuất country code từ filename"""
    # Pattern: ___NP___ hoặc ___US___
    match = re.search(r'___([A-Z]{2})___', filename)
    if match:
        return match.group(1)
    return "US"

def extract_name_from_filename(filename: str) -> str:
    """Trích xuất tên từ filename"""
    # Pattern: something@email.com_ hoặc trước @
    match = re.search(r'([a-zA-Z0-9._%+-]+)@', filename)
    if match:
        return match.group(1).split('_')[-1] if '_' in match.group(1) else match.group(1)
    return "User"