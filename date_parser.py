from datetime import date
import calendar


class DateParser:
    """
    Rule-based date parser.
    Assumes latest dataset year if year is not specified.
    """

    def __init__(self, default_year=2024):
        self.default_year = default_year

        self.months = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12
        }

    def parse(self, query: str):
        query_lower = query.lower()

        # Case 1: explicit YYYY-MM
        for token in query_lower.split():
            if len(token) == 7 and token[4] == "-":
                try:
                    year = int(token[:4])
                    month = int(token[5:7])
                    start = date(year, month, 1)
                    end = date(year, month, calendar.monthrange(year, month)[1])
                    return start, end
                except ValueError:
                    pass

        # Case 2: last month (relative to dataset year)
        if "last month" in query_lower:
            month = 2  # February in dataset
            year = self.default_year
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            return start, end

        # Case 3: this month (relative to dataset year)
        if "this month" in query_lower:
            month = 3  # March in dataset
            year = self.default_year
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            return start, end

        # Case 4: month name (assume dataset year)
        for name, month_num in self.months.items():
            if name in query_lower:
                year = self.default_year
                start = date(year, month_num, 1)
                end = date(year, month_num, calendar.monthrange(year, month_num)[1])
                return start, end

        return None, None
