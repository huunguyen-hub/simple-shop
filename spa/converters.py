# https://www.webforefront.com/django/accessurlparamstemplates.html
class RomanNumeralConverter:
    regex = '[MDCLXVImdclxvi]+'

    @staticmethod
    def to_python(value):
        return str(value)

    @staticmethod
    def to_url(self, value):
        return '{}'.format(value)


class FloatConverter:
    regex = '[\d\.\d]+'

    @staticmethod
    def to_python(self, value):
        return float(value)

    @staticmethod
    def to_url(self, value):
        return '{}'.format(value)
