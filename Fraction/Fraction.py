def gcd(a, b):
    try:
        if isinstance(a, int) and isinstance(b, int):
            if a != 0 and b != 0:
                if b > a:
                    a, b = b, a
                if a % b == 0:
                    return b
                else:
                    return gcd((a % b), b)
            else:
                raise ValueError("Invalid Value(s): Expected non-zero values")
        else:
            raise InvalidArgumentError(
                "Invalid Argument Type: expected <+int, +int>")
    except ValueError as val_exception:
        print(val_exception)
    except InvalidArgumentError as arg_exception:
        print(arg_exception)


class InvalidArgumentError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Fraction:
    def get_numerator(self):
        return self.__numerator

    def get_denominator(self):
        return self.__denominator

    def get_sign_flag(self):
        return self.__sign_flag

    def get_zero_flag(self):
        return self.__zero_flag

    def get_float_value(self):
        return float((self.__sign_flag * self.__numerator) /
                     self.__denominator)

    def simplify(self):
        if gcd(self.__numerator, self.__denominator) != 1:
            return Fraction(
                (self.__numerator / gcd(self.__numerator, self.__denominator)),
                (self.__denominator / gcd(self.__numerator,
                                          self.__denominator)))
        else:
            return Fraction(self.__numerator, self.__denominator)

    def __init__(self, numerator, denominator=None):
        try:
            if denominator is not None:
                if isinstance(numerator,
                              (int, float, Fraction)) and isinstance(
                        denominator, (int, float, Fraction)):
                    if isinstance(numerator, int) and isinstance(denominator,
                                                                 int):
                        if denominator == 0:
                            raise ValueError(
                                "Division by Zero: Expected non-zero value "
                                "in denominator")
                        else:
                            if numerator == 0:
                                self.__zero_flag = True
                                self.__sign_flag = 1
                                self.__numerator = 0
                                self.__denominator = 1
                            else:
                                self.__zero_flag = False
                                if numerator * denominator < 0:
                                    self.__sign_flag = -1
                                else:
                                    self.__sign_flag = 1
                                self.__numerator = int(
                                    abs(numerator) / gcd(abs(numerator),
                                                         abs(denominator)))
                                self.__denominator = int(
                                    abs(denominator) / gcd(abs(numerator),
                                                           abs(denominator)))
                    else:
                        if isinstance(numerator, float):
                            numerator = Fraction.from_float(numerator)
                        if isinstance(denominator, float):
                            denominator = Fraction.from_float(denominator)
                        if isinstance(numerator, int):
                            numerator = Fraction.from_int(numerator)
                        if isinstance(denominator, int):
                            denominator = Fraction.from_int(denominator)
                        if not denominator.get_zero_flag():
                            if numerator.get_sign_flag() * \
                                    denominator.get_sign_flag() < 0:
                                self.__sign_flag = -1
                            else:
                                self.__sign_flag = 1

                            if numerator.get_zero_flag():
                                self.__zero_flag = True
                                self.__numerator = 0
                                self.__denominator = 1
                            else:
                                self.__zero_flag = False
                                self.__numerator = abs((numerator.__div__(
                                    denominator)).simplify().get_numerator())
                                self.__denominator = abs((numerator.__div__(
                                    denominator)).simplify().get_denominator())
                        else:
                            raise ValueError(
                                "Illegal Value: Expected non-zero Denominator")
                else:
                    raise InvalidArgumentError(
                        "Invalid Argument: Expected <int/float/Fraction, "
                        "int/float/Fraction>")
            else:
                ratio = None
                if isinstance(numerator, float):
                    ratio = Fraction.from_float(numerator)
                if isinstance(numerator, int):
                    ratio = Fraction.from_int(numerator)
                self.__zero_flag = ratio.get_zero_flag()
                self.__sign_flag = ratio.get_sign_flag()
                self.__numerator = ratio.get_numerator()
                self.__denominator = ratio.get_denominator()
        except InvalidArgumentError as arg_exception:
            print(arg_exception)
        except ValueError as val_exception:
            print(val_exception)

    @classmethod
    def from_float(cls, n):
        try:
            if isinstance(n, float):
                frac = n.as_integer_ratio()
                return Fraction(frac[0], frac[1])
            else:
                raise InvalidArgumentError(
                    "Invalid Argument Type: Expected <float>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)

    @classmethod
    def from_int(cls, n):
        try:
            if isinstance(n, int):
                return Fraction(n, 1)
            else:
                raise InvalidArgumentError(
                    "Invalid Argument Type: Expected <float>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)

    def inverse(self):
        try:
            if not self.__zero_flag:
                return (
                    Fraction(self.__denominator, self.__numerator)).simplify()
            else:
                raise ValueError("Division by Zero: Zero can not be inverted")
        except ValueError as val_exception:
            print(val_exception)

    def __add__(self, fraction):
        try:
            if isinstance(fraction, (int, float, Fraction)):
                if isinstance(fraction, int):
                    fraction = Fraction.from_int(fraction)
                if isinstance(fraction, float):
                    fraction = Fraction.from_float(fraction)
                return Fraction(((
                                     self.__sign_flag * self.__numerator *
                                     fraction.get_denominator()) + (
                                     fraction.get_sign_flag() *
                                     fraction.get_numerator() *
                                     self.__denominator)),
                                (
                                    self.__denominator *
                                    fraction.get_denominator())).simplify()
            else:
                raise InvalidArgumentError(
                    "Invalid Argument: Expected <int/float/Fraction>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)

    def __sub__(self, fraction):
        try:
            if isinstance(fraction, (int, float, Fraction)):
                if isinstance(fraction, int):
                    fraction = Fraction.from_int(fraction)
                if isinstance(fraction, float):
                    fraction = Fraction.from_float(fraction)
                return Fraction(((
                                     self.__sign_flag * self.__numerator *
                                     fraction.get_denominator()) - (
                                     fraction.get_sign_flag() *
                                     fraction.get_numerator() *
                                     self.__denominator),
                                 self.__denominator *
                                 fraction.get_denominator())).simplify()
            else:
                raise InvalidArgumentError(
                    "Invalid Argument: Expected <int/float/Fraction>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)

    def __mul__(self, fraction):
        try:
            if isinstance(fraction, (int, float, Fraction)):
                if isinstance(fraction, int):
                    fraction = Fraction.from_int(fraction)
                if isinstance(fraction, float):
                    fraction = Fraction.from_float(fraction)
                return (Fraction((
                    self.__sign_flag * fraction.get_sign_flag()
                    * self.__numerator *
                    fraction.get_numerator()),
                    (
                        self.__denominator *
                        fraction.get_denominator()))).simplify()
            else:
                raise InvalidArgumentError(
                    "Invalid Argument: Expected <int/float/Fraction>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)

    def __div__(self, fraction):
        try:
            if isinstance(fraction, (int, float, Fraction)):
                if not self.__zero_flag:
                    return self.__mul__(fraction.inverse())
                else:
                    raise ValueError('Illegal Division: Division by Zero')
            else:
                raise InvalidArgumentError(
                    "Invalid Argument: Expected <int/float/Fraction>")
        except InvalidArgumentError as arg_exception:
            print(arg_exception)
        except ValueError as val_exception:
            print(val_exception)

    def __str__(self):
        if self.__denominator == 1:
            return str(self.__sign_flag * self.__numerator)
        else:
            return str(self.__sign_flag * self.__numerator) + "/" + str(
                self.__denominator)
