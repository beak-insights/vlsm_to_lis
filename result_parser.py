import math

INTEPRETATIONS = {
    "< Titer min": "< 20"
}


class IntResultHandler:
    def __init__(self, result, test_unit):
        self.result = result
        self.test_unit = test_unit

    def to_float(self, val):
        """
        Given a number we need to convert it to a first digit floating point number
        e.g:
            234 -> 2.34
            3566 -> 3.566
        """
        if isinstance(val, float):
            return val

        val = str(val)

        return float(val[0] + "." + val[1:])

    @property
    def quotient(self):
        """derive padding from 'xxx*quotient.unit'"""
        # get 'xxx*exp'
        val = self.test_unit.split('.')[0]
        # get 'exp'
        return int(val.split('*')[1])

    def multiplier(self, multiple):
        """derive padding from 'xxx*exp.unit'"""
        return eval('1' + '0'*abs(multiple))

    def round(self, val):
        """For results with >= .5 round up else round down"""
        return round(val)

    def try_cast(self, val):
        """Thorough check if current result is strictly text or numeric"""
        try:
            val = int(val)
        except ValueError:
            pass
        return val


class StringResultParser:
    def handle(self, val):
        return INTEPRETATIONS.get(val, val)


class ResultParser(IntResultHandler, StringResultParser):
    @property
    def output(self):
        """
        Evaluate result based on result type:
        for Titres recalculate titres based on test unit
        """
        val = self.try_cast(self.result)
        if isinstance(val, str):
            return self.handle(val)

        if not self.test_unit:
            return val

        if self.quotient == 0:
            return val

        multiplier = self.multiplier(self.quotient)
        if self.quotient > 0:
            return val*multiplier

        # self.quotient < 0
        return self.round(val/multiplier)
