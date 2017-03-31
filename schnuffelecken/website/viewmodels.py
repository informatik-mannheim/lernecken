from datetime import datetime


class WeekViewModel(object):
    """
    Transform week into a row layout that allows for easy table row creation looping
    """

    def __init__(self, week, facility, user):
        self._day_names = ["Montag", "Dienstag",
                           "Mittwoch", "Donnerstag", "Freitag"]
        self.rows = []
        self.headers = [(self._day_names[day.date.weekday()], day.date.strftime(
            "%d.%m.%y"), day.date.date() == datetime.now().date()) for day in week.days]
        self.calendar_week = week.calendar_week
        self._to_view_model(week, facility, user)

    def _to_view_model(self, week, facility, user):

        for hour in range(0, 11):
            blocks = [week.days[day].get_bookings(
                facility, user)[hour] for day in range(0, 5)]
            self.rows.append(Row(hour + 8, blocks))


class Row(object):

    def __init__(self, hour, blocks):
        self.time_start = "{0:02d}:00".format(hour)
        self.time_end = "{0:02d}:00".format(hour + 1)
        self.blocks = blocks


class AllOk(object):

    def __init__(self):
        self.status_code = 200
        self.message = ""
        self.css = ""


class RedAlert(object):

    def __init__(self, message):
        self.status_code = 403
        self.message = message
        self.css = "label-xl label-danger"


class GreenAlert(object):

    def __init__(self, message):
        self.status_code = 200
        self.message = message
        self.css = "label-xl label-success"


class BlockAvailable(object):

    def __init__(self, date):
        self.label = "available"
        self.text = "Block reservieren?"
        self.date = date
        self.timestamp = date.timestamp()
        self.available = "available"
        self.bookable = self.date > datetime.now()


class BlockBooked(object):

    def __init__(self, date):
        self.label = "booked"
        self.text = "Belegt"
        self.date = date
        self.timestamp = date.timestamp()
        self.available = "booked"
        self.bookable = self.date > datetime.now()


class BlockReserved(object):

    def __init__(self, date):
        self.label = "reserved"
        self.text = "Reserviert"
        self.date = date
        self.timestamp = self.date.timestamp()
        self.available = "reserved"
        self.bookable = self.date > datetime.now()


class CancellationAlert(GreenAlert):

    def __init__(self, date):
        message = "Buchung storniert: {0}".format(
            date.strftime("%d.%m.%y, %H:%M Uhr"))
        super(CancellationAlert, self).__init__(message)


class BookingSuccessfulAlert(GreenAlert):

    def __init__(self, date):
        message = "Gebucht: {0}".format(date.strftime("%d.%m.%y, %H:%M Uhr"))
        super(BookingSuccessfulAlert, self).__init__(message)


class NotAllowedAlert(RedAlert):

    def __init__(self):
        message = "Buchung nicht möglich"
        super(NotAllowedAlert, self).__init__(message)


class CancellationNotAllowedAlert(RedAlert):

    def __init__(self):
        message = "Stornieren nicht möglich: liegt in der Vergangenheit"
        super(CancellationNotAllowedAlert, self).__init__(message)


class QuotaExceededAlert(RedAlert):

    def __init__(self):
        message = "Buchungskontingent reicht nicht aus"
        super(QuotaExceededAlert, self).__init__(message)
