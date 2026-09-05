import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Tuple, List, Set, Dict

from scheduler.models import (
    ScheduleConfig,
    ClassGroup,
    Teacher,
    TeachingAssignment
)

def create_excel_input_template(file_path: str = "Input_Mau_TKB.xlsx"):
    """
    Tạo file Excel mẫu chuẩn Tiểu học (Sáng 4 tiết, Chiều 3 tiết, Chiều Thứ 6 nghỉ):
    - Sheet 1: Lop_Hoc (Mã lớp, Tên lớp, Khối)
    - Sheet 2: Giao_Vien (Mã GV, Tên GV, Lịch bận)
    - Sheet 3: Phan_Cong (Mã lớp, Môn học, Mã GV, Số tiết/tuần, Tiết tối đa/ngày, Tiết cố định, Hoạt động chung)
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    from data.sample_data import get_sample_school_data
    _, classes, teachers, sample_assignments = get_sample_school_data()

    # 1. SHEET LOP_HOC
    ws_classes = wb.create_sheet(title="Lop_Hoc")
    headers1 = ["Mã Lớp", "Tên Lớp", "Khối Học (1-5)"]
    for i, h in enumerate(headers1, 1):
        c = ws_classes.cell(row=1, column=i, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal='center')

    for r_idx, c in enumerate(classes, 2):
        row_data = [c.id, c.name, c.grade]
        for c_idx, val in enumerate(row_data, 1):
            cell = ws_classes.cell(row=r_idx, column=c_idx, value=val)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')

    # 2. SHEET GIAO_VIEN
    ws_teachers = wb.create_sheet(title="Giao_Vien")
    headers2 = ["Mã GV", "Tên Giáo Viên", "Tiết Bận Đăng Ký (VD: Thứ 5-T3, Thứ 5-T4)"]
    for i, h in enumerate(headers2, 1):
        c = ws_teachers.cell(row=1, column=i, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal='center')

    for r_idx, t in enumerate(teachers, 2):
        busy_str = ", ".join(f"{d}-T{p}" for d, p in sorted(t.unavailable_slots)) if t.unavailable_slots else ""
        row_data = [t.id, t.name, busy_str]
        for c_idx, val in enumerate(row_data, 1):
            cell = ws_teachers.cell(row=r_idx, column=c_idx, value=val)
            cell.border = thin_border
            if c_idx != 2:
                cell.alignment = Alignment(horizontal='center')

    # 3. SHEET PHAN_CONG
    ws_assignments = wb.create_sheet(title="Phan_Cong")
    headers3 = ["Mã Lớp", "Môn Học", "Mã GV", "Số Tiết/Tuần", "Tiết Tối Đa/Ngày", "Tiết Cố Định (VD: Thứ 2-T1, Thứ 6-T4)", "Chung Toàn Trường (Có/Không)"]
    for i, h in enumerate(headers3, 1):
        c = ws_assignments.cell(row=1, column=i, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal='center')

    for r_idx, a in enumerate(sample_assignments, 2):
        fixed_str = ", ".join(f"{d}-T{p}" for d, p in a.fixed_slots) if a.fixed_slots else ""
        shared_str = "Có" if a.is_shared_activity else "Không"
        row_vals = [a.class_id, a.subject, a.teacher_id, a.periods_per_week, a.max_periods_per_day, fixed_str, shared_str]
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws_assignments.cell(row=r_idx, column=c_idx, value=val)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')

    for ws in [ws_classes, ws_teachers, ws_assignments]:
        for col in ws.columns:
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = 24

    wb.save(file_path)
    print(f"-> Đã tạo file Excel mẫu dữ liệu đầu vào: {file_path}")

def parse_slot_str(slot_str: str) -> List[Tuple[str, int]]:
    """Phân tích chuỗi 'Thứ 2-T1, Thứ 6-T4' thành [('Thứ 2', 1), ('Thứ 6', 4)]"""
    if not slot_str or pd.isna(slot_str):
        return []
    slots = []
    parts = str(slot_str).split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            day_part, period_part = p.split("-")
            day_part = day_part.strip()
            period_part = period_part.strip().replace("T", "").replace("Tiết", "").strip()
            try:
                slots.append((day_part, int(period_part)))
            except ValueError:
                pass
    return slots

def load_data_from_excel(file_path: str) -> Tuple[ScheduleConfig, List[ClassGroup], List[Teacher], List[TeachingAssignment]]:
    """Đọc dữ liệu từ file Excel người dùng cung cấp"""
    config = ScheduleConfig(
        days=['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6'],
        morning_periods=[1, 2, 3, 4],
        afternoon_periods=[5, 6, 7],
        closed_slots={('Thứ 6', 5), ('Thứ 6', 6), ('Thứ 6', 7)}
    )

    df_classes = pd.read_excel(file_path, sheet_name="Lop_Hoc")
    classes = []
    for _, row in df_classes.iterrows():
        classes.append(ClassGroup(
            id=str(row["Mã Lớp"]).strip(),
            name=str(row["Tên Lớp"]).strip(),
            grade=int(row["Khối Học (1-5)"])
        ))

    df_teachers = pd.read_excel(file_path, sheet_name="Giao_Vien")
    teachers = []
    for _, row in df_teachers.iterrows():
        busy_col = [c for c in df_teachers.columns if "Bận" in c or "Nghỉ" in c]
        busy_val = row[busy_col[0]] if busy_col else ""
        busy_slots = set(parse_slot_str(busy_val))
        teachers.append(Teacher(
            id=str(row["Mã GV"]).strip(),
            name=str(row["Tên Giáo Viên"]).strip(),
            unavailable_slots=busy_slots
        ))

    df_assign = pd.read_excel(file_path, sheet_name="Phan_Cong")
    assignments = []
    for idx, row in df_assign.iterrows():
        fixed_col = [c for c in df_assign.columns if "Cố Định" in c]
        fixed_val = row[fixed_col[0]] if fixed_col else ""
        fixed = parse_slot_str(fixed_val)
        
        shared_col = [c for c in df_assign.columns if "Chung" in c]
        shared_val = row[shared_col[0]] if shared_col else "Không"
        shared = str(shared_val).strip().lower() in ("có", "co", "yes", "true", "1")
        
        max_col = [c for c in df_assign.columns if "Tối Đa" in c]
        max_p = int(row[max_col[0]]) if max_col and not pd.isna(row[max_col[0]]) else 2
        
        assignments.append(TeachingAssignment(
            id=f"AS_{idx+1:03d}",
            class_id=str(row["Mã Lớp"]).strip(),
            subject=str(row["Môn Học"]).strip(),
            teacher_id=str(row["Mã GV"]).strip(),
            periods_per_week=int(row["Số Tiết/Tuần"]),
            max_periods_per_day=max_p,
            fixed_slots=fixed,
            is_shared_activity=shared
        ))

    return config, classes, teachers, assignments
