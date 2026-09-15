from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

DROPDOWN_IDS = [
    "formly_17_select_$$_salutation_$$_0",
    "formly_21_select_$$_country_$$_2",
    "formly_23_select_berlinovo_herkunft_0",
    "formly_24_select_$$_place_of_birth_$$_0",
    "formly_29_select_berlinovo_bundesland_der_hochschule_0",
    "formly_30_select_berlinovo_art_der_hochschule_berlin_0",
    "formly_31_select_berlinovo_art_der_hochschule_brandenburg_0",
    "formly_32_select_berlinovo_name_universitaet_berlin_0",
    "formly_33_select_berlinovo_name_fachhochschule_berlin_0",
    "formly_34_select_berlinovo_name_konfessionelle_hochschule_berlin_0",
    "formly_35_select_berlinovo_name_private_hochschule_berlin_0",
    "formly_36_select_berlinovo_name_dependance_berlin_0",
    "formly_37_select_berlinovo_name_universitaet_brandenburg_0",
    "formly_38_select_berlinovo_name_fachhochschule_brandenburg_0",
    "formly_39_select_berlinovo_name_private_hochschule_brandenburg_0",
    "formly_9_select_berlinovo_gewuenschte_wohnform_0"
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=100
    )

    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}
    )

    print("Opening Wohnungshelden...")
    page.goto(
        APPLICATION_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    print("\n========================================")
    print("DROPDOWN INSPECTION")
    print("========================================")

    for field_id in DROPDOWN_IDS:

        print("\n----------------------------------------")
        print("FIELD:", field_id)
        print("----------------------------------------")

        locator = page.locator(f'[id="{field_id}"]')

        if locator.count() == 0:
            print("NOT FOUND")
            continue

        element = locator.first

        if not element.is_visible():
            print("NOT VISIBLE - SKIPPING")
            continue

        try:
            print("Value:", element.input_value())
        except Exception:
            print("Value: <unavailable>")

        try:
            print("Tag:", element.evaluate("(el) => el.tagName"))
        except Exception:
            pass

        try:
            print("Class:", element.get_attribute("class"))
        except Exception:
            pass

        try:
            print("Role:", element.get_attribute("role"))
        except Exception:
            pass

        try:
            print("ARIA expanded:", element.get_attribute("aria-expanded"))
        except Exception:
            pass

        try:
            parent_text = element.locator("xpath=..").inner_text()
            print("\nParent text:")
            print(parent_text[:1500])
        except Exception:
            print("Parent text unavailable")

        print("\nClicking field...")

        try:
            element.click()
            page.wait_for_timeout(700)

            options = page.locator('[role="option"]:visible')

            print(
                f"Visible role=option elements: {options.count()}"
            )

            for i in range(options.count()):
                try:
                    text = options.nth(i).inner_text().strip()

                    if text:
                        print(f"  OPTION {i}: {text}")
                except Exception:
                    pass

            # Also inspect visible list items
            items = page.locator("li:visible")

            print(
                f"Visible LI elements: {items.count()}"
            )

            shown = 0

            for i in range(items.count()):

                if shown >= 30:
                    break

                try:
                    text = items.nth(i).inner_text().strip()

                    if text:
                        print(f"  LI {i}: {text}")
                        shown += 1

                except Exception:
                    pass

            # Press Escape so the next dropdown starts closed
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        except Exception as e:
            print("Could not click:", e)

    print("\n========================================")
    print("DONE")
    print("========================================")
    print("Chrome will remain OPEN.")
    print("Close Chrome manually when finished inspecting.")

    while True:
        page.wait_for_timeout(60000)
