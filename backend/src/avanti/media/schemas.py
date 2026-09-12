"""DTO модуля media."""

from pydantic import BaseModel


class MediaOut(BaseModel):
    """Результат безопасно сохранённого файла."""

    filename: str
    url: str
    content_type: str
    size: int
