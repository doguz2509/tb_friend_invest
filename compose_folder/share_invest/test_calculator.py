from unittest import TestCase

from share_calculator import ShareCalculator


class TestParticipantInvestCalculator(TestCase):
    def test_01(self):
        c = ShareCalculator(100, 10)
        if c.add_amount_per_participant('dima', 50):
            raise
        if c.add_amount_per_participant('roni', 25):
            raise
        if not c.add_amount_per_participant('maks', 50):
            raise

        r = c()
        print(f"{r}")
