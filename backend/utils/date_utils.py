def format_uzbek_date_long(date_obj):
    """
    Sanalarni '2025-yil oktyabr oyining 21-kuni' formatiga o'tkazish.
    """
    months = {
        1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
        5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
        9: "sentyabr", 10: "oktyabr", 11: "noyabr", 12: "dekabr"
    }
    if not date_obj:
        return ""
    
    day = date_obj.day
    month = months.get(date_obj.month, "")
    year = date_obj.year
    
    return f"{year}-yil {month} oyining {day}-kuni"
