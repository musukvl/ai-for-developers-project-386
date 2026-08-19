"""The API's fixed error codes and JSON error envelope."""

from __future__ import annotations

_STATUS_BY_CODE = {
    "validation_error": 400,
    "name_mismatch": 400,
    "not_found": 404,
    "conflict": 409,
}


class ApiError(Exception):
    """An error that maps directly onto the API's `{"error": {code, message}}` envelope."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = _STATUS_BY_CODE[code]

    def to_body(self) -> dict:
        return {"error": {"code": self.code, "message": self.message}}


def validation_error(message: str) -> ApiError:
    return ApiError("validation_error", message)


def name_mismatch(
    message: str = "The entered name does not match the calendar owner.",
) -> ApiError:
    return ApiError("name_mismatch", message)


def not_found(message: str = "The requested resource was not found.") -> ApiError:
    return ApiError("not_found", message)


def conflict(message: str) -> ApiError:
    return ApiError("conflict", message)
