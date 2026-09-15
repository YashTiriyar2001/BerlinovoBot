from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://www.berlinovo.de/de/apartments/suche"
PARAMS = "?a%5B0%5D=apartments_angebot%3AS&a%5B1%5D=keine_apartments_verfuegbar%3A0"


def get_listing_links(page):
    links = page.locator("a[href]")
    found = []

    ignored = [
        "/datenschutz",
        "/mieterservice",
        "/firmenservice",
        "/apartmentanlagen",
        "/team"
    ]

    for i in range(links.count()):
        link = links.nth(i)

        try:
            href = link.get_attribute("href")

            if not href:
                continue

            full_url = urljoin(page.url, href)

            if "/de/apartments/" not in full_url:
                continue

            if "/suche" in full_url:
                continue

            if any(x in full_url for x in ignored):
                continue

            if full_url not in found:
                found.append(full_url)

        except Exception:
            pass

    return found


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    all_listings = []

    # Berlinovo currently exposes 3 pages.
    # We use the numbered pagination rather than guessing a "next" button.
    for page_number in range(3):

        if page_number == 0:
            url = BASE_URL + PARAMS
        else:
            url = BASE_URL + PARAMS + f"&page={page_number}"

        print()
        print("=" * 80)
        print(f"LISTING PAGE {page_number + 1}")
        print("=" * 80)
        print(url)

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(3000)

        listings = get_listing_links(page)

        print(f"Listings found on this page: {len(listings)}")

        for listing in listings:
            if listing not in all_listings:
                all_listings.append(listing)
                print(f"{len(all_listings)}. {listing}")

    print()
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    for i, listing in enumerate(all_listings, 1):
        print(f"{i}. {listing}")

    print()
    print(f"TOTAL UNIQUE LISTINGS: {len(all_listings)}")
    print("TOTAL LISTING PAGES VISITED: 3")

    with open("all_listings.txt", "w", encoding="utf-8") as f:
        for listing in all_listings:
            f.write(listing + "\n")

    print()
    print("Saved: all_listings.txt")
    print("No applications were opened or submitted.")

    browser.close()
