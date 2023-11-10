"Common exceptions and warnings"

import pyparsing as pp


class ParseException(pp.ParseException):
    pass


class ParseWarning(RuntimeWarning):
    pass
