from __future__ import annotations

import asyncio
import re
from typing import Any, Optional
from urllib.parse import urlparse

from aiohttp import ClientSession, ClientTimeout

from .const import USER_AGENT

LAKE_TEMP_REGEXES = [
    re.compile(r"Wassertemperatur\D*([0-9]+(?:[.,][0-9])?)\s*°\s*C", re.IGNORECASE),
    re.compile(r"([0-9]+(?:[.,][0-9])?)\s*°\s*C", re.IGNORECASE),
]
TITLE_REGEX = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class WassertemperaturClient:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def _fetch_html(self, url: str) -> str:
        timeout = ClientTimeout(total=15)
        headers = {"User-Agent": USER_AGENT}
        async with self._session.get(url, timeout=timeout, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.text()

    @staticmethod
    def _parse_lake_name(html: str, url: str) -> str:
        m = TITLE_REGEX.search(html)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()
            # Titles often contain separators like " - Wassertemperatur"; keep first part
            if " - " in title:
                return title.split(" - ")[0].strip()
            return title
        # Fallback to URL path
        parsed = urlparse(url)
        slug = parsed.path.strip("/").split("/")[-1]
        return slug.replace("-", " ").title() or url

    @staticmethod
    def _parse_temperature_c(html: str) -> Optional[float]:
        for rx in LAKE_TEMP_REGEXES:
            m = rx.search(html)
            if m:
                txt = m.group(1).replace(",", ".")
                try:
                    return float(txt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _slug_from_url(url: str) -> str:
        p = urlparse(url)
        slug = p.path.strip("/").split("/")[-1]
        return slug or p.netloc

    async def fetch_lake(self, url: str) -> dict[str, Any]:
        html = await self._fetch_html(url)
        temp = self._parse_temperature_c(html)
        name = self._parse_lake_name(html, url)
        slug = self._slug_from_url(url)
        return {
            "lake_url": url,
            "lake_name": name,
            "lake_id": slug,
            "temperature_c": temp,
        }
