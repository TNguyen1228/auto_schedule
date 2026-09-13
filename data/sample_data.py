from typing import List, Tuple
from scheduler.models import (
    ScheduleConfig,
    ClassGroup,
    Teacher,
    TeachingAssignment
)

def get_sample_school_data() -> Tuple[ScheduleConfig, List[ClassGroup], List[Teacher], List[TeachingAssignment]]:
    """
    Khởi tạo bộ dữ liệu mẫu chuẩn thực tế cho 5 cấp học (Khối 1 đến Khối 5) gồm 9 lớp học:
    - Khối 1: Lớp 1A, 1B
    - Khối 2: Lớp 2A, 2B
    - Khối 3: Lớp 3A
    - Khối 4: Lớp 4A, 4B
    - Khối 5: Lớp 5A, 5B
    Khung giờ học Tiểu học 2 buổi/ngày:
    - Sáng: 4 tiết (1, 2, 3, 4)
    - Chiều: 3 tiết (5, 6, 7)
    - Chiều Thứ 6 nghỉ (Tiết 5, 6, 7 đóng)
    -> Tổng cộng đúng 32 slot học/lớp/tuần (134 phân công).
    """
    from data.excel_io import get_default_source_tables, parse_slot_str
    from data.assignment_generator import generate_phan_cong_df, generate_assignments_from_df
    import pandas as pd

    config = ScheduleConfig(
        days=['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6'],
        morning_periods=[1, 2, 3, 4],
        afternoon_periods=[5, 6, 7],
        closed_slots={('Thứ 6', 5), ('Thứ 6', 6), ('Thứ 6', 7)}
    )

    df_ctk, df_lop, df_gvbm, df_gv = get_default_source_tables()

    # 1. Danh sách lớp
    classes = []
    for _, row in df_lop.iterrows():
        classes.append(ClassGroup(
            id=str(row["Mã Lớp"]).strip(),
            name=str(row["Tên Lớp"]).strip(),
            grade=int(row["Khối"]),
            homeroom_teacher_id=str(row["GV Chủ Nhiệm"]).strip()
        ))

    # 2. Danh sách giáo viên
    teachers = []
    for _, row in df_gv.iterrows():
        busy_val = row.get("Tiết Bận Đăng Ký (VD: Thứ 5-T3, Thứ 5-T4)", "")
        busy_slots = set(parse_slot_str(busy_val))
        teachers.append(Teacher(
            id=str(row["Mã GV"]).strip(),
            name=str(row["Tên Giáo Viên"]).strip(),
            unavailable_slots=busy_slots
        ))

    # 3. Phân công giảng dạy tự động sinh từ 3 bảng nguồn A, B, C
    df_pc = generate_phan_cong_df(df_ctk, df_lop, df_gvbm)
    assignments = generate_assignments_from_df(df_pc)

    return config, classes, teachers, assignments
