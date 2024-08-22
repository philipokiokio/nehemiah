from datetime import date


def today():
    return date.today()


def is_sunday() -> bool:
    day_ = date.today().isoweekday()
    if day_ != 7:
        return False

    return True


def is_tuesday() -> bool:
    day_ = date.today().isoweekday()
    if day_ != 2:
        return False

    return True


def is_wednesday() -> bool:
    day_ = date.today().isoweekday()
    if day_ != 3:
        return False

    return True
