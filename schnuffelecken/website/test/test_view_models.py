from django.test import TestCase

from website.models import *
from website.viewmodels import *


class ViewModelTests(TestCase):

    def setUp(self):
        pass

    def test_row(self):
        hour = 8
        blocks = [1, 2, 3]

        row = Row(hour, blocks)

        self.assertEqual(row.time_start, "{0:02d}:00".format(hour))
        self.assertEqual(row.time_end, "{0:02d}:00".format(hour + 1))
        self.assertEqual(row.blocks, blocks)

    def test_week_create_viewmodel(self):
        pattern = "%d.%m.%y"
        now = datetime(2030, 3, 11)
        facility = 'g'
        user = 'max'

        week = Week(now)
        vm = WeekViewModel(week, facility, user)

        self.assertEqual(len(vm.headers), 5)

        self.assertEqual(vm.headers[0][0], "Montag")
        self.assertEqual(vm.headers[1][0], "Dienstag")
        self.assertEqual(vm.headers[2][0], "Mittwoch")
        self.assertEqual(vm.headers[3][0], "Donnerstag")
        self.assertEqual(vm.headers[4][0], "Freitag")

        self.assertEqual(vm.headers[0][1], now.strftime(pattern))
        self.assertEqual(vm.headers[1][1], (now + timedelta(1)).strftime(pattern))
        self.assertEqual(vm.headers[2][1], (now + timedelta(2)).strftime(pattern))
        self.assertEqual(vm.headers[3][1], (now + timedelta(3)).strftime(pattern))
        self.assertEqual(vm.headers[4][1], (now + timedelta(4)).strftime(pattern))
        self.assertEqual(len(vm.rows), 11)
        self.assertEqual(vm.calendar_week, 11, "Expected KW to be 11")
