from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=100
    )

    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}
    )

    print("Opening application...")

    page.goto(
        APPLICATION_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    print("\nPAGE TITLE:")
    print(page.title())

    print("\nPAGE URL:")
    print(page.url)

    print("\nINPUT FIELDS:")

    inputs = page.locator("input")

    for i in range(inputs.count()):
        el = inputs.nth(i)

        print(
            f"INPUT {i}: "
            f"type={el.get_attribute('type')}, "
            f"name={el.get_attribute('name')}, "
            f"id={el.get_attribute('id')}, "
            f"placeholder={el.get_attribute('placeholder')}, "
            f"aria-label={el.get_attribute('aria-label')}"
        )

    print("\nTEXTAREAS:")

    textareas = page.locator("textarea")

    for i in range(textareas.count()):
        el = textareas.nth(i)

        print(
            f"TEXTAREA {i}: "
            f"name={el.get_attribute('name')}, "
            f"id={el.get_attribute('id')}, "
            f"placeholder={el.get_attribute('placeholder')}"
        )

    print("\nSELECTS:")

    selects = page.locator("select")

    for i in range(selects.count()):
        el = selects.nth(i)

        print(
            f"SELECT {i}: "
            f"name={el.get_attribute('name')}, "
            f"id={el.get_attribute('id')}"
        )

    print("\nFILE UPLOADS:")

    files = page.locator('input[type="file"]')

    for i in range(files.count()):
        el = files.nth(i)

        print(
            f"FILE {i}: "
            f"name={el.get_attribute('name')}, "
            f"id={el.get_attribute('id')}, "
            f"accept={el.get_attribute('accept')}, "
            f"multiple={el.get_attribute('multiple')}"
        )

    print("\nBUTTONS:")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        el = buttons.nth(i)

        try:
            text = el.inner_text().strip()
        except Exception:
            text = ""

        print(
            f"BUTTON {i}: "
            f"text={repr(text)}, "
            f"type={el.get_attribute('type')}, "
            f"id={el.get_attribute('id')}, "
            f"name={el.get_attribute('name')}"
        )

    print("\nCHECKBOXES / RADIOS:")

    controls = page.locator(
        'input[type="checkbox"], input[type="radio"]'
    )

    for i in range(controls.count()):
        el = controls.nth(i)

        print(
            f"CONTROL {i}: "
            f"type={el.get_attribute('type')}, "
            f"name={el.get_attribute('name')}, "
            f"id={el.get_attribute('id')}, "
            f"value={el.get_attribute('value')}"
        )

    page.screenshot(
        path="results/screenshots/form_inspection.png",
        full_page=True
    )

    print("\n================================")
    print("INSPECTION COMPLETE")
    print("Chrome will remain OPEN.")
    print("================================")

    while True:
        page.wait_for_timeout(60000)
