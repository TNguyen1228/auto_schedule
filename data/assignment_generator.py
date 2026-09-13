"""
Trình tạo phân công tự động (Assignment Generator) từ 3 bảng nguồn:
1. Bảng A - Chuong_Trinh_Khung: Khung chương trình theo khối
2. Bảng B - Lop_Hoc: Danh sách lớp và GV chủ nhiệm
3. Bảng C - Giao_Vien_Bo_Mon: Bảng ánh xạ GV bộ môn, GV liên khối và ngoại lệ theo lớp
"""

from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

from scheduler.models import TeachingAssignment


def parse_grades(grade_val: Any) -> List[int]:
    """Phân tích giá trị cột Khối (VD: '1', '1,2', '4,5', 'Tất cả') thành list các khối int."""
    if pd.isna(grade_val):
        return []
    s = str(grade_val).strip()
    if s.lower() in ("tất cả", "tat ca", "all", "*"):
        return [1, 2, 3, 4, 5]
    
    grades = []
    for part in s.split(","):
        p = part.strip()
        if p.isdigit():
            grades.append(int(p))
    return grades


def resolve_teacher(
    class_id: str,
    grade: int,
    gv_type: str,
    subject: str,
    df_lop: pd.DataFrame,
    df_gvbm: pd.DataFrame
) -> str:
    """
    Quy tắc giải mã Loại GV thành Mã GV thực tế:
    1. 'CHU_NHIEM': Lấy cột 'GV Chủ Nhiệm' từ Bảng B (Lop_Hoc).
    2. Mã trực tiếp (bắt đầu bằng 'GV_' hoặc 'PHT'): Trả về chính mã đó.
    3. Tra cứu từ Bảng C (Giao_Vien_Bo_Mon):
       - Độ ưu tiên 1: Khớp chính xác Mã Lớp (ngoại lệ riêng của lớp).
       - Độ ưu tiên 2: Khớp Khối của lớp.
       - Độ ưu tiên 3: Khớp 'Tất cả' toàn trường.
    """
    gv_type_str = str(gv_type).strip() if pd.notna(gv_type) else ""
    subject_str = str(subject).strip() if pd.notna(subject) else ""

    # 1. GV Chủ nhiệm
    if gv_type_str.upper() in ("CHU_NHIEM", "GVCN", "CHỦ NHIỆM"):
        col_cn = [c for c in df_lop.columns if "Chủ Nhiệm" in c or "chu_nhiem" in c.lower()]
        if col_cn:
            match_row = df_lop[df_lop["Mã Lớp"].astype(str).str.strip() == str(class_id).strip()]
            if not match_row.empty:
                val = match_row.iloc[0][col_cn[0]]
                if pd.notna(val) and str(val).strip():
                    return str(val).strip()
        return f"GV_{class_id}"

    # 2. Mã GV trực tiếp (VD: GV_CHUNG, GV_12, PHT...)
    # Nếu gv_type là một mã cố định không có tiền tố BO_MON
    if not gv_type_str.upper().startswith("BO_MON"):
        # Nếu là mã cụ thể như GV_CHUNG, GV_12, PHT thì trả về ngay
        if gv_type_str.startswith("GV_") or gv_type_str in ("PHT", "BGH"):
            return gv_type_str

    # 3. Tra cứu Bảng C
    # Token trích xuất sau tiền tố BO_MON: (nếu có)
    token = gv_type_str
    if ":" in gv_type_str:
        token = gv_type_str.split(":", 1)[1].strip()
    elif gv_type_str.upper().startswith("BO_MON"):
        token = gv_type_str[6:].strip()

    col_target = [c for c in df_gvbm.columns if "Khối" in c or "Lớp" in c][0]
    col_type = [c for c in df_gvbm.columns if "Môn" in c or "Loại" in c][0]
    col_gv = [c for c in df_gvbm.columns if "Mã GV" in c or "GV" in c][0]

    # Độ ưu tiên 1: Ngoại lệ cho lớp cụ thể (Mã Lớp)
    for _, r in df_gvbm.iterrows():
        kl = str(r[col_target]).strip()
        ml = str(r[col_type]).strip()
        if (ml.upper() == token.upper() or ml.lower() == subject_str.lower()) and kl == str(class_id).strip():
            return str(r[col_gv]).strip()

    # Độ ưu tiên 2: Khớp Khối học
    for _, r in df_gvbm.iterrows():
        kl = str(r[col_target]).strip()
        ml = str(r[col_type]).strip()
        if ml.upper() == token.upper() or ml.lower() == subject_str.lower():
            grades = parse_grades(kl)
            if grade in grades:
                return str(r[col_gv]).strip()

    # Độ ưu tiên 3: Toàn trường ("Tất cả")
    for _, r in df_gvbm.iterrows():
        kl = str(r[col_target]).strip().lower()
        ml = str(r[col_type]).strip()
        if (ml.upper() == token.upper() or ml.lower() == subject_str.lower()) and kl in ("tất cả", "tat ca", "all", "*"):
            return str(r[col_gv]).strip()

    # Nếu không tìm thấy, trả về token gốc nếu có dạng mã GV
    if gv_type_str.startswith("GV_") or gv_type_str in ("PHT", "BGH"):
        return gv_type_str

    raise ValueError(
        f"Không tìm được giáo viên phù hợp cho Lớp '{class_id}' (Khối {grade}), "
        f"Môn '{subject_str}', Loại GV '{gv_type_str}' trong Bảng C."
    )


