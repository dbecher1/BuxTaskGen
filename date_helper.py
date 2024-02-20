import datetime
# Turns out I just thought python's date library was immutable. Oops!

WEEKDAY_ENUM = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class DateHelper:
    # Calculates the last monday and constructs a nifty little helper
    def __init__(self) -> None:
        self.today = datetime.date.today()
        # If not monday:
        if self.today.weekday() != 0:
            self.today = self.today - datetime.timedelta(days=self.today.weekday())

    # Returns a string representation of the month/date/year (e.g. 2_12_24)
    # Does NOT increment the offset/date
    def get_date(self) -> str:
        return self.today.strftime('%m_%d_%y')

    # Returns a (pretty) string representation of the weekday/month/date (e.g. Monday, 2/12)
    # It then increments its offset to be used for the next call
    def get_date_pretty_and_incr(self) -> str:
        out = '{}, {}/{}'.format(
            WEEKDAY_ENUM[self.today.weekday()],
            self.today.month % 10 if self.today.month < 10 else self.today.month,
            self.today.day)
        self.today = self.today + datetime.timedelta(days=1)
        return out
        
    # returns Monday-Sunday, lowercase
    def get_offset_as_weekday(self) -> int:
        return WEEKDAY_ENUM[self.today.weekday()].lower()
