from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 0
    limit: int = 50

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