def generate_phan_cong_df(
    df_ctk: pd.DataFrame,
    df_lop: pd.DataFrame,
    df_gvbm: pd.DataFrame
) -> pd.DataFrame:
    """
    Sinh DataFrame Phan_Cong gồm 7 cột chuẩn:
    1. Mã Lớp
    2. Môn Học
    3. Mã GV
    4. Số Tiết/Tuần
    5. Tiết Tối Đa/Ngày
    6. Tiết Cố Định (VD: Thứ 2-T1, Thứ 6-T4)
    7. Chung Toàn Trường (Có/Không)
    """
    col_class_id = [c for c in df_lop.columns if "Mã Lớp" in c or "ma_lop" in c.lower()][0]
    col_grade = [c for c in df_lop.columns if "Khối" in c or "grade" in c.lower()][0]

    col_ctk_grade = [c for c in df_ctk.columns if "Khối" in c][0]
    col_ctk_subj = [c for c in df_ctk.columns if "Môn" in c][0]
    col_ctk_st = [c for c in df_ctk.columns if "Số Tiết" in c][0]
    col_ctk_max = [c for c in df_ctk.columns if "Tối Đa" in c][0]
    col_ctk_gvtype = [c for c in df_ctk.columns if "Loại GV" in c or "GV" in c][0]
    col_ctk_fixed = [c for c in df_ctk.columns if "Cố Định" in c][0]
    col_ctk_shared = [c for c in df_ctk.columns if "Chung" in c][0]

    rows = []
    for _, lop_row in df_lop.iterrows():
        c_id = str(lop_row[col_class_id]).strip()
        grade = int(lop_row[col_grade])

        # Lọc các dòng chương trình khung áp dụng cho khối này
        for _, ctk_row in df_ctk.iterrows():
            grades = parse_grades(ctk_row[col_ctk_grade])
            if grade in grades:
                subject = str(ctk_row[col_ctk_subj]).strip()
                gv_type = str(ctk_row[col_ctk_gvtype]).strip()
                st = int(ctk_row[col_ctk_st])
                mx = int(ctk_row[col_ctk_max]) if pd.notna(ctk_row[col_ctk_max]) else 1
                
                fixed_val = ctk_row[col_ctk_fixed]
                fixed_str = str(fixed_val).strip() if pd.notna(fixed_val) and str(fixed_val).strip() != "" else ""

                shared_val = ctk_row[col_ctk_shared]
                shared_str = "Có" if pd.notna(shared_val) and str(shared_val).strip().lower() in ("có", "co", "yes", "true", "1") else "Không"

                real_gv = resolve_teacher(c_id, grade, gv_type, subject, df_lop, df_gvbm)

                rows.append({
                    "Mã Lớp": c_id,
                    "Môn Học": subject,
                    "Mã GV": real_gv,
                    "Số Tiết/Tuần": st,
                    "Tiết Tối Đa/Ngày": mx,
                    "Tiết Cố Định (VD: Thứ 2-T1, Thứ 6-T4)": fixed_str if fixed_str else np.nan,
                    "Chung Toàn Trường (Có/Không)": shared_str
                })

    return pd.DataFrame(rows)


def generate_assignments_from_df(df_pc: pd.DataFrame) -> List[TeachingAssignment]:
    """Chuyển đổi DataFrame Phan_Cong thành List[TeachingAssignment] cho solver."""
    from data.excel_io import parse_slot_str

    assignments = []
    for idx, row in df_pc.iterrows():
        fixed_val = row.get("Tiết Cố Định (VD: Thứ 2-T1, Thứ 6-T4)", "")
        fixed = parse_slot_str(fixed_val)

        shared_val = row.get("Chung Toàn Trường (Có/Không)", "Không")
        shared = str(shared_val).strip().lower() in ("có", "co", "yes", "true", "1")

        max_p = int(row["Tiết Tối Đa/Ngày"]) if pd.notna(row.get("Tiết Tối Đa/Ngày")) else 1

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
    return assignments

