import os
import ast
import os
import json
from playwright.sync_api import sync_playwright


# Load config
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


# Get the first application URL
with open("application_links.txt", "r", encoding="utf-8") as f:
    first_line = next(line for line in f if line.strip())

parts = first_line.strip().split("\t")
APPLICATION_URL = parts[2]


# Load only the functions from final_bot.py.
# This does NOT execute the main bot.
with open("final_bot.py", "r", encoding="utf-8") as f:
    source = f.read()

tree = ast.parse(source)

functions = []

for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        functions.append(node)

module = ast.Module(body=functions, type_ignores=[])

namespace = {
    "CONFIG": CONFIG,
    "os": os
}

exec(
    compile(module, "final_bot.py", "exec"),
    namespace
)

field = namespace["field"]
fill_application = namespace["fill_application"]


with sync_playwright() as p:

    browser = p.chromium.launch(
        channel="chrome",
        headless=False
    )

    context = browser.new_context(
        viewport={"width": 1440, "height": 1000}
    )

    page = context.new_page()

    print()
    print("=" * 80)
    print("FORM DIAGNOSTIC")
    print("=" * 80)
    print()
    print("Opening:", APPLICATION_URL)

    page.goto(
        APPLICATION_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(2500)

    print("Page loaded.")
    print()
    print("Filling form...")
    print()

    fill_application(page)

    page.wait_for_timeout(1500)

    print()
    print("=" * 80)
    print("DROPDOWN / COMBOBOX VALUES")
    print("=" * 80)

    comboboxes = page.locator(
        'input[role="combobox"], [role="combobox"]'
    )

    print("Combobox count:", comboboxes.count())
    print()

for i in range(comboboxes.count()):
    try:
        element = comboboxes.nth(i)

        # ng-select keeps the real input value empty.
        # The selected option is displayed inside .ng-value-label.
        container = element.locator(
            "xpath=ancestor::*[contains(@class,'ng-select')][1]"
        )

        selected = container.locator(".ng-value-label")

        if selected.count() > 0:
            values = []

            for j in range(selected.count()):
                try:
                    text = selected.nth(j).inner_text().strip()
                    if text:
                        values.append(text)
                except Exception:
                    pass

            value = " | ".join(values)
        else:
            value = ""

        print(
            i,
            "| ID:", element.get_attribute("id"),
            "| SELECTED:", repr(value)
        )

    except Exception as e:
        print(i, "| ERROR:", e)

    print()
    print("=" * 80)
    print("RADIO BUTTONS")
    print("=" * 80)

    radios = page.locator('input[type="radio"]')

    print("Radio count:", radios.count())
    print()

    for i in range(radios.count()):
        try:
            radio = radios.nth(i)

            print(
                i,
                "|",
                "CHECKED:", radio.is_checked(),
                "|",
                "VALUE:", radio.get_attribute("value"),
                "|",
                "ID:", radio.get_attribute("id")
            )

        except Exception:
            pass


    print()
    print("=" * 80)
    print("CHECKBOXES")
    print("=" * 80)

    checkboxes = page.locator('input[type="checkbox"]')

    print("Checkbox count:", checkboxes.count())
    print()

    for i in range(checkboxes.count()):
        try:
            checkbox = checkboxes.nth(i)

            print(
                i,
                "|",
                "CHECKED:", checkbox.is_checked(),
                "|",
                "ID:", checkbox.get_attribute("id"),
                "|",
                "NAME:", checkbox.get_attribute("name")
            )

        except Exception:
            pass


    print()
    print("=" * 80)
    print("UPLOADED FILES")
    print("=" * 80)

    files = page.locator('input[type="file"]')

    print("File input count:", files.count())
    print()

    for i in range(files.count()):
        try:
            file_names = files.nth(i).evaluate(
                """el => Array.from(el.files).map(f => f.name)"""
            )

            print(i, "=>", file_names)

        except Exception as e:
            print(i, "=> ERROR:", e)


    print()
    print("=" * 80)
    print("REQUIRED / VISIBLE FIELD CHECK")
    print("=" * 80)

    important_ids = [
        "firstName",
        "lastName",
        "email",
        "formly_17_select_$$_salutation_$$_0",
        "formly_18_input_$$_first_name_$$_0",
        "formly_18_input_$$_last_name_$$_1",
        "formly_19_input_$$_date_of_birth_$$_0",
        "formly_20_input_$$_street_$$_0",
        "formly_20_input_$$_house_number_$$_1",
        "formly_21_input_$$_zip_code_$$_0",
        "formly_21_input_$$_city_$$_1",
        "formly_21_select_$$_country_$$_2",
        "formly_22_input_$$_email_$$_0",
        "formly_22_input_$$_mobile_number_$$_1",
        "formly_23_select_berlinovo_herkunft_0",
        "formly_24_select_$$_place_of_birth_$$_0",
        "formly_29_select_berlinovo_bundesland_der_hochschule_0",
        "formly_30_select_berlinovo_art_der_hochschule_berlin_0",
        "formly_33_select_berlinovo_name_fachhochschule_berlin_0",
        "formly_40_checkbox_$$_is_contract_partner_$$_0",
        "formly_7_input_berlinovo_gewuenschter_vertragsbeginn_0",
        "formly_8_input_berlinovo_gewuenschte_mietdauer_in_monaten_0",
        "formly_9_select_berlinovo_gewuenschte_wohnform_0",
        "formly_11_textarea_berlinovo_zusaetzliche_bemerkung_0",
        "formly_13_checkbox_berlinovo_bestaetigung_datenschutzhinweis_0",
    ]

    print()

    for field_id in important_ids:

        try:
            element = field(page, field_id)

            tag = element.evaluate("el => el.tagName")

            if tag == "INPUT" or tag == "TEXTAREA":
                value = element.input_value()
            else:
                value = element.inner_text()

            print(
                field_id,
                "=>",
                repr(value)
            )

        except Exception as e:
            print(
                field_id,
                "=> ERROR:",
                e
            )


    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()
    print("NO SUBMIT BUTTON WAS CLICKED.")
    print("The browser will remain open.")
    print()
    print("Close this browser manually when finished.")
