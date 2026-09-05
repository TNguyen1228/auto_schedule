from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set

@dataclass
class ScheduleConfig:
    """
    Cấu hình khung thời gian học Tiểu học:
    - Buổi sáng: 4 tiết (Tiết 1, 2, 3, 4)
    - Buổi chiều: 3 tiết (Tiết 5, 6, 7)
    - Nghỉ chiều Thứ 6 (Tiết 5, 6, 7 Thứ 6 đóng hoàn toàn)
    """
    days: List[str] = field(default_factory=lambda: ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6'])
    morning_periods: List[int] = field(default_factory=lambda: [1, 2, 3, 4])
    afternoon_periods: List[int] = field(default_factory=lambda: [5, 6, 7])
    # Các tiết toàn trường nghỉ cố định (ví dụ chiều Thứ 6: Tiết 5, 6, 7)
    closed_slots: Set[Tuple[str, int]] = field(default_factory=lambda: {
        ('Thứ 6', 5), ('Thứ 6', 6), ('Thứ 6', 7)
    })

    @property
    def all_periods(self) -> List[int]:
        return self.morning_periods + self.afternoon_periods

    def get_active_periods(self, day: str) -> List[int]:
        """Lấy danh sách các tiết có học của ngày d"""
        return [p for p in self.all_periods if (day, p) not in self.closed_slots]

    @property
    def total_active_slots_per_week(self) -> int:
        count = 0
        for d in self.days:
            count += len(self.get_active_periods(d))
        return count

@dataclass
class ClassGroup:
    """Lớp học"""
    id: str         # Ví dụ: '1A', '2B', '5A'
    name: str       # Ví dụ: 'Lớp 1A'
    grade: int      # Khối/cấp học: 1 đến 5

@dataclass
class Teacher:
    """Giáo viên"""
    id: str         # Mã GV hoặc tên: 'GV_Toan_1', 'Cô Lan'
    name: str       # Tên hiển thị
    unavailable_slots: Set[Tuple[str, int]] = field(default_factory=set)  # Tập hợp các (ngày, tiết) GV bận

@dataclass
class TeachingAssignment:
    """Phân công giảng dạy: Lớp nào, Môn nào, GV nào dạy, Bao nhiêu tiết/tuần"""
    id: str                             # Mã định danh phân công
    class_id: str                       # Mã lớp
    subject: str                        # Tên môn học
    teacher_id: str                     # Mã giáo viên phụ trách
    periods_per_week: int               # Số tiết trong 1 tuần
    max_periods_per_day: int = 2        # Số tiết tối đa của môn trong 1 ngày (tránh dồn tiết)
    fixed_slots: List[Tuple[str, int]] = field(default_factory=list) # Các tiết cố định nếu có (ví dụ [('Thứ 2', 1)])
    is_shared_activity: bool = False    # True nếu là tiết hoạt động chung toàn trường (như Chào cờ)

@dataclass
class ScheduleSlot:
    """Một ô thời khóa biểu được xếp"""
    day: str
    period: int
    session: str                        # 'Sáng' hoặc 'Chiều'
    class_id: str
    subject: str
    teacher_id: str
    teacher_name: str

@dataclass
class ScheduleResult:
    """Kết quả xếp thời khóa biểu"""
    status: str                         # 'OPTIMAL', 'FEASIBLE', 'INFEASIBLE'
    solve_time_seconds: float
    slots: List[ScheduleSlot] = field(default_factory=list)
    message: str = ""
