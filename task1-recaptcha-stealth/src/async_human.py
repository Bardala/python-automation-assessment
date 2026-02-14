"""Async Mouse/Scroll Simulation."""

import random
from playwright.async_api import Page

async def random_mouse_movements(page: Page, count: int = 5) -> None:
    viewport = page.viewport_size
    if not viewport:
        return

    for _ in range(count):
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        # Non-blocking sleep: critical for async
        await page.mouse.move(x, y, steps=random.randint(5, 12))
        await page.wait_for_timeout(random.uniform(50, 200))

async def random_scroll(page: Page) -> None:
    for _ in range(random.randint(2, 4)):
        scroll_amount = random.randint(80, 200)
        await page.mouse.wheel(0, scroll_amount)
        await page.wait_for_timeout(random.uniform(200, 500))

    await page.wait_for_timeout(random.uniform(300, 800))

    for _ in range(random.randint(1, 3)):
        scroll_amount = random.randint(80, 200)
        await page.mouse.wheel(0, -scroll_amount)
        await page.wait_for_timeout(random.uniform(200, 500))

async def human_click(page: Page, selector: str) -> None:
    element = page.locator(selector)
    box = await element.bounding_box()

    if box:
        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        await page.mouse.move(target_x, target_y, steps=random.randint(10, 25))
        await page.wait_for_timeout(random.uniform(200, 600))
        await page.mouse.click(target_x, target_y)
    else:
        await element.click()
