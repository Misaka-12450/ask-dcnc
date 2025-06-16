"""
ask_dcnc/html.py
HTML-related utilities
"""

import re

from bs4 import BeautifulSoup
from langchain_community.utilities import TextRequestsWrapper


class HTMLStripRequestsWrapper(TextRequestsWrapper):
    """
    Strips down HTML tags from the webpages to avoid exceeding token limits
    """

    def get(self, url: str, **kwargs) -> str:
        html = super().get(url, **kwargs)

        # Parse and remove script/style tags
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Preserve URLs
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True) or a["href"]
            a.replace_with(f"[{text}]({a['href']})")

        # Remove all mobile nav elements
        for tag in soup.select("[class*='mobinav']"):
            tag.decompose()

        # Strip tags, whitespaces, and newlines
        text = soup.get_text(strip=True)
        text = text.replace("\\n", " ")

        return re.sub(r'\s+', ' ', text)
