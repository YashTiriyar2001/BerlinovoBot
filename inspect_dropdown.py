from playwright.sync_api import sync_playwright

URL = "https://app.wohnungshelden.de/public/listings/1230%2F2388%2FTypII/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="chrome"
    )

    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    field_id = "formly_17_select_$$_salutation_$$_0"
    combo = page.locator(f'[id="{field_id}"]')

    print("\n" + "=" * 80)
    print("BEFORE SELECTION")
    print("=" * 80)

    print("Input value:", repr(combo.input_value()))
    print("Outer HTML:")
    print(combo.evaluate("(el) => el.outerHTML"))

    print("\nClicking dropdown...")
    combo.click()
    page.wait_for_timeout(500)

    options = page.locator('[role="option"]:visible')

    print("\nOptions found:", options.count())

    for i in range(options.count()):
        print(
            i,
            repr(options.nth(i).inner_text()),
            options.nth(i).evaluate("(el) => el.outerHTML")
        )

    print("\nClicking Herr (Mr)...")

    for i in range(options.count()):
        if options.nth(i).inner_text().strip() == "Herr (Mr)":
            options.nth(i).click()
            break

    page.wait_for_timeout(1500)

    print("\n" + "=" * 80)
    print("AFTER SELECTION")
    print("=" * 80)

    print("Input value:", repr(combo.input_value()))
    print("Aria-expanded:", combo.get_attribute("aria-expanded"))
    print("Aria-activedescendant:", combo.get_attribute("aria-activedescendant"))

    print("\nInput outer HTML:")
    print(combo.evaluate("(el) => el.outerHTML"))

    print("\nParent outer HTML:")
    print(
        combo.evaluate(
            "(el) => el.parentElement.parentElement.outerHTML"
        )
    )

    print("\nVisible text around dropdown:")

    parent = combo.locator("xpath=..")

    try:
        print(parent.inner_text())
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)

    input("\nPress ENTER to close browser...")

    browser.close()
