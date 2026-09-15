import re
from playwright.sync_api import sync_playwright

MAX_RENT = 600.0

EXCLUDED_TITLE = (
    "Studierendenwohnen Iranische Straße – Einzelapartment Typ 2"
)

INPUT_FILE = "application_links.txt"
OUTPUT_FILE = "application_links_filtered.txt"


def extract_rent(text):
    """
    Extract Berlinovo's monthly inclusive rent.

    Handles:
    - normal spaces
    - line breaks
    - non-breaking spaces
    - German decimal formatting
    - € before or after the amount
    """

    import re

    # Normalize whitespace.
    normalized = text.replace("\xa0", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    patterns = [
        # Inklusivmiete mtl. ab 510,00 €
        r"Inklusivmiete\s*mtl\.?\s*ab\s*[:\-]?\s*"
        r"€?\s*([\d.]+(?:,\d{1,2})?)\s*€?",

        # Inklusivmiete monatlich ab 510,00 €
        r"Inklusivmiete\s*monatlich\s*ab\s*[:\-]?\s*"
        r"€?\s*([\d.]+(?:,\d{1,2})?)\s*€?",

        # Warmmiete / Gesamtmiete variants
        r"(?:Warmmiete|Gesamtmiete)\s*"
        r"(?:mtl\.?|monatlich)?\s*ab?\s*[:\-]?\s*"
        r"€?\s*([\d.]+(?:,\d{1,2})?)\s*€?",

        # Miete mtl. ab 510 €
        r"Miete\s*mtl\.?\s*ab\s*[:\-]?\s*"
        r"€?\s*([\d.]+(?:,\d{1,2})?)\s*€?",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        if match:

            value = match.group(1)

            # German number format:
            # 510,00 -> 510.00
            # 1.250,00 -> 1250.00
            if "," in value:

                value = value.replace(
                    ".",
                    "",
                )

                value = value.replace(
                    ",",
                    ".",
                )

            else:

                # If there is a dot but it looks like
                # a thousands separator, remove it.
                if re.match(
                    r"^\d{1,3}\.\d{3}$",
                    value,
                ):
                    value = value.replace(
                        ".",
                        "",
                    )

            try:
                return float(value)

            except ValueError:
                pass

    return None

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
) as f:

    applications = []

    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split("\t")

        if len(parts) >= 3:
            applications.append(parts)


print()
print("=" * 80)
print("BERLINOVO RENT FILTER")
print("=" * 80)
print(f"APPLICATIONS BEFORE FILTER: {len(applications)}")
print(f"MAXIMUM RENT: €{MAX_RENT:.2f}")
print("=" * 80)
print()


kept = []
skipped = []


with sync_playwright() as p:

    browser = p.chromium.launch(
        channel="chrome",
        headless=False,
    )

    page = browser.new_page(
        viewport={
            "width": 1440,
            "height": 1000,
        }
    )

    for number, parts in enumerate(
        applications,
        1,
    ):

        listing_url = parts[0]
        title = parts[1]

        print(
            f"[{number}/{len(applications)}] "
            f"{title}"
        )

        # Explicit exclusion.
        if (
            title.strip()
            == EXCLUDED_TITLE
        ):
            print(
                "  SKIP: Explicitly excluded apartment"
            )

            skipped.append(
                (
                    title,
                    listing_url,
                    "Explicitly excluded",
                )
            )

            continue

        try:

            page.goto(
                listing_url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            page.wait_for_timeout(1500)

            text = page.locator(
                "body"
            ).inner_text()

            rent = extract_rent(text)

            if rent is None:

                print(
                    "  WARNING: Could not determine rent."
                )

                print(
                    "  Keeping apartment for manual review."
                )

                kept.append(parts)

                continue

            print(
                f"  Rent: €{rent:.2f}"
            )

            if rent > MAX_RENT:

                print(
                    f"  SKIP: Rent exceeds €{MAX_RENT:.0f}"
                )

                skipped.append(
                    (
                        title,
                        listing_url,
                        f"Rent €{rent:.2f} > €{MAX_RENT:.2f}",
                    )
                )

            else:

                print("  KEEP")

                kept.append(parts)

        except Exception as e:

            print(
                f"  WARNING: Could not check listing: {e}"
            )

            print(
                "  Keeping apartment for manual review."
            )

            kept.append(parts)

    browser.close()


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as f:

    for parts in kept:
        f.write(
            "\t".join(parts)
            + "\n"
        )


print()
print("=" * 80)
print("FILTER COMPLETE")
print("=" * 80)
print(
    f"KEPT: {len(kept)}"
)
print(
    f"SKIPPED: {len(skipped)}"
)
print("=" * 80)

print()
print("SKIPPED APARTMENTS:")

for title, url, reason in skipped:

    print()
    print(
        f"SKIP: {title}"
    )

    print(
        f"REASON: {reason}"
    )

print()
print(
    f"Filtered file created: {OUTPUT_FILE}"
)
print()
