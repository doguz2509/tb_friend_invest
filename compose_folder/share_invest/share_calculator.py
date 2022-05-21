import logging
import os
from collections import namedtuple

result_item = namedtuple('ResultItem', ('Units', 'Spend', 'Change'))

logger = logging.getLogger(os.path.split(__file__)[-1])


class ShareCalculator:
    def __init__(self):
        self._participants: dict = {}
        self._participant_change: dict = {}
        self._price: float = 0
        self._count: float = 0
        self._ready_for_invoice = False
        logger.info(f"Started {self}")

    def __str__(self):
        return f"{self.__class__.__name__}:{id(self)}"

    def add_amount_per_participant(self, name: str, amount: float):
        _new_amount = self._participants.get(name, 0) + amount

        if sum([am_ for name_, am_ in self._participants.items() if name_ != name]) + _new_amount > self._price:
            _new_updated_amount = self._price - sum(
                [am_ for name_, am_ in self._participants.items() if name_ != name])
            _change = _new_amount - _new_updated_amount
            self._participants.update(**{name: _new_updated_amount})
            self._participant_change.update(**{name: _change})
            self._ready_for_invoice = True
        elif sum([am_ for name_, am_ in self._participants.items() if name_ != name]) + _new_amount < self._price:
            self._participants.update(**{name: _new_amount})
            self._ready_for_invoice = False
        else:
            self._participants.update(**{name: _new_amount})
            self._ready_for_invoice = True
        logger.info("{self}::add_amount_per_participant: {name} -> {price}{change}".format(
            self=self,
            name=name,
            price=self._participants.get(name),
            change=f"; change: {self._participant_change.get(name)}"
            if self._participant_change.get(name, 0) > 0 else ""
            )
        )

    @property
    def purchase(self):
        return dict(price=self._price, count=self._count)
        # return f"Price: {self._price}; Count: {self._count}"

    def set_amount(self, amount: float, append=False):
        _amount = (self._price + amount) if append else amount
        self._price = _amount
        logger.info(f"{self}::set_amount: {amount}")

    def set_units(self, units, append=False):
        _units = (self._count + units) if append else units
        self._count = _units
        logger.info(f"{self}::set_units: {units}")

    @property
    def invoice_ready(self) -> bool:
        return sum(self._participants.values()) >= self._price

    @property
    def invoice(self):
        assert self._ready_for_invoice, \
            f"""Overall purchase amount not reached; 
Collected {sum(self._participants.values())} of total price {self._price};
Continue to add or update participant involvement"""
        return {name: result_item(amount / self._price * self._count, amount,
                                  self._participant_change.get(name, 0))
                for name, amount in self._participants.items()}


__all__ = [
    'ShareCalculator'
]
