from playwright.sync_api import sync_playwright

LISTINGS_URL = "https://www.berlinovo.de/de/apartments/suche?a%5B0%5D=apartments_angebot%3AS&a%5B1%5D=keine_apartments_verfuegbar%3A0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    print("Opening Berlinovo listings page...")
    page.goto(LISTINGS_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    print()
    print("PAGE TITLE:")
    print(page.title())

    print()
    print("LISTING LINKS:")
    print("=" * 70)

    links = page.locator("a[href]")
    found = set()

    for i in range(links.count()):
        link = links.nth(i)

        try:
            href = link.get_attribute("href")
            text = link.inner_text().strip()

            if href and "/de/apartments/" in href and "/suche" not in href:
                if href.startswith("/"):
                    href = "https://www.berlinovo.de" + href

                if href not in found:
                    found.add(href)
                    print(f"{len(found)}. {text}")
                    print(f"   {href}")
                    print()

        except Exception:
            pass

    print("=" * 70)
    print(f"TOTAL LISTING PAGES FOUND: {len(found)}")

    page.screenshot(path="berlinovo_listings.png", full_page=True)

    print()
    print("Screenshot saved as: berlinovo_listings.png")
    print()
    print("Leave the browser open for inspection.")
    input("Press ENTER when finished...")

    browser.close()
