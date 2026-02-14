"""Human-like behavior simulation — mouse movements, scrolling, and natural click timing."""

import random
import time

from playwright.sync_api import Page


def random_mouse_movements(page: Page, count: int = 5) -> None:
    """Move the mouse to random positions on the page to generate interaction signals.

    Args:
        page: Playwright Page instance.
        count: Number of random movements.
    """
    viewport = page.viewport_size
    if not viewport:
        return

    for _ in range(count):
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        # Move with slight random steps to appear natural
        page.mouse.move(x, y, steps=random.randint(3, 8))
        time.sleep(random.uniform(0.05, 0.2))


def random_scroll(page: Page) -> None:
    """Scroll the page down and then back up with natural timing.

    Args:
        page: Playwright Page instance.
    """
    # Scroll down in small increments
    for _ in range(random.randint(2, 4)):
        scroll_amount = random.randint(80, 200)
        page.mouse.wheel(0, scroll_amount)
        time.sleep(random.uniform(0.2, 0.5))

    time.sleep(random.uniform(0.3, 0.8))

    # Scroll back up
    for _ in range(random.randint(1, 3)):
        scroll_amount = random.randint(80, 200)
        page.mouse.wheel(0, -scroll_amount)
        time.sleep(random.uniform(0.2, 0.5))


def human_click(page: Page, selector: str) -> None:
    """Click an element with human-like hover → pause → click behavior.

    Args:
        page: Playwright Page instance.
        selector: CSS selector for the target element.
    """
    element = page.locator(selector)
    box = element.bounding_box()

    if box:
        # Move to a random point within the element (not dead center)
        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        # Move mouse to element with steps (simulates natural cursor path)
        page.mouse.move(target_x, target_y, steps=random.randint(5, 12))

        # Brief hover pause before clicking
        time.sleep(random.uniform(0.1, 0.3))

        # Click
        page.mouse.click(target_x, target_y)
    else:
        # Fallback to standard click if bounding box unavailable
        element.click()
