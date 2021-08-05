def get_appropriate_timeunits_from_day(days):
    years, months, weeks = None, None, None
    if days > 7:
        weeks = int(days / 7)
        days = days % 7
        if weeks > 4:
            months = int(weeks / 4)
            weeks = weeks % 4
            if months > 12:
                years = int(months / 12)
                months = months % 12

    if years: return str(years) + " years " + str(months) + " months"
    if months: return str(months) + " months " + str(weeks) + " weeks"
    if weeks: return str(weeks) + " weeks " + str(days) + " days"
    return str(days) + " days"



