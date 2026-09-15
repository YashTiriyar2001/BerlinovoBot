from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

with open("all_listings.txt", "r", encoding="utf-8") as f:
    LISTINGS = [line.strip() for line in f if line.strip()]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    results = []

    for number, url in enumerate(LISTINGS, 1):
        print()
        print("=" * 80)
        print(f"LISTING {number} OF {len(LISTINGS)}")
        print("=" * 80)
        print(url)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)

            title = page.title()
            print("TITLE:", title)

            links = page.locator("a[href]")
            found = []

            for i in range(links.count()):
                link = links.nth(i)

                try:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip()

                    if not href:
                        continue

                    href_lower = href.lower()
                    text_lower = text.lower()

                    if (
                        "wohnungshelden" in href_lower
                        or "mietanfrage" in text_lower
                        or "anfrage" in text_lower
                    ):
                        full_url = urljoin(url, href)

                        if full_url not in [x["href"] for x in found]:
                            found.append({
                                "text": text,
                                "href": full_url
                            })

                except Exception:
                    pass

            if found:
                print("APPLICATION LINK(S):")

                for item in found:
                    print(" TEXT:", item["text"])
                    print(" HREF:", item["href"])

                    results.append({
                        "listing": url,
                        "title": title,
                        "text": item["text"],
                        "href": item["href"]
                    })
            else:
                print("NO APPLICATION LINK FOUND")

        except Exception as e:
            print("ERROR:", e)

    print()
    print("=" * 80)
    print("FINAL APPLICATION-LINK SUMMARY")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   LISTING: {result['listing']}")
        print(f"   APPLICATION: {result['href']}")
        print()

    print(f"APPLICATION LINKS FOUND: {len(results)}")

    with open("application_links.txt", "w", encoding="utf-8") as f:
        for result in results:
            f.write(
                result["listing"] + "\t" +
                result["title"] + "\t" +
                result["href"] + "\n"
            )

    print("Saved: application_links.txt")
    print()
    print("No applications were submitted.")

    browser.close()
