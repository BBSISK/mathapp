"""
AgentMath.app - Irish School Calendar Helper
=============================================

This module provides utilities for determining Irish school days,
excluding weekends, bank holidays, and school holiday periods.

Used by the streak system to only count school days.
"""

from datetime import date, timedelta
from typing import List, Tuple

# Irish Bank Holidays (fixed dates)
# These are approximations - some move slightly year to year
def get_irish_bank_holidays(year: int) -> List[date]:
    """Get Irish bank holidays for a given year"""
    holidays = [
        date(year, 1, 1),    # New Year's Day
        date(year, 3, 17),   # St. Patrick's Day
        date(year, 12, 25),  # Christmas Day
        date(year, 12, 26),  # St. Stephen's Day
    ]
    
    # Easter-based holidays (approximate - Easter moves each year)
    # For simplicity, we'll calculate Easter using an algorithm
    easter = calculate_easter(year)
    holidays.append(easter - timedelta(days=2))  # Good Friday
    holidays.append(easter + timedelta(days=1))  # Easter Monday
    
    # First Monday of May
    holidays.append(get_first_monday(year, 5))
    
    # First Monday of June
    holidays.append(get_first_monday(year, 6))
    
    # First Monday of August
    holidays.append(get_first_monday(year, 8))
    
    # Last Monday of October
    holidays.append(get_last_monday(year, 10))
    
    return holidays


