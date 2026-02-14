class CourierCannotTakeOrder(BaseException):
    pass


class OrderVolumeIncorrect(BaseException):
    pass


class CourierNameIncorrect(BaseException):
    pass


class CourierSpeedIncorrect(BaseException):
    pass


class CourierNotFound(BaseException):
    pass
