from typing import Annotated, Literal

from pydantic import Field

from .models import ApiModel

TextFilter = Annotated[str, Field(max_length=256)]


class PageQuery(ApiModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class SelectionQuery(ApiModel):
    q: TextFilter | None = None
    platform: TextFilter | None = None
    material: TextFilter | None = None
    gravity_raw: TextFilter | None = None
    tag: TextFilter | None = None
    purpose: TextFilter | None = None
    source_type: TextFilter | None = None
    evidence_status: TextFilter | None = None
    review_status: TextFilter | None = None


class CatalogQuery(SelectionQuery, PageQuery):
    sort: Literal["title-asc", "runs-desc"] = "title-asc"