def calculate_easter(year: int) -> date:
    """Calculate Easter Sunday using the Anonymous Gregorian algorithm"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_first_monday(year: int, month: int) -> date:
    """Get the first Monday of a given month"""
    d = date(year, month, 1)
    while d.weekday() != 0:  # 0 = Monday
        d += timedelta(days=1)
    return d


def get_last_monday(year: int, month: int) -> date:
    """Get the last Monday of a given month"""
    # Start from the last day of the month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    
    while last_day.weekday() != 0:
        last_day -= timedelta(days=1)
    return last_day


def get_irish_school_holidays(year: int) -> List[Tuple[date, date]]:
    """
    Get Irish school holiday periods for a given academic year.
    Year parameter is the START of the academic year (e.g., 2024 for 2024-2025).
    
    Returns list of (start_date, end_date) tuples.
    
    Based on typical Irish post-primary school calendars.
    Individual schools may vary slightly.
    """
    
    # Specific holiday dates for known academic years
    SCHOOL_HOLIDAYS = {
        # 2024-2025 Academic Year
        2024: [
            (date(2024, 10, 28), date(2024, 11, 1)),    # October Mid-term
            (date(2024, 12, 21), date(2025, 1, 6)),    # Christmas Holidays
            (date(2025, 2, 17), date(2025, 2, 21)),    # February Mid-term
            (date(2025, 4, 14), date(2025, 4, 25)),    # Easter Holidays
            (date(2025, 6, 27), date(2025, 8, 31)),    # Summer Holidays
        ],
        # 2025-2026 Academic Year
        2025: [
            (date(2025, 10, 27), date(2025, 10, 31)),  # October Mid-term
            (date(2025, 12, 22), date(2026, 1, 5)),    # Christmas Holidays
            (date(2026, 2, 16), date(2026, 2, 20)),    # February Mid-term
            (date(2026, 3, 30), date(2026, 4, 10)),    # Easter Holidays (Easter: Apr 5)
            (date(2026, 6, 26), date(2026, 8, 31)),    # Summer Holidays
        ],
        # 2026-2027 Academic Year
        2026: [
            (date(2026, 10, 26), date(2026, 10, 30)),  # October Mid-term
            (date(2026, 12, 21), date(2027, 1, 4)),    # Christmas Holidays
            (date(2027, 2, 15), date(2027, 2, 19)),    # February Mid-term
            (date(2027, 3, 22), date(2027, 4, 2)),     # Easter Holidays (Easter: Mar 28)
            (date(2027, 6, 25), date(2027, 8, 31)),    # Summer Holidays
        ],
        # 2027-2028 Academic Year
        2027: [
            (date(2027, 10, 25), date(2027, 10, 29)),  # October Mid-term
            (date(2027, 12, 20), date(2028, 1, 3)),    # Christmas Holidays
            (date(2028, 2, 14), date(2028, 2, 18)),    # February Mid-term
            (date(2028, 4, 10), date(2028, 4, 21)),    # Easter Holidays (Easter: Apr 16)
            (date(2028, 6, 23), date(2028, 8, 31)),    # Summer Holidays
        ],
    }
    
    if year in SCHOOL_HOLIDAYS:
        return SCHOOL_HOLIDAYS[year]
    
    # Fallback for years not explicitly defined - use approximate dates
    holidays = []
    
    # October Mid-term (last week of October, Mon-Fri)
    oct_bank_holiday = get_last_monday(year, 10)
    holidays.append((oct_bank_holiday, oct_bank_holiday + timedelta(days=4)))
    
    # Christmas Holidays (approx Dec 21 - Jan 5)
    holidays.append((date(year, 12, 21), date(year + 1, 1, 5)))
    
    # February Mid-term (typically 3rd week of Feb)
    feb_start = date(year + 1, 2, 15)
    while feb_start.weekday() != 0:
        feb_start += timedelta(days=1)
    holidays.append((feb_start, feb_start + timedelta(days=4)))
    
    # Easter Holidays (2 weeks around Easter)
    easter = calculate_easter(year + 1)
    easter_start = easter - timedelta(days=7)
    while easter_start.weekday() != 0:
        easter_start -= timedelta(days=1)
    holidays.append((easter_start, easter + timedelta(days=5)))
    
    # Summer Holidays (late June to end of August)
    holidays.append((date(year + 1, 6, 27), date(year + 1, 8, 31)))
    
    return holidays


def is_school_day(check_date: date) -> bool:
    """
    Determine if a given date is a school day in Ireland.
    
    Returns False for:
    - Weekends (Saturday, Sunday)
    - Bank holidays
    - School holiday periods
    
    Returns True for regular school days (Mon-Fri during term time)
    """
    # Check weekend
    if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check bank holidays
    year = check_date.year
    bank_holidays = get_irish_bank_holidays(year)
    if check_date in bank_holidays:
        return False
    
    # Check school holiday periods
    # Need to check current year and previous year's academic calendar
    for academic_year in [year - 1, year]:
        try:
            school_holidays = get_irish_school_holidays(academic_year)
            for start_date, end_date in school_holidays:
                if start_date <= check_date <= end_date:
                    return False
        except:
            pass  # Skip if date calculation fails
    
    return True


def get_previous_school_day(from_date: date) -> date:
    """Get the most recent school day before the given date"""
    check = from_date - timedelta(days=1)
    while not is_school_day(check):
        check -= timedelta(days=1)
        # Safety limit - don't go back more than 100 days
        if (from_date - check).days > 100:
            return from_date - timedelta(days=1)
    return check


def get_next_school_day(from_date: date) -> date:
    """Get the next school day after the given date"""
    check = from_date + timedelta(days=1)
    while not is_school_day(check):
        check += timedelta(days=1)
        # Safety limit - don't go forward more than 100 days
        if (check - from_date).days > 100:
            return from_date + timedelta(days=1)
    return check


def count_school_days_between(start_date: date, end_date: date) -> int:
    """Count the number of school days between two dates (exclusive of end)"""
    count = 0
    current = start_date
    while current < end_date:
        if is_school_day(current):
            count += 1
        current += timedelta(days=1)
    return count


def is_consecutive_school_day(last_activity_date: date, today: date) -> bool:
    """
    Check if today is the consecutive school day after last_activity_date.
    
    Returns True if:
    - last_activity was yesterday (and both are school days)
    - last_activity was Friday and today is Monday (no school days in between)
    - last_activity was before a holiday and today is the first school day back
    """
    if last_activity_date >= today:
        return False  # Same day or future date
    
    # Get the next expected school day after last activity
    expected_next = get_next_school_day(last_activity_date)
    
    # If today is that expected school day, streak continues
    return today == expected_next


def should_reset_streak(last_activity_date: date, today: date) -> bool:
    """
    Determine if a streak should be reset.
    
    Reset if the student missed a school day between last activity and today.
    """
    if last_activity_date is None:
        return False  # No previous activity, starting fresh
    
    if last_activity_date >= today:
        return False  # Same day, no reset
    
    # Count school days between last activity and today
    # If more than 1, they missed at least one school day
    school_days_missed = count_school_days_between(last_activity_date, today)
    
    # They should have been active on the next school day
    # So if school_days_missed > 1, they missed days
    return school_days_missed > 1


# Streak milestone definitions
STREAK_MILESTONES = {
    3: {'name': 'Getting Started', 'points': 10, 'emoji': '🔥'},
    5: {'name': 'Building Momentum', 'points': 25, 'emoji': '⚡'},
    7: {'name': 'One Week Wonder', 'points': 50, 'emoji': '🌟'},
    14: {'name': 'Fortnight Fighter', 'points': 100, 'emoji': '💪'},
    21: {'name': 'Three Week Warrior', 'points': 150, 'emoji': '🏆'},
    30: {'name': 'Monthly Master', 'points': 250, 'emoji': '👑'},
    50: {'name': 'Dedicated Learner', 'points': 500, 'emoji': '🎯'},
    100: {'name': 'Century Champion', 'points': 1000, 'emoji': '💎'},
}


def get_streak_milestone(streak_days: int) -> dict:
    """Check if current streak has hit a milestone"""
    if streak_days in STREAK_MILESTONES:
        return STREAK_MILESTONES[streak_days]
    return None


def get_next_milestone(streak_days: int) -> Tuple[int, dict]:
    """Get the next streak milestone to aim for"""
    for milestone_days in sorted(STREAK_MILESTONES.keys()):
        if milestone_days > streak_days:
            return milestone_days, STREAK_MILESTONES[milestone_days]
    return None, None


# For testing
if __name__ == "__main__":
    from datetime import date
    
    print("=== Irish School Calendar Test ===\n")
    
    today = date.today()
    print(f"Today: {today} ({today.strftime('%A')})")
    print(f"Is school day: {is_school_day(today)}")
    print(f"Previous school day: {get_previous_school_day(today)}")
    print(f"Next school day: {get_next_school_day(today)}")
    
    print(f"\n2025 Bank Holidays:")
    for h in get_irish_bank_holidays(2025):
        print(f"  {h} ({h.strftime('%A')})")
    
    print(f"\n2024-2025 School Holidays:")
    for start, end in get_irish_school_holidays(2024):
        print(f"  {start} to {end}")
    
    print(f"\nStreak Milestones:")
    for days, info in STREAK_MILESTONES.items():
        print(f"  {days} days: {info['emoji']} {info['name']} (+{info['points']} pts)")
