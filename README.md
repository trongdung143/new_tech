# Natural Language to SQL Query Generation

Một ứng dụng web thông minh cho phép bạn chuyển đổi câu hỏi bằng tiếng tự nhiên (Tiếng Việt/Tiếng Anh) thành các truy vấn SQL, tự động thực thi chúng trên database và hiển thị kết quả.

## Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/trongdung143/new_tech.git
cd new_tech
```

### 2. Tạo virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment variables

Tạo file `.env` ở thư mục gốc project với nội dung:

```env
# Google Generative AI
GOOGLE_API_KEY=<your-google-api-key>

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
DB_NAME=<your-database-name>
```

**Cách lấy Google API Key:**
1. Truy cập [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy API key vào file `.env`

## Chạy ứng dụng

### Option 1: Chạy với uvicorn (Development)
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Chạy trực tiếp
```bash
python -m uvicorn src.main:app --reload
```

Ứng dụng sẽ chạy tại: `http://localhost:8000`

## Cách sử dụng

### 1. Đăng nhập
- Nhập **Họ và tên** và **Email** vào form
- Nhấn **Tiếp tục** để vào ứng dụng

### 2. Chọn chế độ
- Auto Mode (Mặc định): Tự động thực thi SQL, chỉ hiển thị kết quả
- Manual Mode: Hiển thị SQL trước khi thực thi, cho phép xem và kiểm tra

### 3. Nhập câu hỏi
- Ví dụ tiếng Việt: "Lấy tất cả khách hàng có tên chứa 'Việt'"
- Ví dụ tiếng Anh: "Show all users where age > 25"

### 4. Nhận kết quả
- Auto Mode: Kết quả được hiển thị tự động trong bảng
- Manual Mode: Xem SQL, nhấn **Thực thi SQL** để chạy truy vấn

