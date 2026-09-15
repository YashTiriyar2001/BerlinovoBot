from playwright.sync_api import sync_playwright

START_URL = "https://www.berlinovo.de/de/apartments/suche?a%5B0%5D=apartments_angebot%3AS&a%5B1%5D=keine_apartments_verfuegbar%3A0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    page.goto(START_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)

    print()
    print("=" * 80)
    print("PAGINATION LINKS")
    print("=" * 80)

    links = page.locator("a[href]")

    for i in range(links.count()):
        link = links.nth(i)

        try:
            if not link.is_visible():
                continue

            text = link.inner_text().strip()
            href = link.get_attribute("href")
            aria = link.get_attribute("aria-label")
            title = link.get_attribute("title")
            classes = link.get_attribute("class")

            if text or aria or title:
                print(f"\nLINK {i}")
                print("TEXT:", repr(text))
                print("HREF:", repr(href))
                print("ARIA:", repr(aria))
                print("TITLE:", repr(title))
                print("CLASS:", repr(classes))

        except Exception:
            pass

    print()
    print("=" * 80)
    print("BUTTONS")
    print("=" * 80)

    buttons = page.locator("button")

    for i in range(buttons.count()):
        button = buttons.nth(i)

        try:
            if not button.is_visible():
                continue

            print(f"\nBUTTON {i}")
            print("TEXT:", repr(button.inner_text().strip()))
            print("ARIA:", repr(button.get_attribute("aria-label")))
            print("TITLE:", repr(button.get_attribute("title")))
            print("CLASS:", repr(button.get_attribute("class")))
            print("DISABLED:", button.is_disabled())

        except Exception:
            pass

    print()
    print("=" * 80)
    print("CURRENT URL")
    print("=" * 80)
    print(page.url)

    input("\nPress ENTER to close...")

    browser.close()
