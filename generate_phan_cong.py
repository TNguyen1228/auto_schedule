"""
Script sinh bảng Phan_Cong tự động từ 3 bảng nguồn:
1. Chuong_Trinh_Khung (Bảng A)
2. Lop_Hoc (Bảng B - kèm GV Chủ Nhiệm)
3. Giao_Vien_Bo_Mon (Bảng C - ánh xạ liên khối, bộ môn và ngoại lệ theo lớp)

Cách dùng:
    python generate_phan_cong.py
    python generate_phan_cong.py --file Input_Mau_TKB.xlsx
"""

import os
import sys
import argparse
import pandas as pd

# Đảm bảo đường dẫn import
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from data.excel_io import sync_phan_cong_to_excel, create_excel_input_template


def main():
    parser = argparse.ArgumentParser(description="Tự động sinh sheet Phan_Cong từ 3 bảng nguồn A, B, C trong Excel.")
    parser.add_argument(
        "--file", "-f",
        default=os.path.join(project_root, "Input_Mau_TKB.xlsx"),
        help="Đường dẫn tới file Excel chứa dữ liệu đầu vào (mặc định: Input_Mau_TKB.xlsx)"
    )
    parser.add_argument(
        "--create-template", "-c",
        action="store_true",
        help="Tạo mới lại toàn bộ file template Excel chuẩn với 3 bảng nguồn mẫu"
    )

    args = parser.parse_args()
    excel_path = os.path.abspath(args.file)

    print("=" * 70)
    print(" CÔNG CỤ SINH BẢNG PHÂN CÔNG GIẢNG DẠY TỰ ĐỘNG TỪ 3 BẢNG NGUỒN")
    print("=" * 70)

    if args.create_template or not os.path.exists(excel_path):
        print(f"\n[+] Đang khởi tạo file Excel mẫu 3 bảng tại: {excel_path}")
        create_excel_input_template(excel_path)
        print("\n[✓] Hoàn thành tạo file mẫu!")
        return

    print(f"\n[1] Đang đọc 3 bảng nguồn từ: {excel_path}")
    xls = pd.ExcelFile(excel_path)
    required_sheets = ["Chuong_Trinh_Khung", "Lop_Hoc", "Giao_Vien_Bo_Mon"]
    missing = [s for s in required_sheets if s not in xls.sheet_names]
    
    if missing:
        print(f"[!] Lỗi: File Excel thiếu các sheet nguồn: {missing}")
        print("    Vui lòng chạy với cờ --create-template để tạo file mẫu chuẩn.")
        sys.exit(1)

    print(f"  ✓ Sheet 'Chuong_Trinh_Khung': Khung chương trình theo khối")
    print(f"  ✓ Sheet 'Lop_Hoc': Danh sách lớp & GV chủ nhiệm")
    print(f"  ✓ Sheet 'Giao_Vien_Bo_Mon': Ánh xạ GV bộ môn/liên khối & ngoại lệ")

    print(f"\n[2] Đang xử lý quy tắc và đồng bộ vào sheet 'Phan_Cong'...")
    num_rows = sync_phan_cong_to_excel(excel_path)

    # Đọc lại và hiển thị thống kê
    df_pc = pd.read_excel(excel_path, sheet_name="Phan_Cong")
    df_lop = pd.read_excel(excel_path, sheet_name="Lop_Hoc")

    print(f"\n[3] THỐNG KÊ KẾT QUẢ PHÂN CÔNG ({num_rows} dòng đã sinh):")
    print("-" * 55)
    print(f"{'Lớp':<10} | {'Số môn':<10} | {'Tổng số tiết/tuần':<20}")
    print("-" * 55)
    for lop in df_lop["Mã Lớp"]:
        sub_df = df_pc[df_pc["Mã Lớp"] == lop]
        total_p = sub_df["Số Tiết/Tuần"].sum()
        print(f"{lop:<10} | {len(sub_df):<10} | {total_p:<20} tiết")
    print("-" * 55)

    print("\n[✓] Xong! Bạn có thể chạy ngay 'python main.py' để xếp thời khóa biểu.")


if __name__ == "__main__":
    main()

