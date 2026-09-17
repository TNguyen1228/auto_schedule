# Hệ Thống Xếp Thời Khóa Biểu Tự Động Tiểu Học (Auto Schedule)

Hệ thống xếp Thời khóa biểu tự động dành cho trường Tiểu học (học 2 buổi/ngày) sử dụng công nghệ tối ưu hóa ràng buộc **Google OR-Tools CP-SAT**. Hệ thống giải quyết trọn vẹn bài toán xếp lịch phức tạp với cấu trúc dữ liệu đầu vào chuẩn hóa 3 bảng nguồn, tự động xử lý giáo viên liên khối, giáo viên bộ môn và các ngoại lệ lớp học.

---

## 🌟 Tính Năng Nổi Bật

- **Mô hình học 2 buổi/ngày chuẩn Tiểu học**:
  - Buổi sáng: 4 tiết (Tiết 1 – 4).
  - Buổi chiều: 3 tiết (Tiết 5 – 7).
  - Chiều Thứ 6: Toàn trường nghỉ học (Tiết 5, 6, 7 đóng hoàn toàn).
  - Tổng định mức: Đúng **32 tiết thực học/lớp/tuần**.
- **Cấu trúc dữ liệu 3 bảng nguồn thông minh**: Thay vì nhập thủ công hàng trăm dòng phân công, người dùng chỉ cần quản trị 3 bảng nguồn gọn gàng; hệ thống sẽ tự động sinh bảng `Phan_Cong` đầy đủ.
- **Hỗ trợ giáo viên liên khối & ngoại lệ linh hoạt**: Tự động giải quyết các mô hình phân công phức tạp (`GV_12`, `GV_23`, `GV_45`, Ban Giám Hiệu/Phó Hiệu Trưởng dạy GDTC, ngoại lệ từng lớp).
- **Hệ thống ràng buộc toàn diện**:
  - **Ràng buộc cứng (Hard Constraints)**: Chống trùng giờ GV, chống trùng giờ lớp, tiết Chào cờ toàn trường (Thứ 2 - T1), Sinh hoạt lớp (Thứ 6 - T4), tránh các tiết GV bận/đăng ký nghỉ, giới hạn số tiết/ngày của từng môn.
  - **Tối ưu mềm (Soft Optimization)**: Phân bổ đều và hạn chế số buổi dạy trong tuần của giáo viên.
- **Bộ kiểm định độc lập (Independent Validator)**: Tự động kiểm tra và xác thực 100% ràng buộc sau khi xếp lịch.
- **Xuất file Excel chuyên nghiệp**: Tự động tạo file `Thoi_Khoa_Bieu_Truong_9_Lop.xlsx` với 2 góc nhìn: Thời khóa biểu theo từng lớp học và Thời khóa biểu theo từng giáo viên.

---

## 📁 Cấu Trúc Dự Án

```text
auto_schedule/
├── data/
│   ├── __init__.py
│   ├── assignment_generator.py      # Module giải mã quy tắc & tự sinh Phan_Cong từ 3 bảng
│   ├── excel_io.py                  # Đọc/ghi Excel, đồng bộ sheet và tạo template mẫu
│   └── sample_data.py               # Dữ liệu khởi tạo chuẩn
├── scheduler/
│   ├── __init__.py
│   ├── models.py                    # Định nghĩa Dataclass (Lớp, GV, Phân công, Slot, Config)
│   ├── timetable_solver.py          # Bộ giải toán Google OR-Tools CP-SAT
│   ├── validator.py                 # Bộ kiểm định độc lập kiểm tra vi phạm
│   └── exporter.py                  # Xuất TKB ra Console & file Excel đa giao diện
├── generate_phan_cong.py            # CLI tool: Đồng bộ/sinh tự động bảng Phan_Cong từ 3 bảng nguồn
├── main.py                          # Script chạy chính toàn bộ quy trình xếp lịch
├── Input_Mau_TKB.xlsx               # File Excel đầu vào chuẩn hóa (5 sheets)
├── Thoi_Khoa_Bieu_Truong_9_Lop.xlsx # File Excel kết quả TKB sau khi xếp
├── requirements.txt                 # Danh sách thư viện phụ thuộc
└── README.md                        # Tài liệu hướng dẫn sử dụng
```

---

## ⚡ Dành Cho Người Dùng Phổ Thông (Không Cần Gõ Lệnh)

Chỉ cần **nhấp đúp chuột** vào một trong hai file `.bat` có sẵn trong thư mục dự án:

1. **`1_CLICK_XEP_LICH.bat`** *(Khuyên dùng)*:
   - Tự động nhận diện Python, đọc dữ liệu, giải toán và kiểm định ràng buộc.
   - **Tự động mở file Excel Thời khóa biểu kết quả** ngay khi hoàn tất.
2. **`CHAY_XEP_LICH.bat`** *(Menu điều khiển)*:
   - Hiển thị bảng chọn trực quan: Xếp lịch, Đồng bộ bảng phân công, Mở file Excel đầu vào, Mở file kết quả, Khởi tạo dữ liệu mẫu.

