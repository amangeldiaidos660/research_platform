from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class OpenAlexClient:
    def __init__(self) -> None:
        self.base_url = settings.openalex_base_url.rstrip("/")
        self.default_per_page = settings.openalex_default_per_page

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": "ResearchIntelligencePlatform/0.1"}

    def _params(self, **kwargs: Any) -> dict[str, Any]:
        params = {key: value for key, value in kwargs.items() if value not in (None, "", False)}
        if settings.openalex_mailto:
            params["mailto"] = settings.openalex_mailto
        if settings.openalex_api_key:
            params["api_key"] = settings.openalex_api_key
        return params

    def list_entities(self, entity: str, **kwargs: Any) -> dict[str, Any]:
        params = self._params(**kwargs)
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            response = client.get(f"{self.base_url}/{entity}", params=params)
            response.raise_for_status()
            return response.json()

    def get_entity(self, entity: str, openalex_id: str, select: str | None = None) -> dict[str, Any]:
        params = self._params(select=select)
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            response = client.get(f"{self.base_url}/{entity}/{openalex_id}", params=params)
            response.raise_for_status()
            return response.json()

    def iterate_entities(
        self,
        entity: str,
        *,
        search: str | None = None,
        filter: str | None = None,
        select: str | None = None,
        sort: str | None = None,
        per_page: int | None = None,
        pages: int = 1,
        use_cursor: bool = False,
    ) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        per_page = per_page or self.default_per_page

        if use_cursor:
            cursor = "*"
            for _ in range(pages):
                payload = self.list_entities(
                    entity,
                    search=search,
                    filter=filter,
                    select=select,
                    sort=sort,
                    per_page=per_page,
                    cursor=cursor,
                )
                collected.extend(payload.get("results", []))
                cursor = payload.get("meta", {}).get("next_cursor")
                if not cursor:
                    break
        else:
            for page in range(1, pages + 1):
                payload = self.list_entities(
                    entity,
                    search=search,
                    filter=filter,
                    select=select,
                    sort=sort,
                    per_page=per_page,
                    page=page,
                )
                collected.extend(payload.get("results", []))

        return collected
