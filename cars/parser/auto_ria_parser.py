import re

from playwright.sync_api import sync_playwright


def parse_auto_ria(max_price=None):
    cars = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            viewport={"width": 1280, "height": 800},
            locale="uk-UA"
        )

        page = context.new_page()

        url = "https://auto.ria.com/uk/search/?search_type=1&category=1&price[0]=1&abroad=0&customs_cleared=1"

        if max_price:
            url += f"&price[2]={max_price}"

        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_selector("a.product-card", timeout=15000)

        items = page.query_selector_all("a.product-card")

        for item in items[:5]:
            try:
                title = item.query_selector(".titleS").inner_text()
                price_raw = item.query_selector(".c-green").inner_text()
                price = int(re.sub(r"\D", "", price_raw))
                modification = item.query_selector(".ellipsis-1").inner_text()
                link = item.get_attribute("href")

                spans = item.query_selector_all("span.common-text")
                mileage = None

                for span in spans:
                    text = span.inner_text()
                    if "км" in text:
                        mileage = text
                        break

                cars.append({
                    "title": title,
                    "price": price, # для користувача
                    "price_raw": price_raw, # для апі
                    "modification": modification,
                    "mileage": mileage,
                    "link": "https://auto.ria.com" + link
                })

            except Exception as e:
                print("ERROR:", e)
                continue

        browser.close()

    return cars