---

## 🚀 Hướng Dẫn Cài Đặt (Dành Cho Lần Đầu)

### 1. Chuẩn bị môi trường Python (Python 3.10+)

```powershell
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.\venv\Scripts\activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 2. Sinh bảng phân công từ dữ liệu nguồn (Tùy chọn)

Nếu bạn vừa chỉnh sửa khung chương trình hoặc phân công trong file `Input_Mau_TKB.xlsx`, chạy lệnh sau để tự động cập nhật lại sheet `Phan_Cong`:

```powershell
python generate_phan_cong.py
```

*Muốn tạo mới lại file mẫu chuẩn từ đầu:*
```powershell
python generate_phan_cong.py --create-template
```

### 3. Chạy hệ thống xếp Thời khóa biểu

```powershell
python main.py
```

Hệ thống sẽ:
1. Đọc dữ liệu từ `Input_Mau_TKB.xlsx`.
2. Khởi tạo mô hình CP-SAT và giải trong vòng **< 1 giây**.
3. Chạy Validator kiểm định 100% ràng buộc cứng.
4. Xuất kết quả ra file `Thoi_Khoa_Bieu_Truong_9_Lop.xlsx`.

---

## 📊 Cấu Trúc Dữ Liệu Đầu Vào (`Input_Mau_TKB.xlsx`)

File Excel đầu vào gồm 5 sheet, trong đó người dùng chỉ cần quản lý **3 bảng nguồn chính** và danh sách giáo viên:

### 1. Bảng A — `Chuong_Trinh_Khung` (Khung chương trình theo khối)
Định nghĩa mỗi khối học môn gì, số tiết/tuần, giới hạn tiết/ngày. Không cần lặp lại theo từng lớp.

| Khối | Môn Học | Số Tiết/Tuần | Tiết Tối Đa/Ngày | Loại GV | Tiết Cố Định | Chung Toàn Trường |
|---|---|---|---|---|---|---|
| `1` | Chào cờ | 1 | 1 | `GV_CHUNG` | Thứ 2-T1 | Có |
| `1` | Sinh hoạt lớp | 1 | 1 | `CHU_NHIEM` | Thứ 6-T4 | Không |
| `1` | Toán | 3 | 1 | `CHU_NHIEM` | | Không |
| `1` | Tiếng Việt | 12 | 2 | `CHU_NHIEM` | | Không |
| `1` | TC Tiếng Việt | 1 | 1 | `CHU_NHIEM` | | Không |
| `1` | TC Tiếng Việt | 2 | 1 | `BO_MON:TC_TV` | | Không |
| `1` | Tiếng Anh | 2 | 1 | `BO_MON:ANH` | | Không |
| `4,5` | Khoa học | 2 | 2 | `BO_MON:KHOA_HOC` | | Không |
| `4,5` | LS & ĐL | 2 | 2 | `BO_MON:LS_DL` | | Không |

> **Quy ước cột Loại GV**:
> - `CHU_NHIEM`: Tự động map sang GV chủ nhiệm của từng lớp (theo Bảng B).
> - `BO_MON:<loại>`: Tra cứu mã GV thực tế theo khối/lớp trong Bảng C.
> - Mã GV trực tiếp (như `GV_CHUNG`, `GV_12`, `PHT`): Gán trực tiếp giáo viên đó.
> - **Khối học chung**: Có thể khai nhóm khối phân cách bằng dấu phẩy (VD: `4,5` hoặc `1,2,3`).

### 2. Bảng B — `Lop_Hoc` (Danh sách lớp & GV Chủ nhiệm)
Khai báo danh sách các lớp học và phân công GVCN.

| Mã Lớp | Tên Lớp | Khối | GV Chủ Nhiệm |
|---|---|---|---|
| 1A | Lớp 1A | 1 | GV_1A |
| 1B | Lớp 1B | 1 | GV_1B |
| 2A | Lớp 2A | 2 | GV_2A |
| 2B | Lớp 2B | 2 | GV_2B |
| 3A | Lớp 3A | 3 | GV_3A |
| 4A | Lớp 4A | 4 | GV_4A |
| 4B | Lớp 4B | 4 | GV_4B |
| 5A | Lớp 5A | 5 | GV_5A |
| 5B | Lớp 5B | 5 | GV_5B |

### 3. Bảng C — `Giao_Vien_Bo_Mon` (Ánh xạ GV bộ môn, liên khối & ngoại lệ)
Map theo cặp `(Khối/Lớp, Môn/Loại) -> Mã GV`. Hỗ trợ xử lý môn liên khối và ngoại lệ riêng theo từng lớp:

| Khối/Lớp | Môn/Loại | Mã GV | Ghi Chú |
|---|---|---|---|
| Tất cả | ANH | GV_ANH | Tiếng Anh toàn trường |
| Tất cả | NHAC | GV_NHAC | Âm nhạc toàn trường |
| Tất cả | HOA | GV_HOA | Mỹ thuật toàn trường |
| Tất cả | TIN | GV_TIN | Tin học toàn trường |
| 1 | GDTC | GV_12 | Thể dục Khối 1 do GV liên khối 1-2 dạy |
| 2 | GDTC | PHT | Thể dục Khối 2 do Phó Hiệu Trưởng phụ trách |
| 3,4,5 | GDTC | GV_TD | Thể dục Khối 3-5 do GV chuyên trách |
| 1 | TC_TOAN | GV_12 | TC Toán Khối 1 |
| 2 | TC_TOAN | GV_23 | TC Toán Khối 2 |
| 2 | DAO_DUC | GV_12 | Đạo đức Khối 2 mặc định GV_12 |
| **2B** | **DAO_DUC** | **GV_23** | **NGOẠI LỆ: Riêng lớp 2B học Đạo đức với GV_23** |
| 4,5 | KHOA_HOC | GV_45 | Khoa học Khối 4, 5 |
| 4,5 | LS_DL | GV_45 | Lịch sử & Địa lý Khối 4, 5 |

### 4. Sheet `Giao_Vien` (Danh sách GV & Lịch bận đăng ký)
- Cột `Mã GV`: Mã định danh giáo viên.
- Cột `Tên Giáo Viên`: Tên hiển thị trên TKB.
- Cột `Tiết Bận Đăng Ký`: Các tiết GV đăng ký nghỉ (VD: `Thứ 3-T1, Thứ 3-T2`). Solver cam kết **không bao giờ xếp tiết** vào các khung giờ này.

### 5. Sheet `Phan_Cong` (Sheet Tự Sinh)
- Được sinh tự động hoàn toàn từ Bảng A + B + C thông qua script `generate_phan_cong.py` hoặc tự động khi chạy `main.py`.
- Người dùng có thể xem lại để kiểm tra số tiết/tuần của từng lớp (đúng chuẩn 32 tiết/lớp).
- **Tính tương thích ngược**: Nếu file Excel chỉ có sheet `Phan_Cong` mà không có các bảng A, B, C, hệ thống vẫn tự động đọc trực tiếp từ `Phan_Cong` mà không báo lỗi.

---

## 📈 Kết Quả Đầu Ra (`Thoi_Khoa_Bieu_Truong_9_Lop.xlsx`)

Sau khi giải thành công, kết quả được xuất ra file Excel với định dạng trực quan:
1. **Sheet `TKB_Theo_Lop`**:
   - Bảng thời khóa biểu tuần của từng lớp (1A đến 5B).
   - Phân tách rõ ràng buổi Sáng (Tiết 1–4) và Chiều (Tiết 5–7).
   - Đánh dấu ô `[NGHỈ CHIỀU]` màu xám cho chiều Thứ 6.
   - Tô màu nổi bật các tiết đặc thù: Chào cờ (vàng nhạt), Sinh hoạt lớp (xanh lá nhạt).
2. **Sheet `TKB_Theo_Giao_Vien`**:
   - Lịch dạy tổng hợp của từng giáo viên trong tuần.
   - Đánh dấu rõ các tiết bận/đăng ký nghỉ bằng ô `[BẬN]` màu đỏ gạch.
   - Giúp Ban Giám hiệu dễ dàng theo dõi và giám sát khối lượng giảng dạy.

---

## ⚙️ Các Ràng Buộc Được Áp Dụng (Constraints)

| Mã | Loại | Mô tả ràng buộc |
|---|---|---|
| **H0** | Cứng | Khóa toàn bộ các tiết nghỉ cố định (Chiều Thứ 6 - Tiết 5, 6, 7). |
| **H1** | Cứng | Đạt chính xác 100% định mức số tiết/tuần theo chương trình khung. |
| **H2** | Cứng | Một lớp tại một thời điểm chỉ học tối đa 1 môn (Không trùng lịch lớp). |
| **H3** | Cứng | Một GV tại một thời điểm chỉ dạy 1 lớp (Không trùng lịch GV, trừ tiết Chào cờ chung). |
| **H4** | Cứng | Tuyệt đối không xếp tiết vào khung giờ GV đã đăng ký bận/nghỉ. |
| **H5** | Cứng | Cố định tiết Chào cờ vào **Thứ 2 Tiết 1**, Sinh hoạt lớp vào **Thứ 6 Tiết 4** toàn trường. |
| **H6** | Cứng | Khống chế số tiết tối đa trong ngày của môn học (tránh dồn tiết). |
| **H7** | Mềm | Tối ưu hóa số buổi đến trường của giáo viên (khuyến khích không quá 7 buổi/tuần). |

---

## 🛠️ Yêu Cầu Kỹ Thuật

- **Python**: 3.10 trở lên
- **Thư viện chính**:
  - `ortools >= 9.7`: Bộ giải Google OR-Tools CP-SAT.
  - `openpyxl >= 3.1.0`: Đọc/ghi và định dạng nâng cao bảng tính Excel.
  - `pandas >= 2.0.0`: Xử lý và chuyển đổi cấu trúc dữ liệu.

---

## 📄 Bản Quyền (License)

Dự án được phân phối dưới giấy phép **MIT License**.
