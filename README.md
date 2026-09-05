# Auto Schedule

A Python project that automatically generates school timetables respecting hard constraints such as teacher availability, classroom limits, and custom daily session configurations (e.g., 4 morning periods, 3 afternoon periods, with Friday afternoon closed).

## Project Structure
```
auto_schedule/
├─ data/                # Sample data and Excel I/O helpers
├─ scheduler/           # Core models, solver, validator, exporter
├─ main.py              # Entry point script
├─ requirements.txt     # Python dependencies
├─ README.md            # This file
└─ .github/workflows/ci.yml  # GitHub Actions CI workflow
```

## Quick Start
1. **Create a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the scheduler**
   ```powershell
   python main.py
   ```
   This will generate `Thoi_Khoa_Bieu_Truong_9_Lop.xlsx` based on the input template `Input_Mau_TKB.xlsx`.

## Input Excel Template
The project expects an Excel file `Input_Mau_TKB.xlsx` with three sheets:
- **Lop_Hoc** – class information.
- **Giao_Vien** – teacher information.
- **Phan_Cong** – assignment of teachers to subjects and classes.
The template can be generated automatically by running `python main.py` the first time.

## Schedule Model
- **Days**: Monday‑Friday.
- **Morning periods**: 1‑4.
- **Afternoon periods**: 5‑7.
- **Closed slots**: All afternoon periods on Friday (periods 5‑7).
- Fixed slots: "Chào cờ" on Monday period 1, "Sinh hoạt lớp" on Friday period 4.

## CI / Tests
A GitHub Actions workflow runs the script on each push/PR to ensure the timetable can be generated without errors.

## License
MIT License (see LICENSE file).

