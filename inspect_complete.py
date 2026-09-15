from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"


def clean(text):
    if not text:
        return ""
    return " ".join(text.split())


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
    print("COMPLETE FORM INSPECTION")
    print("========================================")

    # ==========================================================
    # ALL FORM CONTROLS
    # ==========================================================

    controls = page.locator(
        "input, textarea, select"
    )

    print("\nTOTAL FORM CONTROLS:", controls.count())

    for i in range(controls.count()):

        element = controls.nth(i)

        print("\n----------------------------------------")
        print(f"CONTROL {i}")
        print("----------------------------------------")

        try:
            tag = element.evaluate(
                "(el) => el.tagName"
            )
        except Exception:
            tag = ""

        print("Tag:", tag)

        for attr in [
            "type",
            "id",
            "name",
            "placeholder",
            "autocomplete",
            "role",
            "aria-label",
            "aria-required",
            "required",
            "readonly",
            "disabled",
            "accept",
            "multiple"
        ]:
            try:
                value = element.get_attribute(attr)

                if value is not None:
                    print(f"{attr}: {value}")

            except Exception:
                pass

        try:
            print(
                "Visible:",
                element.is_visible()
            )
        except Exception:
            pass

        try:
            print(
                "Enabled:",
                element.is_enabled()
            )
        except Exception:
            pass

        try:
            if tag == "INPUT":
                input_type = element.get_attribute("type")

                if input_type in [
                    "checkbox",
                    "radio"
                ]:
                    print(
                        "Checked:",
                        element.is_checked()
                    )
                else:
                    print(
                        "Value:",
                        element.input_value()
                    )

            elif tag == "TEXTAREA":
                print(
                    "Value:",
                    element.input_value()
                )

        except Exception:
            pass

        # ------------------------------------------------------
        # Look for associated <label>
        # ------------------------------------------------------

        try:
            element_id = element.get_attribute("id")

            if element_id:

                label = page.locator(
                    f'label[for="{element_id}"]'
                )

                if label.count() > 0:
                    print(
                        "LABEL:",
                        clean(label.first.inner_text())
                    )

        except Exception:
            pass

        # ------------------------------------------------------
        # Parent / surrounding text
        # ------------------------------------------------------

        try:

            parent = element.locator(
                "xpath=.."
            )

            parent_text = clean(
                parent.inner_text()
            )

            if parent_text:
                print(
                    "PARENT TEXT:",
                    parent_text[:1000]
                )

        except Exception:
            pass

        # ------------------------------------------------------
        # Grandparent text
        # ------------------------------------------------------

        try:

            grandparent = element.locator(
                "xpath=../.."
            )

            text = clean(
                grandparent.inner_text()
            )

            if text:
                print(
                    "SURROUNDING TEXT:",
                    text[:1500]
                )

        except Exception:
            pass


    # ==========================================================
    # FIELDSETS
    # ==========================================================

    print("\n\n========================================")
    print("FIELDSETS / RADIO GROUPS")
    print("========================================")

    fieldsets = page.locator(
        "fieldset"
    )

    print(
        "Total fieldsets:",
        fieldsets.count()
    )

    for i in range(fieldsets.count()):

        fieldset = fieldsets.nth(i)

        print("\n----------------------------------------")
        print(f"FIELDSET {i}")
        print("----------------------------------------")

        try:
            print(
                "Visible:",
                fieldset.is_visible()
            )
        except Exception:
            pass

        try:
            text = clean(
                fieldset.inner_text()
            )

            print(
                "TEXT:",
                text[:2000]
            )

        except Exception:
            pass

        try:

            radios = fieldset.locator(
                'input[type="radio"]'
            )

            print(
                "Radio buttons:",
                radios.count()
            )

            for j in range(radios.count()):

                radio = radios.nth(j)

                print(
                    f"  RADIO {j}:",
                    "id=",
                    radio.get_attribute("id"),
                    "| checked=",
                    radio.is_checked(),
                    "| visible=",
                    radio.is_visible()
                )

        except Exception:
            pass


    # ==========================================================
    # DROPDOWNS / COMBOBOXES
    # ==========================================================

    print("\n\n========================================")
    print("ALL COMBOBOXES")
    print("========================================")

    combos = page.locator(
        '[role="combobox"]'
    )

    print(
        "Total comboboxes:",
        combos.count()
    )

    for i in range(combos.count()):

        combo = combos.nth(i)

        print("\n----------------------------------------")
        print(f"COMBOBOX {i}")
        print("----------------------------------------")

        print(
            "ID:",
            combo.get_attribute("id")
        )

        print(
            "Visible:",
            combo.is_visible()
        )

        try:
            print(
                "Value:",
                combo.input_value()
            )
        except Exception:
            pass

        print(
            "ARIA expanded:",
            combo.get_attribute(
                "aria-expanded"
            )
        )


    # ==========================================================
    # FILE UPLOADS
    # ==========================================================

    print("\n\n========================================")
    print("FILE UPLOADS")
    print("========================================")

    files = page.locator(
        'input[type="file"]'
    )

    print(
        "Total file inputs:",
        files.count()
    )

    for i in range(files.count()):

        file_input = files.nth(i)

        print("\n----------------------------------------")
        print(f"FILE INPUT {i}")
        print("----------------------------------------")

        print(
            "Visible:",
            file_input.is_visible()
        )

        print(
            "ID:",
            file_input.get_attribute("id")
        )

        print(
            "Name:",
            file_input.get_attribute("name")
        )

        print(
            "Accept:",
            file_input.get_attribute("accept")
        )

        print(
            "Multiple:",
            file_input.get_attribute("multiple")
        )

        # Nearby text
        try:

            parent = file_input.locator(
                "xpath=.."
            )

            print(
                "PARENT TEXT:",
                clean(parent.inner_text())[:2000]
            )

        except Exception:
            pass

        try:

            grandparent = file_input.locator(
                "xpath=../.."
            )

            print(
                "SURROUNDING TEXT:",
                clean(
                    grandparent.inner_text()
                )[:3000]
            )

        except Exception:
            pass


    # ==========================================================
    # BUTTONS
    # ==========================================================

    print("\n\n========================================")
    print("ALL BUTTONS")
    print("========================================")

    buttons = page.locator(
        "button"
    )

    print(
        "Total buttons:",
        buttons.count()
    )

    for i in range(buttons.count()):

        button = buttons.nth(i)

        try:
            text = clean(
                button.inner_text()
            )
        except Exception:
            text = ""

        print(
            f"BUTTON {i}:",
            repr(text)
        )

        print(
            "  Type:",
            button.get_attribute("type")
        )

        print(
            "  ID:",
            button.get_attribute("id")
        )

        print(
            "  Visible:",
            button.is_visible()
        )


    # ==========================================================
    # PAGE TEXT
    # ==========================================================

    print("\n\n========================================")
    print("FORM PAGE TEXT")
    print("========================================")

    try:

        body_text = clean(
            page.locator("body").inner_text()
        )

        print(
            body_text[:15000]
        )

    except Exception as e:

        print(
            "Could not read page text:",
            e
        )


    # ==========================================================
    # FINISHED
    # ==========================================================

    print("\n\n========================================")
    print("COMPLETE INSPECTION FINISHED")
    print("========================================")

    print(
        "IMPORTANT: Nothing was submitted."
    )

    print(
        "Chrome will remain OPEN."
    )

    print(
        "Close Chrome manually when finished."
    )

    while True:
        page.wait_for_timeout(60000)
