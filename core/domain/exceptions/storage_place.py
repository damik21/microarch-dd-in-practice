class StorageCannotStoreOrder(BaseException):
    pass

class CourierHasNoSuchOrder(BaseException):
    pass

class StoragePlaceNameIncorrect(BaseException):
    pass

class StoragePlaceTotalValueIncorrect(BaseException):
    pass