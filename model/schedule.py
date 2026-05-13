# model/schedule.py

from datetime import datetime, timedelta
import re

from .subjects import subjects_for


SCHEDULE_START_HOURS = {
    "MORNING": 6,
    "AFTERNOON": 12,
    "EVENING": 18,
}

SECTION_SCHEDULE_LABELS = {
    "1": "Morning",
    "2": "Afternoon",
    "3": "Evening",
}


def normalize_schedule(value: str) -> str:
    schedule = str(value or "").strip().upper()
    return schedule if schedule in SCHEDULE_START_HOURS else "MORNING"


def section_number(section: str) -> str:
    match = re.search(r"(\d+)\s*$", str(section or ""))
    return match.group(1) if match else ""


def schedule_label_for_section(section: str) -> str:
    number = section_number(section)
    return SECTION_SCHEDULE_LABELS.get(number, "")


def schedule_from_section(section: str) -> str:
    return schedule_label_for_section(section).upper()


def build_subject_time_slots(schedule: str, grade: str, strand: str, assignments: dict) -> list:
    start_hour = SCHEDULE_START_HOURS[normalize_schedule(schedule)]
    start = datetime(2000, 1, 1, start_hour, 0)

    subjects = list(assignments.keys()) if assignments else subjects_for(strand, grade)
    rows = []
    for index, subject in enumerate(subjects):
        slot_start = start + timedelta(hours=index)
        slot_end = slot_start + timedelta(hours=1)
        rows.append({
            "time": f"{slot_start.strftime('%I:%M %p').lstrip('0')} - {slot_end.strftime('%I:%M %p').lstrip('0')}",
            "subject": subject,
            "teacher": assignments.get(subject, "") if assignments else "",
        })
    return rows
