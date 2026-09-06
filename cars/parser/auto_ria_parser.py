import logging
import os
import re
from urllib.parse import urljoin

from django.conf import settings

logger = logging.getLogger(__name__)


def parse_auto_ria(max_price=None, min_price=None):
    from playwright.sync_api import sync_playwright

    cars = []
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-dev-shm-usage"],
        )

        try:
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                locale="uk-UA",
            )

            page = context.new_page()

            url = (
                "https://auto.ria.com/uk/search/?search_type=1&category=1"
                "&price[0]=1&abroad=0&customs_cleared=1"
            )

            if min_price:
                url += f"&price[1]={int(min_price)}"
            if max_price:
                url += f"&price[2]={int(max_price)}"

            logger.info("Parsing AUTO.RIA price range %s-%s", min_price, max_price)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            card_selector = "section.ticket-item, a.product-card"
            page.wait_for_selector(card_selector, timeout=20000)

            items = page.query_selector_all(card_selector)

            for item in items[: settings.PARSER_RESULT_LIMIT]:
                try:
                    metadata = item.query_selector("[data-advertisement-data]")
                    title_element = item.query_selector(".head-ticket a.address, .titleS")
                    price_element = item.query_selector(".price-ticket, .c-green")
                    link_element = item.query_selector(".head-ticket a.address")
                    link = (
                        link_element.get_attribute("href")
                        if link_element
                        else item.get_attribute("href")
                    )
                    if not title_element or not price_element or not link:
                        continue

                    title = " ".join(title_element.inner_text().split())
                    price_raw = (
                        price_element.get_attribute("data-main-price")
                        or price_element.inner_text()
                    )
                    price = int(re.sub(r"\D", "", price_raw))
                    modification_element = item.query_selector(".generation, .ellipsis-1")
                    modification = (
                        modification_element.inner_text() if modification_element else ""
                    )

                    mileage_element = item.query_selector(".js-race")
                    mileage = mileage_element.inner_text().strip() if mileage_element else None
                    if not mileage:
                        for span in item.query_selector_all("span.common-text"):
                            text = span.inner_text()
                            if "км" in text:
                                mileage = text
                                break

                    cars.append(
                        {
                            "title": title,
                            "brand": (
                                metadata.get_attribute("data-mark-name")
                                if metadata
                                else None
                            ),
                            "model": (
                                metadata.get_attribute("data-model-name")
                                if metadata
                                else None
                            ),
                            "year": (
                                metadata.get_attribute("data-year")
                                if metadata
                                else None
                            ),
                            "price": price,
                            "price_raw": price_raw,
                            "modification": modification,
                            "mileage": mileage,
                            "link": urljoin("https://auto.ria.com", link),
                        }
                    )
                except Exception:
                    logger.exception("Could not parse an AUTO.RIA product card")

            logger.info("Parsed %s AUTO.RIA listings", len(cars))
        finally:
            browser.close()

    return cars
