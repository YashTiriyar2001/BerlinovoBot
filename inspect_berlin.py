from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

STATE_FIELD = "formly_29_select_berlinovo_bundesland_der_hochschule_0"
TYPE_FIELD = "formly_30_select_berlinovo_art_der_hochschule_berlin_0"
FH_NAME_FIELD = "formly_33_select_berlinovo_name_fachhochschule_berlin_0"

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
    print("HTW BERLIN UNIVERSITY INSPECTION")
    print("========================================")

    # ------------------------------------
    # STEP 1: Select Berlin
    # ------------------------------------

    print("\n1. Selecting university state: Berlin")

    state = page.locator(f'[id="{STATE_FIELD}"]')
    state.click()
    page.wait_for_timeout(500)

    options = page.locator('[role="option"]:visible')

    berlin = options.filter(
        has_text="Berlin"
    ).first

    print("Berlin option found:", berlin.count())

    berlin.click()

    page.wait_for_timeout(1000)

    # ------------------------------------
    # STEP 2: Select Fachhochschule
    # ------------------------------------

    print("\n2. Selecting university type: Fachhochschule")

    university_type = page.locator(
        f'[id="{TYPE_FIELD}"]'
    )

    print(
        "Fachhochschule field visible:",
        university_type.is_visible()
    )

    university_type.click()

    page.wait_for_timeout(500)

    options = page.locator('[role="option"]:visible')

    print("\nUniversity type options:")

    for i in range(options.count()):
        try:
            text = options.nth(i).inner_text().strip()

            if text:
                print(f"  OPTION {i}: {text}")

        except Exception:
            pass

    fh_option = options.filter(
        has_text="Fachhochschule"
    ).first

    print(
        "\nFachhochschule option found:",
        fh_option.count()
    )

    fh_option.click()

    page.wait_for_timeout(1500)

    # ------------------------------------
    # STEP 3: Inspect HTW/university list
    # ------------------------------------

    print("\n========================================")
    print("FACHHOCHSCHULE NAME FIELD")
    print("========================================")

    fh_name = page.locator(
        f'[id="{FH_NAME_FIELD}"]'
    )

    print(
        "Name field found:",
        fh_name.count()
    )

    print(
        "Name field visible:",
        fh_name.is_visible()
    )

    if fh_name.is_visible():

        print("\nClicking Fachhochschule name field...")

        fh_name.click()

        page.wait_for_timeout(700)

        options = page.locator(
            '[role="option"]:visible'
        )

        print(
            "\nVisible Fachhochschule options:",
            options.count()
        )

        for i in range(options.count()):

            try:
                text = options.nth(i).inner_text().strip()

                if text:
                    print(f"  OPTION {i}: {text}")

            except Exception:
                pass

    else:
        print(
            "\nThe Fachhochschule name field "
            "did not become visible."
        )

    print("\n========================================")
    print("INSPECTION COMPLETE")
    print("========================================")

    print("\nChrome will remain OPEN.")
    print("Close Chrome manually when finished.")

    while True:
        page.wait_for_timeout(60000)
