from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

STATE_FIELD = "formly_29_select_berlinovo_bundesland_der_hochschule_0"
TYPE_FIELD = "formly_30_select_berlinovo_art_der_hochschule_berlin_0"
FH_NAME_FIELD = "formly_33_select_berlinovo_name_fachhochschule_berlin_0"

REMAINING_FIELDS = [
    "formly_25_radio_berlinovo_gewuenschte_kommunikationssprache_0",
    "formly_28_radio_berlinovo_studienphase_0",
    "formly_7_input_berlinovo_gewuenschter_vertragsbeginn_0",
    "formly_8_input_berlinovo_gewuenschte_mietdauer_in_monaten_0",
    "formly_9_select_berlinovo_gewuenschte_wohnform_0",
    "formly_10_radio_berlinovo_barrierefreies_apartment_benoetigt_0",
    "formly_11_textarea_berlinovo_zusaetzliche_bemerkung_0",
    "formly_13_checkbox_berlinovo_bestaetigung_datenschutzhinweis_0",
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

    # ==========================================
    # SELECT BERLIN
    # ==========================================

    print("\nSelecting Berlin...")

    state = page.locator(f'[id="{STATE_FIELD}"]')
    state.click()
    page.wait_for_timeout(500)

    page.locator('[role="option"]:visible').filter(
        has_text="Berlin"
    ).first.click()

    page.wait_for_timeout(1000)

    # ==========================================
    # SELECT FACHHOCHSCHULE
    # ==========================================

    print("Selecting Fachhochschule...")

    university_type = page.locator(
        f'[id="{TYPE_FIELD}"]'
    )

    university_type.click()
    page.wait_for_timeout(500)

    page.locator('[role="option"]:visible').filter(
        has_text="Fachhochschule"
    ).first.click()

    page.wait_for_timeout(1000)

    # ==========================================
    # SELECT HTW BERLIN
    # ==========================================

    print("Selecting HTW Berlin...")

    htw = page.locator(
        f'[id="{FH_NAME_FIELD}"]'
    )

    htw.click()
    page.wait_for_timeout(500)

    htw_option = page.locator(
        '[role="option"]:visible'
    ).filter(
        has_text="Hochschule für Technik und Wirtschaft Berlin (HTW)"
    ).first

    print(
        "HTW option found:",
        htw_option.count()
    )

    htw_option.click()

    page.wait_for_timeout(1500)

    # ==========================================
    # INSPECT REMAINING FIELDS
    # ==========================================

    print("\n========================================")
    print("REMAINING FIELD INSPECTION")
    print("========================================")

    for field_id in REMAINING_FIELDS:

        print("\n----------------------------------------")
        print("FIELD:", field_id)
        print("----------------------------------------")

        locator = page.locator(
            f'[id="{field_id}"]'
        )

        if locator.count() == 0:
            print("NOT FOUND")
            continue

        count = locator.count()

        print("Elements found:", count)

        for i in range(count):

            element = locator.nth(i)

            print(f"\n  ELEMENT {i}")

            try:
                print(
                    "  Tag:",
                    element.evaluate(
                        "(el) => el.tagName"
                    )
                )
            except Exception:
                pass

            try:
                print(
                    "  Type:",
                    element.get_attribute("type")
                )
            except Exception:
                pass

            try:
                print(
                    "  Value:",
                    element.input_value()
                )
            except Exception:
                pass

            try:
                print(
                    "  Visible:",
                    element.is_visible()
                )
            except Exception:
                pass

            try:
                print(
                    "  Checked:",
                    element.is_checked()
                )
            except Exception:
                pass

            try:
                print(
                    "  Placeholder:",
                    element.get_attribute(
                        "placeholder"
                    )
                )
            except Exception:
                pass

    # ==========================================
    # RADIO OPTIONS
    # ==========================================

    print("\n========================================")
    print("RADIO OPTIONS")
    print("========================================")

    radio_names = [
        "formly_25_radio_berlinovo_gewuenschte_kommunikationssprache_0",
        "formly_28_radio_berlinovo_studienphase_0",
        "formly_10_radio_berlinovo_barrierefreies_apartment_benoetigt_0",
    ]

    for name in radio_names:

        print("\n----------------------------------------")
        print("RADIO GROUP:", name)
        print("----------------------------------------")

        radios = page.locator(
            f'input[type="radio"][name="{name}"]'
        )

        print("Radio count:", radios.count())

        for i in range(radios.count()):

            radio = radios.nth(i)

            print(
                f"  RADIO {i}:",
                "id=",
                radio.get_attribute("id"),
                "| value=",
                radio.get_attribute("value"),
                "| visible=",
                radio.is_visible()
            )

    # ==========================================
    # FILE UPLOADS
    # ==========================================

    print("\n========================================")
    print("FILE UPLOAD INSPECTION")
    print("========================================")

    uploads = page.locator(
        'input[type="file"]'
    )

    print(
        "Number of file inputs:",
        uploads.count()
    )

    for i in range(uploads.count()):

        upload = uploads.nth(i)

        print("\n----------------------------------------")
        print("FILE INPUT:", i)
        print("----------------------------------------")

        print(
            "Visible:",
            upload.is_visible()
        )

        print(
            "Accept:",
            upload.get_attribute("accept")
        )

        print(
            "Multiple:",
            upload.get_attribute("multiple")
        )

        try:
            parent_text = upload.locator(
                "xpath=.."
            ).inner_text()

            print("\nParent text:")
            print(parent_text[:2000])

        except Exception:
            print(
                "Could not read parent text"
            )

    # ==========================================
    # BUTTONS
    # ==========================================

    print("\n========================================")
    print("BUTTON INSPECTION")
    print("========================================")

    buttons = page.locator("button:visible")

    for i in range(buttons.count()):

        button = buttons.nth(i)

        try:
            text = button.inner_text().strip()
        except Exception:
            text = ""

        print(
            f"BUTTON {i}:",
            repr(text),
            "| type=",
            button.get_attribute("type")
        )

    print("\n========================================")
    print("INSPECTION COMPLETE")
    print("========================================")

    print("Chrome will remain OPEN.")
    print("Do not submit the application.")

    while True:
        page.wait_for_timeout(60000)
