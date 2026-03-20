from fastapi import HTTPException, status

class APIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFound(APIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class BadRequest(APIException):
    def __init__(self, detail: str = "Invalid request data"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class Unauthorized(APIException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class Forbidden(APIException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)

class Conflict(APIException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status.HTTP_409_CONFLICT, detail)
