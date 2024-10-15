from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(1, description="Current page number")
    limit: int = Field(50, description="Number of items per page")
    total_items: int = Field(0, description="Total number of items")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

    @property
    def total_pages(self) -> int:
        if self.limit == 0:
            return 0
        return (self.total_items + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data.update({
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous
        })
        return data


class Data_display(BaseModel):
    data: list
    pagination: Pagination
