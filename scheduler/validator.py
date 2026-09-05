import math
from typing import List, Dict, Tuple, Set
from scheduler.models import (
    ScheduleConfig,
    ClassGroup,
    Teacher,
    TeachingAssignment,
    ScheduleResult
)

class TimetableValidator:
    """
    Bộ kiểm định độc lập (Validator) kiểm tra xem kết quả TKB có vi phạm bất kỳ Ràng buộc cứng nào không:
    - Không xếp vào tiết nghỉ toàn trường (Chiều Thứ 6)
    - Đúng 100% định mức tiết
    - Không trùng lớp, không trùng GV
    - Đúng tiết cố định (Chào cờ, Sinh hoạt lớp)
    - Tuyệt đối không xếp vào lịch bận của GV
    - Không vượt quá giới hạn số tiết/ngày của môn
    """
    def __init__(
        self,
        config: ScheduleConfig,
        classes: List[ClassGroup],
        teachers: List[Teacher],
        assignments: List[TeachingAssignment],
        result: ScheduleResult
    ):
        self.config = config
        self.classes = classes
        self.teachers = teachers
        self.assignments = assignments
        self.result = result

    def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Thực hiện toàn bộ các bước kiểm tra ràng buộc cứng.
        Trả về: (is_valid, list_of_violations)
        """
        if self.result.status not in ('OPTIMAL', 'FEASIBLE'):
            return False, [f"Kết quả không hợp lệ (Trạng thái: {self.result.status})"]

        violations = []
        slots = self.result.slots

        # 0. Kiểm tra tiết nghỉ toàn trường (Closed Slots - Chiều Thứ 6)
        for s in slots:
            if (s.day, s.period) in self.config.closed_slots:
                violations.append(
                    f"Vi phạm tiết nghỉ toàn trường: Lớp {s.class_id} môn {s.subject} "
                    f"bị xếp vào {s.day} Tiết {s.period} (buổi này toàn trường nghỉ)!"
                )

        # 1. Kiểm tra đủ số tiết theo từng phân công (Curriculum Demand)
        assignment_counts: Dict[Tuple[str, str, str], int] = {}
        for a in self.assignments:
            key = (a.class_id, a.subject, a.teacher_id)
            assignment_counts[key] = 0

        for s in slots:
            key = (s.class_id, s.subject, s.teacher_id)
            if key in assignment_counts:
                assignment_counts[key] += 1
            else:
                violations.append(f"Vi phạm dữ liệu lạ: Ô xếp {s} không nằm trong danh mục phân công giảng dạy.")

        for a in self.assignments:
            key = (a.class_id, a.subject, a.teacher_id)
            actual = assignment_counts.get(key, 0)
            if actual != a.periods_per_week:
                violations.append(
                    f"Vi phạm số tiết môn: Lớp {a.class_id}, Môn {a.subject}, GV {a.teacher_id} "
                    f"yêu cầu {a.periods_per_week} tiết nhưng chỉ được xếp {actual} tiết."
                )

        # 2. Kiểm tra trùng tiết lớp học (Single class conflict)
        class_time_map: Dict[Tuple[str, str, int], List[str]] = {}
        for s in slots:
            key = (s.class_id, s.day, s.period)
            if key not in class_time_map:
                class_time_map[key] = []
            class_time_map[key].append(s.subject)

        for (c_id, day, period), subjects in class_time_map.items():
            if len(subjects) > 1:
                violations.append(
                    f"Vi phạm trùng giờ LỚP: Lớp {c_id} tại {day} Tiết {period} bị xếp {len(subjects)} môn: {', '.join(subjects)}"
                )

        # 3. Kiểm tra trùng tiết giáo viên (Single teacher conflict)
        assignment_shared = {(a.class_id, a.subject, a.teacher_id): a.is_shared_activity for a in self.assignments}

        teacher_time_map: Dict[Tuple[str, str, int], List[str]] = {}
        for s in slots:
            is_shared = assignment_shared.get((s.class_id, s.subject, s.teacher_id), False)
            if is_shared:
                continue # Bỏ qua tiết chung toàn trường
            key = (s.teacher_id, s.day, s.period)
            if key not in teacher_time_map:
                teacher_time_map[key] = []
            teacher_time_map[key].append(f"Lớp {s.class_id} (Môn {s.subject})")

        for (t_id, day, period), teachings in teacher_time_map.items():
            if len(teachings) > 1:
                violations.append(
                    f"Vi phạm trùng giờ GIÁO VIÊN: GV {t_id} tại {day} Tiết {period} bị xếp dạy nhiều lớp cùng lúc: {', '.join(teachings)}"
                )

        # 4. Kiểm tra tiết cố định (Fixed slots)
        for a in self.assignments:
            for (f_day, f_period) in a.fixed_slots:
                matched = any(
                    s.class_id == a.class_id and s.subject == a.subject and s.teacher_id == a.teacher_id
                    and s.day == f_day and s.period == f_period
                    for s in slots
                )
                if not matched:
                    violations.append(
                        f"Vi phạm tiết cố định: Môn {a.subject} của lớp {a.class_id} chưa được xếp đúng vào {f_day} Tiết {f_period}."
                    )

        # 5. Kiểm tra lịch bận / nghỉ của giáo viên (Teacher unavailability)
        teacher_busy_dict = {t.id: t.unavailable_slots for t in self.teachers}
        for s in slots:
            busy_slots = teacher_busy_dict.get(s.teacher_id, set())
            if (s.day, s.period) in busy_slots:
                violations.append(
                    f"Vi phạm lịch nghỉ của GV: GV {s.teacher_name} ({s.teacher_id}) đã đăng ký nghỉ tại {s.day} Tiết {s.period} nhưng vẫn bị xếp dạy lớp {s.class_id}."
                )

        # 6. Kiểm tra giới hạn số tiết tối đa trong 1 ngày của môn
        daily_subject_count: Dict[Tuple[str, str, str], int] = {}
        for s in slots:
            key = (s.class_id, s.subject, s.day)
            daily_subject_count[key] = daily_subject_count.get(key, 0) + 1

        class_subject_map: Dict[Tuple[str, str], List[TeachingAssignment]] = {}
        for a in self.assignments:
            key = (a.class_id, a.subject)
            if key not in class_subject_map:
                class_subject_map[key] = []
            class_subject_map[key].append(a)

        num_days = len(self.config.days)
        for (c_id, subj), asg_list in class_subject_map.items():
            total_subj_periods = sum(a.periods_per_week for a in asg_list)
            min_needed = math.ceil(total_subj_periods / num_days)
            allowed_max = max(max(a.max_periods_per_day for a in asg_list), min_needed)

            for day in self.config.days:
                cnt = daily_subject_count.get((c_id, subj, day), 0)
                if cnt > allowed_max:
                    violations.append(
                        f"Vi phạm số tiết/ngày: Lớp {c_id} môn {subj} tại {day} bị xếp {cnt} tiết "
                        f"(vượt giới hạn tối đa {allowed_max} tiết/ngày)."
                    )

        is_valid = len(violations) == 0
        return is_valid, violations
