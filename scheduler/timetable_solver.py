import time
import math
from typing import List, Dict, Tuple, Set, Optional
from ortools.sat.python import cp_model

from scheduler.models import (
    ScheduleConfig,
    ClassGroup,
    Teacher,
    TeachingAssignment,
    ScheduleSlot,
    ScheduleResult
)

class TimetableSolver:
    """
    Bộ giải Thời Khóa Biểu Tự Động sử dụng Google OR-Tools CP-SAT.
    Triển khai toàn diện hệ thống Ràng buộc cứng (Hard Constraints) cho Tiểu học:
    - 4 tiết sáng, 3 tiết chiều
    - Chiều Thứ 6 đóng hoàn toàn
    """
    def __init__(
        self,
        config: ScheduleConfig,
        classes: List[ClassGroup],
        teachers: List[Teacher],
        assignments: List[TeachingAssignment]
    ):
        self.config = config
        self.classes = classes
        self.teachers = teachers
        self.assignments = assignments
        
        # Mapping tiện ích
        self.class_map = {c.id: c for c in classes}
        self.teacher_map = {t.id: t for t in teachers}
        self.assignment_map = {a.id: a for a in assignments}
        
    def validate_pre_conditions(self) -> Tuple[bool, List[str]]:
        """
        Kiểm tra tính khả thi cơ bản trước khi đưa vào Solver:
        - Tổng số tiết lớp học không vượt quá tổng số slot tuần thực tế (32 tiết)
        - Tổng số tiết của GV không vượt quá số slot rảnh trong tuần
        - Các tiết cố định không rơi vào ô bị đóng (như chiều Thứ 6)
        """
        errors = []
        total_active_slots = self.config.total_active_slots_per_week
        
        # 1. Kiểm tra tải của từng lớp
        class_loads: Dict[str, int] = {c.id: 0 for c in self.classes}
        for a in self.assignments:
            if a.class_id not in class_loads:
                errors.append(f"Lỗi phân công: Lớp '{a.class_id}' không tồn tại trong danh sách lớp.")
            else:
                class_loads[a.class_id] += a.periods_per_week
                
        for c_id, load in class_loads.items():
            if load > total_active_slots:
                errors.append(
                    f"Lớp {c_id} có tổng {load} tiết/tuần, vượt quá khung thời gian thực tế ({total_active_slots} tiết/tuần)."
                )

        # 2. Kiểm tra tiết cố định có rơi vào ô đóng không
        for a in self.assignments:
            for (f_d, f_p) in a.fixed_slots:
                if (f_d, f_p) in self.config.closed_slots:
                    errors.append(
                        f"Phân công {a.id} ({a.class_id} - {a.subject}) cố định vào {f_d} Tiết {f_p} "
                        f"nhưng ô này là ô toàn trường nghỉ (Closed slot)!"
                    )

        # 3. Kiểm tra tải của từng giáo viên và lịch bận
        teacher_loads: Dict[str, int] = {t.id: 0 for t in self.teachers}
        for a in self.assignments:
            if a.teacher_id not in teacher_loads and not a.is_shared_activity:
                errors.append(f"Lỗi phân công: Giáo viên '{a.teacher_id}' không tồn tại trong danh sách GV.")
            elif not a.is_shared_activity:
                teacher_loads[a.teacher_id] += a.periods_per_week

        for t in self.teachers:
            # Số slot GV có thể dạy = các slot mở của trường trừ đi slot GV bận
            available_slots = 0
            for d in self.config.days:
                for p in self.config.get_active_periods(d):
                    if (d, p) not in t.unavailable_slots:
                        available_slots += 1
                        
            load = teacher_loads.get(t.id, 0)
            if load > available_slots:
                errors.append(
                    f"Giáo viên {t.name} ({t.id}) được phân {load} tiết, nhưng chỉ còn {available_slots} slot rảnh "
                    f"trong các khung giờ trường mở cửa."
                )

        # 4. Kiểm tra max_periods_per_day
        num_days = len(self.config.days)
        for a in self.assignments:
            min_needed_per_day = math.ceil(a.periods_per_week / num_days)
            if a.max_periods_per_day < min_needed_per_day:
                a.max_periods_per_day = min_needed_per_day

        return len(errors) == 0, errors

    def solve(self, time_limit_seconds: float = 30.0) -> ScheduleResult:
        """
        Khởi tạo mô hình CP-SAT, thiết lập biến và các Ràng buộc cứng, sau đó giải.
        """
        # Kiểm tra điều kiện tiên quyết
        is_valid, pre_errors = self.validate_pre_conditions()
        if not is_valid:
            return ScheduleResult(
                status='INFEASIBLE',
                solve_time_seconds=0.0,
                message="Kiểm tra tiền khả thi thất bại:\n- " + "\n- ".join(pre_errors)
            )

        model = cp_model.CpModel()
        
        # Biến quyết định: x[a_id, d, p] = 1 nếu phân công a được xếp vào ngày d, tiết p
        x = {}
        for a in self.assignments:
            for d in self.config.days:
                for p in self.config.all_periods:
                    x[(a.id, d, p)] = model.NewBoolVar(f"x_{a.id}_{d}_{p}")

        # =========================================================================
        # HỆ THỐNG RÀNG BUỘC CỨNG (HARD CONSTRAINTS)
        # =========================================================================

        # H0. KHÓA CÁC TIẾT NGHỈ TOÀN TRƯỜNG (Closed Slots - Chiều Thứ 6)
        # Toàn bộ các lớp và môn học không được xếp vào các tiết này
        for (d, p) in self.config.closed_slots:
            for a in self.assignments:
                model.Add(x[(a.id, d, p)] == 0)

        # H1. ĐỦ SỐ TIẾT QUY ĐỊNH (Curriculum Demand)
        # Mỗi phân công phải được xếp chính xác số tiết quy định trong tuần
        for a in self.assignments:
            model.Add(
                sum(x[(a.id, d, p)] for d in self.config.days for p in self.config.get_active_periods(d)) == a.periods_per_week
            )

        # H2. CHỐNG TRÙNG TIẾT LỚP HỌC (No Class Conflict)
        # Tại một thời điểm (ngày d, tiết p), một lớp chỉ học tối đa 1 môn
        for c in self.classes:
            class_assignments = [a for a in self.assignments if a.class_id == c.id]
            for d in self.config.days:
                for p in self.config.get_active_periods(d):
                    model.Add(
                        sum(x[(a.id, d, p)] for a in class_assignments) <= 1
                    )

        # H3. CHỐNG TRÙNG TIẾT GIÁO VIÊN (No Teacher Conflict)
        # Tại một thời điểm (ngày d, tiết p), một giáo viên chỉ dạy tối đa 1 lớp
        # (Ngoại trừ các tiết hoạt động chung toàn trường như Chào cờ được đánh dấu is_shared_activity=True)
        for t in self.teachers:
            teacher_assignments = [
                a for a in self.assignments 
                if a.teacher_id == t.id and not a.is_shared_activity
            ]
            for d in self.config.days:
                for p in self.config.get_active_periods(d):
                    model.Add(
                        sum(x[(a.id, d, p)] for a in teacher_assignments) <= 1
                    )

        # H4. LỊCH BẬN / NGÀY NGHỈ CỦA GIÁO VIÊN (Teacher Availability)
        # Nếu giáo viên đăng ký nghỉ tại (d, p), không được phân công dạy vào ô đó
        for t in self.teachers:
            if t.unavailable_slots:
                t_assignments = [a for a in self.assignments if a.teacher_id == t.id]
                for (d, p) in t.unavailable_slots:
                    if d in self.config.days and p in self.config.all_periods:
                        for a in t_assignments:
                            model.Add(x[(a.id, d, p)] == 0)

        # H5. CỐ ĐỊNH TIẾT HỌC ĐẶC BIỆT (Fixed Slots Constraint)
        # Ví dụ: Tiết Chào cờ (Thứ 2, Tiết 1), Sinh hoạt lớp (Thứ 6, Tiết 4)
        for a in self.assignments:
            for (d, p) in a.fixed_slots:
                if d in self.config.days and p in self.config.all_periods:
                    model.Add(x[(a.id, d, p)] == 1)

        # H6. GIỚI HẠN SỐ TIẾT TỐI ĐA CỦA MỘN TRONG 1 NGÀY (Max Periods Per Day Per Subject)
        # Nhóm theo (class_id, subject) để tránh việc học dồn quá số tiết của một môn trong ngày
        # ngay cả khi môn đó được chia cho nhiều giáo viên dạy
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
            max_limit = max(max(a.max_periods_per_day for a in asg_list), min_needed)

            for d in self.config.days:
                active_p_for_day = self.config.get_active_periods(d)
                model.Add(
                    sum(x[(a.id, d, p)] for a in asg_list for p in active_p_for_day) <= max_limit
                )
        
        # H7 (SOFT). Khuyến khích GV không quá 7 buổi/tuần, cho phép vượt nếu cần thiết
        teacher_max_sessions_per_week = getattr(self.config, "teacher_max_sessions_per_week", 7)
        overflow_penalties = []

        for t in self.teachers:
            t_assignments = [
                a for a in self.assignments
                if a.teacher_id == t.id and not a.is_shared_activity
            ]
            if not t_assignments:
                continue

            session_vars = []
            for d in self.config.days:
                active_periods = self.config.get_active_periods(d)
                morning_p = [p for p in active_periods if p in self.config.morning_periods]
                afternoon_p = [p for p in active_periods if p not in self.config.morning_periods]

                for session_periods in (morning_p, afternoon_p):
                    if not session_periods:
                        continue
                    y = model.NewBoolVar(f"buoi_{t.id}_{d}_{session_periods[0]}")
                    related_x = [x[(a.id, d, p)] for a in t_assignments for p in session_periods]
                    for xv in related_x:
                        model.Add(xv <= y)
                    model.Add(sum(related_x) >= y)
                    session_vars.append(y)

            total_sessions = sum(session_vars)
            overflow = model.NewIntVar(0, len(session_vars), f"overflow_{t.id}")
            model.Add(overflow >= total_sessions - teacher_max_sessions_per_week)
            overflow_penalties.append(overflow)

        # Thêm vào mục tiêu: giảm thiểu tổng số buổi vượt ngưỡng 7 của toàn trường
        if overflow_penalties:
            model.Minimize(sum(overflow_penalties))

        # =========================================================================
        # CHẠY BỘ GIẢI (SOLVER)
        # =========================================================================
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        
        start_time = time.time()
        status = solver.Solve(model)
        solve_time = time.time() - start_time

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            result_slots = []
            
            for d in self.config.days:
                for p in self.config.get_active_periods(d):
                    session_str = "Sáng" if p in self.config.morning_periods else "Chiều"
                    for a in self.assignments:
                        if solver.Value(x[(a.id, d, p)]) == 1:
                            t_name = self.teacher_map[a.teacher_id].name if a.teacher_id in self.teacher_map else a.teacher_id
                            result_slots.append(
                                ScheduleSlot(
                                    day=d,
                                    period=p,
                                    session=session_str,
                                    class_id=a.class_id,
                                    subject=a.subject,
                                    teacher_id=a.teacher_id,
                                    teacher_name=t_name
                                )
                            )
                            
            return ScheduleResult(
                status=status_str,
                solve_time_seconds=solve_time,
                slots=result_slots,
                message=f"Xếp lịch thành công với trạng thái {status_str} trong {solve_time:.2f}s."
            )
        else:
            return ScheduleResult(
                status='INFEASIBLE',
                solve_time_seconds=solve_time,
                message="Không tìm thấy nghiệm thỏa mãn toàn bộ các ràng buộc cứng (INFEASIBLE). "
                        "Vui lòng kiểm tra lại sự xung đột giữa các tiết cố định, lịch bận của giáo viên hoặc định mức số tiết."
            )
