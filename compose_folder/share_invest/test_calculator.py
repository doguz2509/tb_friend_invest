from unittest import TestCase

from share_calculator import ShareCalculator


class TestParticipantInvestCalculator(TestCase):
    def test_01(self):
        c = ShareCalculator()
        c.set_amount(100)
        c.set_units(10)
        c.add_amount_per_participant('dima', 50)
        c.add_amount_per_participant('roni', 25)
        c.add_amount_per_participant('maks', 50)
        r = c.invoice
        print(f"{r}")
