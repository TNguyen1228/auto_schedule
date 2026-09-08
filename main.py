import os
import sys

# Thêm thư mục hiện tại vào sys.path nếu cần
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from data.sample_data import get_sample_school_data
from data.excel_io import create_excel_input_template, load_data_from_excel
from scheduler.timetable_solver import TimetableSolver
from scheduler.validator import TimetableValidator
from scheduler.exporter import TimetableExporter

def run_pipeline():
    excel_input_path = os.path.join(current_dir, "Input_Mau_TKB.xlsx")
    
    # Tạo file mẫu nếu chưa có
    if not os.path.exists(excel_input_path):
        create_excel_input_template(excel_input_path)

    print("=" * 80)
    print(" HỆ THỐNG XẾP THỜI KHÓA BIỂU TỰ ĐỘNG - GOOGLE OR-TOOLS CP-SAT")
    print(" RÀNG BUỘC CỨNG (HARD CONSTRAINTS) - 5 CẤP HỌC (9 LỚP)")
    print("=" * 80)

    # Đọc dữ liệu từ file Excel template
    print(f"\n[1] ĐANG ĐỌC DỮ LIỆU ĐẦU VÀO TỪ FILE EXCEL: {excel_input_path}...")
    config, classes, teachers, assignments = load_data_from_excel(excel_input_path)
    print(f"\n[1] KHỞI TẠO DỮ LIỆU ĐẦU VÀO:")
    print(f"  - Số ngày trong tuần: {len(config.days)} ({', '.join(config.days)})")
    print(f"  - Khung giờ học: Sáng {len(config.morning_periods)} tiết (1-4), Chiều {len(config.afternoon_periods)} tiết (5-7)")
    print(f"  - Chiều Thứ 6: Toàn trường nghỉ học (Tiết 5, 6, 7)")
    print(f"  - Tổng số tiết thực học: {config.total_active_slots_per_week} tiết/lớp/tuần")
    print(f"  - Số lớp học: {len(classes)} lớp thuộc 5 khối ({', '.join(c.id for c in classes)})")
    print(f"  - Số giáo viên: {len(teachers)} giáo viên")
    print(f"  - Tổng số phân công chuyên môn: {len(assignments)} nhiệm vụ")
    
    total_assigned_periods = sum(a.periods_per_week for a in assignments)
    print(f"  - Tổng số tiết cần xếp: {total_assigned_periods} tiết (Trung bình {total_assigned_periods / len(classes):.1f} tiết/lớp)")

    # Hiển thị một số lịch bận của GV
    print("\n  * Danh sách lịch bận đã đăng ký của giáo viên:")
    has_busy = False
    for t in teachers:
        if t.unavailable_slots:
            has_busy = True
            slots_str = ", ".join(f"{d}-T{p}" for d, p in sorted(t.unavailable_slots))
            print(f"    + {t.name} ({t.id}): Nghỉ các tiết [{slots_str}]")
    if not has_busy:
        print("    + Không có giáo viên nào đăng ký nghỉ.")

    # 2. KHỞI CHẠY BỘ GIẢI VỚI RÀNG BUỘC CỨNG
    print(f"\n[2] THIẾT LẬP MÔ HÌNH VÀ GIẢI TOÁN (CP-SAT SOLVER)...")
    solver = TimetableSolver(
        config=config,
        classes=classes,
        teachers=teachers,
        assignments=assignments
    )
    
    result = solver.solve(time_limit_seconds=30.0)

    # 3. XUẤT KẾT QUẢ & ĐÁNH GIÁ
    print(f"\n[3] KẾT QUẢ TÌM NGHIỆM:")
    exporter = TimetableExporter(
        config=config,
        classes=classes,
        teachers=teachers,
        assignments=assignments,
        result=result
    )
    exporter.print_summary()

    if result.status not in ('OPTIMAL', 'FEASIBLE'):
        print("[!] BÀI TOÁN KHÔNG CÓ NGHIỆM. Vui lòng xem thông báo lỗi phía trên.")
        return

    # 4. BỘ KIỂM ĐỊNH ĐỘC LẬP (VALIDATOR)
    print(f"\n[4] KIỂM ĐỊNH TOÀN BỘ RÀNG BUỘC CỨNG (INDEPENDENT VALIDATION)...")
    validator = TimetableValidator(
        config=config,
        classes=classes,
        teachers=teachers,
        assignments=assignments,
        result=result
    )
    is_valid, violations = validator.validate_all()

    if is_valid:
        print("  -> [THÀNH CÔNG RỰC RỠ] 100% RÀNG BUỘC CỨNG ĐƯỢC THỎA MÃN:")
        print("     [x] Không có xung đột trùng giờ giáo viên.")
        print("     [x] Không có xung đột trùng giờ lớp học.")
        print("     [x] Đạt chính xác 100% định mức số tiết các môn.")
        print("     [x] Tiết Chào cờ xếp chuẩn xác vào Thứ 2 Tiết 1 cho toàn bộ 9 lớp.")
        print("     [x] Tiết Sinh hoạt lớp xếp chuẩn xác vào Thứ 6 Tiết 4 (cuối tuần trước khi nghỉ chiều) cho toàn bộ 9 lớp.")
        print("     [x] Đóng hoàn toàn các tiết chiều Thứ 6 (Tiết 5, 6, 7 không có lịch học).")
        print("     [x] Tuyệt đối không xếp tiết vào các khung giờ giáo viên đăng ký nghỉ.")
        print("     [x] Không vượt quá giới hạn số tiết/ngày quy định của từng môn.")
    else:
        print(f"  -> [CẢNH BÁO] Phát hiện {len(violations)} vi phạm ràng buộc cứng:")
        for v in violations:
            print(f"     [!] {v}")

    # 5. XUẤT BẢNG MẪU VÀ FILE EXCEL
    print(f"\n[5] XUẤT THỜI KHÓA BIỂU:")

    excel_file = os.path.join(current_dir, "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx")
    exporter.export_to_excel(excel_file)
    print(f"\nĐã hoàn thành toàn bộ quy trình! File kết quả lưu tại: {excel_file}")

if __name__ == '__main__':
    run_pipeline()
