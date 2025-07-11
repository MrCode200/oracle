from requests import RequestException
from requests.exceptions import HTTPError


def handle_binance_status(status_code: int, data: dict) -> None:
    match status_code:
        case 200:
            return
        case 400:
            raise HTTPError("Malformed request (400 Bad Request). "
                            "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
        case 403:
            raise HTTPError("Access forbidden, possibly WAF limit violation (403 Forbidden). "
                            "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
        case 409:
            raise HTTPError("Partial order success, cancellation failed (409 Conflict). "
                            "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
        case 418:
            raise RequestException("IP auto-banned after too many requests (418 I'm a teapot). "
                                   "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
        case 429:
            raise RuntimeError("Too many requests, rate limit exceeded (429 Too Many Requests). "
                               "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
        case _:
            if status_code <= 500:
                raise RequestException("Internal Server Error (5xx). "
                                       "Code {}: '{}'".format(getattr(data, "code", None), getattr(data, "msg", None)))
            else:
                raise HTTPError(
                    f"Unhandled HTTP status code: {status_code}. "
                    f"Code {getattr(data, "code", None)}: '{getattr(data, "msg", None)}'"
                )
