import re
from datetime import datetime, timedelta
import calendar
import dateparser


class DateParser:
    """
    Deterministic date parser.
    Handles:
    - specific dates
    - full months / years
    - standalone years (e.g. 2025)  ✅ FIXED
    - since <month>
    - last week / yesterday / last N days
    - between <date> and <date>
    """

    def _start(self, dt):
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0)

    def _end(self, dt):
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59)

    def _full_month(self, year, month):
        last_day = calendar.monthrange(year, month)[1]
        return (
            self._start(datetime(year, month, 1)),
            self._end(datetime(year, month, last_day)),
        )

    def parse(self, query: str):
        if not query:
            return None, None

        q = query.lower()
        now = datetime.now()

        # --------------------------------------------------
        # BETWEEN <date> AND <date>
        # --------------------------------------------------
        m = re.search(r"between\s+(.+?)\s+and\s+(.+)", q)
        if m:
            d1 = dateparser.parse(m.group(1))
            d2 = dateparser.parse(m.group(2))
            if d1 and d2:
                return self._start(d1), self._end(d2)

        # --------------------------------------------------
        # YESTERDAY
        # --------------------------------------------------
        if "yesterday" in q:
            d = now - timedelta(days=1)
            return self._start(d), self._end(d)

        # --------------------------------------------------
        # LAST WEEK (Mon–Sun)
        # --------------------------------------------------
        if "last week" in q:
            start = now - timedelta(days=now.weekday() + 7)
            end = start + timedelta(days=6)
            return self._start(start), self._end(end)

        # --------------------------------------------------
        # LAST N DAYS
        # --------------------------------------------------
        m = re.search(r"last\s+(\d+)\s+days", q)
        if m:
            days = int(m.group(1))
            start = now - timedelta(days=days)
            return self._start(start), self._end(now)

        # --------------------------------------------------
        # SINCE <MONTH>
        # --------------------------------------------------
        m = re.search(
            r"since\s+(january|february|march|april|may|june|july|august|september|october|november|december)",
            q
        )
        if m:
            month = datetime.strptime(m.group(1), "%B").month
            start = datetime(now.year, month, 1)
            return self._start(start), self._end(now)

        # --------------------------------------------------
        # SPECIFIC DATE: "on September 2, 2025"
        # --------------------------------------------------
        m = re.search(r"on\s+([a-z]+)\s+(\d{1,2}),?\s*(\d{4})", q)
        if m:
            dt = datetime.strptime(" ".join(m.groups()), "%B %d %Y")
            return self._start(dt), self._end(dt)

        # --------------------------------------------------
        # LAST MONTH
        # --------------------------------------------------
        if "last month" in q:
            y, mth = now.year, now.month - 1
            if mth == 0:
                y -= 1
                mth = 12
            return self._full_month(y, mth)

        # --------------------------------------------------
        # THIS MONTH
        # --------------------------------------------------
        if "this month" in q:
            return self._full_month(now.year, now.month)

        # --------------------------------------------------
        # THIS YEAR / LAST YEAR
        # --------------------------------------------------
        if "this year" in q:
            return (
                self._start(datetime(now.year, 1, 1)),
                self._end(datetime(now.year, 12, 31)),
            )

        if "last year" in q:
            y = now.year - 1
            return (
                self._start(datetime(y, 1, 1)),
                self._end(datetime(y, 12, 31)),
            )

        # --------------------------------------------------
        # IN <MONTH>
        # --------------------------------------------------
        m = re.search(
            r"in\s+(january|february|march|april|may|june|july|august|september|october|november|december)",
            q
        )
        if m:
            month = datetime.strptime(m.group(1), "%B").month
            return self._full_month(now.year, month)

        # --------------------------------------------------
        # IN <YEAR>  ✅ FINAL FIX
        # --------------------------------------------------
        m = re.search(r"\b(19|20)\d{2}\b", q)
        if m:
            year = int(m.group())
            return (
                self._start(datetime(year, 1, 1)),
                self._end(datetime(year, 12, 31)),
            )

        # --------------------------------------------------
        # FALLBACK (single date)
        # --------------------------------------------------
        parsed = dateparser.parse(q)
        if parsed:
            return self._start(parsed), self._end(parsed)

        return None, None
