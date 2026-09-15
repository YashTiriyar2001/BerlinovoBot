import json
from pathlib import Path
from playwright.sync_api import sync_playwright

APPLICATION_URL = "https://app.wohnungshelden.de/public/listings/1230%2F2386/application?c=6cd678f5-036a-44fa-970f-65224c4d4506"

with open("config.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def field(page, field_id):
    return page.locator(f'[id="{field_id}"]')


def select_option(page, field_id, text):
    el = field(page, field_id)
    el.click()
    page.wait_for_timeout(500)

    option = page.locator('[role="option"]').filter(has_text=text).last
    option.click()
    page.wait_for_timeout(500)


def check_radio_by_text(page, text):
    radio = page.locator('input[type="radio"]')
    mapping = {"English": 1, "Master": 3, "No": 5}
    if text not in mapping:
        raise ValueError(f"Unknown radio option: {text}")
    radio.nth(mapping[text]).check()
    page.wait_for_timeout(500)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    print("Opening application...")
    page.goto(APPLICATION_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)

    # Top-level contact information
    field(page, "firstName").fill(data["first_name"])
    field(page, "lastName").fill(data["last_name"])
    field(page, "email").fill(data["email"])

    # Personal information
    select_option(
        page,
        'formly_17_select_$$_salutation_$$_0',
        data["salutation"]
    )

    field(page, 'formly_18_input_$$_first_name_$$_0').fill(data["first_name"])
    field(page, 'formly_18_input_$$_last_name_$$_1').fill(data["last_name"])
    field(page, 'formly_19_input_$$_date_of_birth_$$_0').fill(data["date_of_birth"])
    field(page, 'formly_20_input_$$_street_$$_0').fill(data["street"])
    field(page, 'formly_20_input_$$_house_number_$$_1').fill(data["house_number"])
    field(page, 'formly_21_input_$$_zip_code_$$_0').fill(data["postal_code"])
    field(page, 'formly_21_input_$$_city_$$_1').fill(data["city"])

    select_option(
        page,
        'formly_21_select_$$_country_$$_2',
        data["country"]
    )

    field(page, 'formly_22_input_$$_email_$$_0').fill(data["email"])
    field(page, 'formly_22_input_$$_mobile_number_$$_1').fill(data["mobile"])

    select_option(
        page,
        'formly_23_select_berlinovo_herkunft_0',
        data["student_from"]
    )

    select_option(
        page,
        'formly_24_select_$$_place_of_birth_$$_0',
        data["nationality"]
    )

    # Communication language
    check_radio_by_text(page, data["communication_language"])

    # Study level
    check_radio_by_text(page, data["study_level"])

    # State
    select_option(
        page,
        'formly_29_select_berlinovo_bundesland_der_hochschule_0',
        data["study_state"]
    )

    # University type
    select_option(
        page,
        'formly_30_select_berlinovo_art_der_hochschule_berlin_0',
        data["university_type"]
    )

    # University
    select_option(
        page,
        'formly_33_select_berlinovo_name_fachhochschule_berlin_0',
        data["university"]
    )

    # Contract partner confirmation
    contract_checkbox = field(
        page,
        'formly_40_checkbox_$$_is_contract_partner_$$_0'
    )

    if data["contract_partner"] and not contract_checkbox.is_checked():
        contract_checkbox.check()

    # Housing details
    field(
        page,
        'formly_7_input_berlinovo_gewuenschter_vertragsbeginn_0'
    ).fill(data["contract_start"])

    field(
        page,
        'formly_8_input_berlinovo_gewuenschte_mietdauer_in_monaten_0'
    ).fill(str(data["rental_months"]))

    select_option(
        page,
        'formly_9_select_berlinovo_gewuenschte_wohnform_0',
        data["housing_type"]
    )

    # Accessible apartment
    check_radio_by_text(page, data["accessible"])

    # Additional note
    field(
        page,
        'formly_11_textarea_berlinovo_zusaetzliche_bemerkung_0'
    ).fill(data["additional_note"])

    # Privacy consent
    privacy_checkbox = field(
        page,
        'formly_13_checkbox_berlinovo_bestaetigung_datenschutzhinweis_0'
    )

    if data["privacy_consent"] and not privacy_checkbox.is_checked():
        privacy_checkbox.check()

    # Upload documents.
    # The three file inputs correspond to:
    # 1. Enrollment
    # 2. Passport
    # 3. Income/guarantee
    files = [
        data["enrollment_document"],
        data["passport_document"],
        data["income_document"]
    ]

    file_inputs = page.locator('input[type="file"]')

    print(f"Found {file_inputs.count()} file inputs.")

    if file_inputs.count() < 3:
        raise RuntimeError("Could not find all three document upload fields.")

    for i, filepath in enumerate(files):
        if not Path(filepath).is_file():
            raise FileNotFoundError(filepath)

        print(f"Uploading document {i + 1}: {Path(filepath).name}")
        file_inputs.nth(i).set_input_files(filepath)
        page.wait_for_timeout(1000)

    # Check for a visible CAPTCHA before submission.
    captcha = page.locator('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"], .g-recaptcha')
    visible_captcha = False
    for n in range(captcha.count()):
        try:
            box = captcha.nth(n).bounding_box()
            if box and box['width'] > 20 and box['height'] > 20:
                visible_captcha = True
                break
        except Exception:
            pass
    if visible_captcha:
        page.screenshot(path="captcha_detected.png", full_page=True)
        print("VISIBLE CAPTCHA DETECTED - NOT SUBMITTING.")
        print("Screenshot saved as: captcha_detected.png")
        input("Press ENTER after handling the CAPTCHA manually...")

    print("Submitting application...")
    submit_button = page.locator("button[type=submit]").first
    submit_button.click()
    page.wait_for_timeout(7000)

    result_url = page.url
    result_title = page.title()
    result_text = page.locator("body").inner_text()

    with open("submission_result.txt", "w", encoding="utf-8") as f:
        f.write("URL: " + result_url + "\n")
        f.write("TITLE: " + result_title + "\n\n")
        f.write(result_text)

    page.screenshot(path="submission_result.png", full_page=True)

    print()
    print("==========================================")
    print("SUBMISSION FINISHED")
    print("==========================================")
    print("Result URL:", result_url)
    print("Result title:", result_title)
    print("Saved: submission_result.txt")
    print("Saved: submission_result.png")
    print("==========================================")

    input("Press ENTER to close this application page...")
    page.close()
    browser.close()
