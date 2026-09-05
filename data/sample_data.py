from typing import List, Tuple
from scheduler.models import (
    ScheduleConfig,
    ClassGroup,
    Teacher,
    TeachingAssignment
)

def get_sample_school_data() -> Tuple[ScheduleConfig, List[ClassGroup], List[Teacher], List[TeachingAssignment]]:
    """
    Khởi tạo bộ dữ liệu mẫu chuẩn cho 5 cấp học (Khối 1 đến Khối 5) gồm 9 lớp học:
    - Khối 1: Lớp 1A, 1B
    - Khối 2: Lớp 2A, 2B
    - Khối 3: Lớp 3A, 3B
    - Khối 4: Lớp 4A, 4B
    - Khối 5: Lớp 5A
    Khung giờ học Tiểu học 2 buổi/ngày:
    - Sáng: 4 tiết (1, 2, 3, 4)
    - Chiều: 3 tiết (5, 6, 7)
    - Chiều Thứ 6 nghỉ (Tiết 5, 6, 7 đóng)
    -> Tổng cộng đúng 32 slot học/lớp/tuần.
    """
    config = ScheduleConfig(
        days=['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6'],
        morning_periods=[1, 2, 3, 4],
        afternoon_periods=[5, 6, 7],
        closed_slots={('Thứ 6', 5), ('Thứ 6', 6), ('Thứ 6', 7)}
    )

    # 1. DANH SÁCH 9 LỚP HỌC (5 CẤP HỌC)
    classes = [
        ClassGroup(id='1A', name='Lớp 1A', grade=1),
        ClassGroup(id='1B', name='Lớp 1B', grade=1),
        ClassGroup(id='2A', name='Lớp 2A', grade=2),
        ClassGroup(id='2B', name='Lớp 2B', grade=2),
        ClassGroup(id='3A', name='Lớp 3A', grade=3),
        ClassGroup(id='3B', name='Lớp 3B', grade=3),
        ClassGroup(id='4A', name='Lớp 4A', grade=4),
        ClassGroup(id='4B', name='Lớp 4B', grade=4),
        ClassGroup(id='5A', name='Lớp 5A', grade=5),
    ]

    # 2. DANH SÁCH GIÁO VIÊN VÀ LỊCH NGHỈ ĐĂNG KÝ
    teachers = [
        # Giáo viên chủ nhiệm & cơ bản theo lớp
        Teacher(id='GV_1A', name='Cô Hoa (GVCN 1A)'),
        Teacher(id='GV_1B', name='Cô Thảo (GVCN 1B)'),
        Teacher(id='GV_2A', name='Thầy Hùng (GVCN 2A)'),
        Teacher(id='GV_2B', name='Cô Lan (GVCN 2B)', unavailable_slots={('Thứ 5', 3), ('Thứ 5', 4)}),
        Teacher(id='GV_3A', name='Cô Mai (GVCN 3A)'),
        Teacher(id='GV_3B', name='Thầy Minh (GVCN 3B)'),
        Teacher(id='GV_4A', name='Cô Hà (GVCN 4A)'),
        Teacher(id='GV_4B', name='Thầy Tuấn (GVCN 4B)', unavailable_slots={('Thứ 3', 1), ('Thứ 3', 2)}),
        Teacher(id='GV_5A', name='Cô Hương (GVCN 5A)'),

        # Giáo viên bộ môn chuyên trách
        Teacher(id='GV_ANH_1', name='Cô Phương (Anh Khối 1-3)', unavailable_slots={('Thứ 4', 1), ('Thứ 4', 2)}),
        Teacher(id='GV_ANH_2', name='Cô Trang (Anh Khối 4-5)'),
        Teacher(id='GV_TD', name='Thầy Dũng (Thể dục)', unavailable_slots={('Thứ 2', 3), ('Thứ 2', 4)}),
        Teacher(id='GV_NHAC', name='Cô Yến (Âm nhạc)'),
        Teacher(id='GV_HOA', name='Thầy Khoa (Mỹ thuật)'),
        Teacher(id='GV_TIN', name='Thầy Quang (Tin học)'),
        Teacher(id='GV_KNS', name='Cô Thủy (Kỹ năng sống)'),
        
        # Tiết chung toàn trường
        Teacher(id='GV_CHUNG', name='BGH (Toàn trường)')
    ]

    # 3. DANH SÁCH PHÂN CÔNG GIẢNG DẠY (TEACHING ASSIGNMENTS)
    # Tổng định mức: 32 tiết/lớp/tuần
    assignments = []
    aid = 1

    for c in classes:
        cid = c.id
        gid = c.grade
        gv_cn = f"GV_{cid}"
        gv_anh = "GV_ANH_1" if gid <= 3 else "GV_ANH_2"

        # --- A. CÁC TIẾT CỐ ĐỊNH (HARD CONSTRAINTS) ---
        # 1. Chào cờ (Thứ 2, Tiết 1) - chung toàn trường
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Chào cờ",
                teacher_id="GV_CHUNG",
                periods_per_week=1,
                max_periods_per_day=1,
                fixed_slots=[('Thứ 2', 1)],
                is_shared_activity=True
            )
        )
        aid += 1

        # 2. Sinh hoạt lớp: Thứ 6 Tiết 4 (tiết cuối cùng của tuần vì chiều T6 nghỉ)
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Sinh hoạt lớp",
                teacher_id=gv_cn,
                periods_per_week=1,
                max_periods_per_day=1,
                fixed_slots=[('Thứ 6', 4)]
            )
        )
        aid += 1

        # --- B. CÁC MÔN CƠ BẢN DO GVCN DẠY ---
        # 3. Toán: 5 tiết/tuần (1 tiết/ngày)
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Toán",
                teacher_id=gv_cn,
                periods_per_week=5,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 4. Tiếng Việt: 8 tiết/tuần (tối đa 2 tiết/ngày)
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Tiếng Việt",
                teacher_id=gv_cn,
                periods_per_week=8,
                max_periods_per_day=2
            )
        )
        aid += 1

        # 5. Tự nhiên & Xã hội (K1-3) / Khoa học (K4-5): 3 tiết/tuần
        sub_sci = "Tự nhiên & Xã hội" if gid <= 3 else "Khoa học"
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject=sub_sci,
                teacher_id=gv_cn,
                periods_per_week=3,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 6. Đạo đức (K1-3) / Lịch sử & Địa lý (K4-5): 2 tiết/tuần
        sub_soc = "Đạo đức" if gid <= 3 else "Lịch sử & Địa lý"
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject=sub_soc,
                teacher_id=gv_cn,
                periods_per_week=2,
                max_periods_per_day=1
            )
        )
        aid += 1

        # --- C. CÁC MÔN CHUYÊN TRÁCH DO BỘ MÔN DẠY ---
        # 7. Tiếng Anh: 4 tiết/tuần (1 tiết/ngày)
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Tiếng Anh",
                teacher_id=gv_anh,
                periods_per_week=4,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 8. Thể dục (GDTC): 2 tiết/tuần
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Thể dục",
                teacher_id="GV_TD",
                periods_per_week=2,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 9. Âm nhạc: 1 tiết/tuần
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Âm nhạc",
                teacher_id="GV_NHAC",
                periods_per_week=1,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 10. Mỹ thuật: 1 tiết/tuần
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Mỹ thuật",
                teacher_id="GV_HOA",
                periods_per_week=1,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 11. Tin học: 2 tiết/tuần
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Tin học",
                teacher_id="GV_TIN",
                periods_per_week=2,
                max_periods_per_day=1
            )
        )
        aid += 1

        # 12. Kỹ năng sống / Trải nghiệm: 2 tiết/tuần
        assignments.append(
            TeachingAssignment(
                id=f"AS_{aid:03d}",
                class_id=cid,
                subject="Kỹ năng sống",
                teacher_id="GV_KNS",
                periods_per_week=2,
                max_periods_per_day=1
            )
        )
        aid += 1
        # Tổng cộng: 1 + 1 + 5 + 8 + 3 + 2 + 4 + 2 + 1 + 1 + 2 + 2 = 32 tiết/tuần!
        # Đúng 100% số slot học thực tế của trường (4 ngày x 7 tiết + 1 ngày x 4 tiết = 32 tiết).

    return config, classes, teachers, assignments
