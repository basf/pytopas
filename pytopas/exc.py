"Common exceptions and warnings"

import pyparsing as pp


class ParseException(pp.ParseException):
    "Parse error"


class ReconstructException(Exception):
    "Reconstruction error"


class ParseWarning(RuntimeWarning):
    "Parse warning"
