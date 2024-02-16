from datetime import datetime
# Python's build in datetime library's dates are immutable
# So using that to just programatically pull the date and then make this helper object

WEEKDAY_ENUM = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class DateHelper:
    # Given a month/day that is always given to be the first monday of a week, constructs a nifty little helper
    def __init__(self) -> None:
        curr = datetime.now()
        self.year = curr.year
        self.month = curr.month
        self.day = curr.day
        self.offset = 0

    # Returns a string representation of the month/date/year (e.g. 2_12_24)
    # Does NOT increment the offset/date
    def get_date(self) -> str:
        return "{m}_{d}_{y}".format(m=self.month, d=self.day, y=(self.year % 100))

    # Returns a (pretty) string representation of the weekday/month/date (e.g. Monday, 2/12)
    # It then increments its offset to be used for the next call
    def get_date_pretty_and_incr(self) -> str:
        out = WEEKDAY_ENUM[self.offset % 7] + ', '
        out += str(self.month) + '/' + str(self.day)
        self.increment_date()
        return out
        
    # returns Monday-Sunday, lowercase
    def get_offset_as_weekday(self) -> int:
        return WEEKDAY_ENUM[self.offset % 7].lower()

    def increment_date(self) -> None:
        self.offset += 1
        # Feb
        if self.month == 2:
            num_days = 28
            if self.year % 4 == 0:
                num_days += 1
        # April, June, Sept, Nov
        elif (self.month) == 4 or (self.month) == 6 or (self.month) == 9 or (self.month == 11):
            num_days = 30
        else:
            num_days = 31
        # Wraparound
        self.day = (self.day + 1) % (num_days + 1)
        if self.day == 0:
            self.day += 1
            self.month = (self.month + 1) % 13
