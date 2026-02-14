class OrderVolumeIncorrect(BaseException):
    pass


class OrderAlreadyAssigned(BaseException):
    pass


class OrderCannotBeAssigned(BaseException):
    pass


class OrderCannotBeCompleted(BaseException):
    pass
