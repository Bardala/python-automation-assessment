"""Intercepts the outgoing POST request to capture the reCAPTCHA token before it reaches the server."""

import re

from playwright.sync_api import Page, Route


class TokenInterceptor:
    """Captures the reCAPTCHA token from the outgoing FormData POST request."""

    def __init__(self):
        self.token: str | None = None

    def attach(self, page: Page, target_url: str) -> None:
        """Register a route handler to intercept the POST containing the token.

        Args:
            page: Playwright page instance.
            target_url: URL pattern to intercept (the page POSTs to itself).
        """
        page.route(target_url, self._handle_route)

    def _handle_route(self, route: Route) -> None:
        """Extract token from the intercepted request and continue.

        The page uses fetch() with a FormData object, which sends
        multipart/form-data encoding. The token field appears between
        Content-Disposition headers in the raw body.
        """
        request = route.request
        if request.method == "POST" and request.post_data:
            body = request.post_data
            # Multipart: token value follows its Content-Disposition header
            match = re.search(
                r'name="token"\r?\n\r?\n(.+?)(?:\r?\n--)', body, re.DOTALL
            )
            if match:
                self.token = match.group(1).strip()
            else:
                # Fallback: URL-encoded form
                for part in body.split("&"):
                    if part.startswith("token="):
                        self.token = part[len("token="):]
                        break
        route.continue_()
