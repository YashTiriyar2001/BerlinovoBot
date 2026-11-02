import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURATION
# ============================================================

BERLINOVO_LISTINGS_URL = (
    "https://www.berlinovo.de/de/apartments/suche"
    "?a%5B0%5D=apartments_angebot%3AS"
    "&a%5B1%5D=keine_apartments_verfuegbar%3A0"
)


# ============================================================
# LOAD CONFIGURATION
# ============================================================

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


with open("application_links.txt", "r", encoding="utf-8") as f:
    APPLICATIONS = []

    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split("\t")

        if len(parts) >= 3:
            APPLICATIONS.append(
                {
                    "listing": parts[0],
                    "title": parts[1],
                    "application": parts[2],
                }
            )


# ============================================================
# BASIC HELPERS
# ============================================================

def field(page, field_id):
    return page.locator(f'[id="{field_id}"]')


def fill_field(page, field_id, value):
    locator = field(page, field_id)
    locator.wait_for(state="visible", timeout=2000)
    locator.fill(str(value))

    if locator.count() == 0:
        raise Exception(f"Field not found: {field_id}")

    locator.fill(str(value))


# ============================================================
# BERLINOVO CUSTOM DROPDOWN
# ============================================================

def select_custom_combobox(page, field_id, option_text):
    """
    Berlinovo uses Angular ng-select.

    IMPORTANT:
    The underlying input keeps VALUE="" even after selection.

    The actual selected value appears as:

        <span class="ng-value-label">...</span>

    Therefore we click the actual role=option and verify
    .ng-value-label instead of input_value().
    """

    combo = page.locator(f'[id="{field_id}"]')

    if combo.count() == 0:
        raise Exception(f"Combobox not found: {field_id}")

    print(f"Selecting '{option_text}'...")

    # Open dropdown.
    combo.click()
    page.wait_for_timeout(500)

    # Berlinovo's ng-select options use role="option".
    options = page.locator('[role="option"]:visible')

    if options.count() == 0:
        raise Exception(
            f"No visible options found for combobox: {field_id}"
        )

    matching_option = None

    for i in range(options.count()):
        try:
            option = options.nth(i)
            text = option.inner_text().strip()

            # Examples:
            # Herr -> Herr (Mr)
            # Indien -> Indien (India)
            # Keine Präferenz -> Keine Präferenz (No Preference)
            #
            # Exact match OR text beginning with requested value.
            if text == option_text:
                matching_option = option
                break

            if text.startswith(option_text + " "):
                matching_option = option
                break

            if text.startswith(option_text + "("):
                matching_option = option
                break

        except Exception:
            pass

    if matching_option is None:
        available = []

        for i in range(options.count()):
            try:
                available.append(
                    options.nth(i).inner_text().strip()
                )
            except Exception:
                pass

        raise Exception(
            f"Option '{option_text}' not found for {field_id}. "
            f"Available visible options: {available}"
        )

    # Click actual option.
    matching_option.click()

    # Give Angular/ng-select time to update.
    page.wait_for_timeout(800)

    # Verify the selected display value.
    #
    # We find the nearest ng-select container from the input.
    ng_select = combo.locator(
        "xpath=ancestor::*[contains(@class,'ng-select')][1]"
    )

    selected_labels = ng_select.locator(".ng-value-label")

    selected_texts = []

    for i in range(selected_labels.count()):
        try:
            text = selected_labels.nth(i).inner_text().strip()

            if text:
                selected_texts.append(text)

        except Exception:
            pass

    selected_display = " | ".join(selected_texts)

    if not selected_texts:
        raise Exception(
            f"Dropdown selection did not register for {field_id}. "
            f"Expected '{option_text}', but no .ng-value-label exists."
        )

    # Check requested value against selected display.
    matched = False

    for text in selected_texts:
        if text == option_text:
            matched = True
            break

        if text.startswith(option_text + " "):
            matched = True
            break

        if text.startswith(option_text + "("):
            matched = True
            break

    if not matched:
        raise Exception(
            f"Wrong dropdown selection for {field_id}. "
            f"Expected '{option_text}', got '{selected_display}'"
        )

    print(f"  OK: {selected_display}")


# ============================================================
# RADIO BUTTONS
# ============================================================

def check_radio(page, radio_index):
    radios = page.locator('input[type="radio"]')

    if radio_index >= radios.count():
        raise Exception(
            f"Radio index {radio_index} does not exist. "
            f"Found {radios.count()} radios."
        )

    radios.nth(radio_index).check()

    page.wait_for_timeout(300)

    if not radios.nth(radio_index).is_checked():
        raise Exception(
            f"Radio button {radio_index} was not checked."
        )


# ============================================================
# CAPTCHA DETECTION
# ============================================================

def visible_captcha_detected(page):
    """
    Detect an actual interactive CAPTCHA challenge.

    A normal hidden reCAPTCHA integration or normal checkbox
    is NOT considered a CAPTCHA challenge.

    We do NOT bypass CAPTCHA.
    """

    try:
        body_text = page.locator("body").inner_text().lower()
    except Exception:
        body_text = ""

    challenge_words = [
        "captcha lösen",
        "captcha challenge",
        "verify you are human",
        "prove you are human",
        "select all images",
        "select all squares",
        "bild auswählen",
        "bilder auswählen",
    ]

    for word in challenge_words:
        if word in body_text:
            return True

    # Google's interactive challenge is normally inside bframe.
    challenge_frames = page.locator(
        'iframe[src*="recaptcha"][src*="bframe"]'
    )

    for i in range(challenge_frames.count()):
        try:
            frame = challenge_frames.nth(i)

            if frame.is_visible():
                box = frame.bounding_box()

                if box:
                    if box["width"] > 200 and box["height"] > 150:
                        return True

        except Exception:
            pass

    return False


# ============================================================
# RESULT DETECTION
# ============================================================

def detect_result(page):
    """
    Returns one of:

        SUBMITTED
        SKIPPED_DUPLICATE
        CAPTCHA
        VALIDATION_ERROR
        ERROR
    """

    # Wait for page response/update.
    page.wait_for_timeout(3000)

    # CAPTCHA first.
    if visible_captcha_detected(page):
        return "CAPTCHA"

    try:
        text = page.locator("body").inner_text().lower()
    except Exception:
        return "ERROR"

    # --------------------------------------------------------
    # Successful submission
    # --------------------------------------------------------

    success_phrases = [
        "vielen dank für das übermitteln ihrer informationen",
        "thank you for submitting your information",
    ]

    for phrase in success_phrases:
        if phrase in text:
            return "SUBMITTED"

    # --------------------------------------------------------
    # Duplicate email
    # --------------------------------------------------------

    duplicate_phrases = [
        "es existiert bereits eine anfrage mit dieser e-mail adresse",
        "an application with this email address already exists",
        "already exists",
    ]

    for phrase in duplicate_phrases:
        if phrase in text:
            return "SKIPPED_DUPLICATE"

    # --------------------------------------------------------
    # Form validation error
    # --------------------------------------------------------

    validation_phrases = [
        "es wurden nicht alle felder korrekt befüllt",
        "bitte prüfen sie ihre eingaben",
        "not all fields were correctly filled",
        "please check your entries",
    ]

    for phrase in validation_phrases:
        if phrase in text:
            return "VALIDATION_ERROR"

    return "ERROR"


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    number,
    title,
    listing_url,
    application_url,
    status,
    text,
):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    text = text.replace("\n", " ").strip()

    if len(text) > 2000:
        text = text[:2000]

    with open(
        "application_results.txt",
        "a",
        encoding="utf-8",
    ) as f:

        f.write("=" * 80 + "\n")
        f.write(f"NUMBER: {number}\n")
        f.write(f"TIME: {timestamp}\n")
        f.write(f"STATUS: {status}\n")
        f.write(f"TITLE: {title}\n")
        f.write(f"LISTING: {listing_url}\n")
        f.write(f"APPLICATION: {application_url}\n")
        f.write(f"RESULT: {text}\n")
        f.write("=" * 80 + "\n\n")


# ============================================================
# VERIFY DROPDOWN SELECTIONS
# ============================================================

def verify_selection(page, field_id, expected_text):
    """
    Verify actual ng-select selected display.

    Do NOT use input_value() here.
    """

    combo = page.locator(f'[id="{field_id}"]')

    if combo.count() == 0:
        raise Exception(
            f"Cannot verify missing combobox: {field_id}"
        )

    ng_select = combo.locator(
        "xpath=ancestor::*[contains(@class,'ng-select')][1]"
    )

    labels = ng_select.locator(".ng-value-label")

    values = []

    for i in range(labels.count()):
        try:
            value = labels.nth(i).inner_text().strip()

            if value:
                values.append(value)

        except Exception:
            pass

    for value in values:
        if value == expected_text:
            return True

        if value.startswith(expected_text + " "):
            return True

        if value.startswith(expected_text + "("):
            return True

    raise Exception(
        f"Selection verification failed for {field_id}. "
        f"Expected '{expected_text}', "
        f"actual selected values: {values}"
    )


# ============================================================
# VERIFY FILE UPLOAD
# ============================================================

def upload_file(files_locator, index, file_path):
    """
    Upload a document to Berlinovo.

    Berlinovo may replace/clear the underlying HTML file input
    after processing the upload, so input.files is NOT used as
    a verification mechanism.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    file_input = files_locator.nth(index)

    print(
        f"Uploading file {index + 1}: "
        f"{os.path.basename(file_path)}"
    )

    file_input.set_input_files(file_path)

    # Give Berlinovo's Angular upload component time to
    # process the selected file.
    page = file_input.page
    page.wait_for_timeout(1500)

    print(
        f"  Upload command completed: "
        f"{os.path.basename(file_path)}"
    )

# ============================================================
# FILL APPLICATION
# ============================================================

def fill_application(page):

    print()
    print("Filling application form...")
    print()

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print("Basic information...")

    fill_field(
        page,
        "firstName",
        CONFIG["first_name"],
    )

    fill_field(
        page,
        "lastName",
        CONFIG["last_name"],
    )

    fill_field(
        page,
        "email",
        CONFIG["email"],
    )

    # --------------------------------------------------------
    # Salutation
    # --------------------------------------------------------

    print("Salutation...")

    select_custom_combobox(
        page,
        "formly_17_select_$$_salutation_$$_0",
        CONFIG["salutation"],
    )

    # --------------------------------------------------------
    # Personal information
    # --------------------------------------------------------

    print("Personal information...")

    fill_field(
        page,
        "formly_18_input_$$_first_name_$$_0",
        CONFIG["first_name"],
    )

    fill_field(
        page,
        "formly_18_input_$$_last_name_$$_1",
        CONFIG["last_name"],
    )

    fill_field(
        page,
        "formly_19_input_$$_date_of_birth_$$_0",
        CONFIG["date_of_birth"],
    )

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    print("Address...")

    fill_field(
        page,
        "formly_20_input_$$_street_$$_0",
        CONFIG["street"],
    )

    fill_field(
        page,
        "formly_20_input_$$_house_number_$$_1",
        CONFIG["house_number"],
    )

    fill_field(
        page,
        "formly_21_input_$$_zip_code_$$_0",
        CONFIG["postal_code"],
    )

    fill_field(
        page,
        "formly_21_input_$$_city_$$_1",
        CONFIG["city"],
    )

    select_custom_combobox(
        page,
        "formly_21_select_$$_country_$$_2",
        CONFIG["country"],
    )

    # --------------------------------------------------------
    # Contact
    # --------------------------------------------------------

    print("Contact information...")

    fill_field(
        page,
        "formly_22_input_$$_email_$$_0",
        CONFIG["email"],
    )

    fill_field(
        page,
        "formly_22_input_$$_mobile_number_$$_1",
        CONFIG["mobile"],
    )

    # --------------------------------------------------------
    # Origin / nationality
    # --------------------------------------------------------

    print("Origin / nationality...")

    select_custom_combobox(
        page,
        "formly_23_select_berlinovo_herkunft_0",
        CONFIG["student_from"],
    )

    select_custom_combobox(
        page,
        "formly_24_select_$$_place_of_birth_$$_0",
        CONFIG["nationality"],
    )

    # --------------------------------------------------------
    # Communication language
    # --------------------------------------------------------

    print("Communication language...")

    # 0 = German
    # 1 = English
    check_radio(page, 1)

    # --------------------------------------------------------
    # Study level
    # --------------------------------------------------------

    print("Study level...")

    # 2 = Bachelor
    # 3 = Master
    check_radio(page, 3)

    # --------------------------------------------------------
    # Study state
    # --------------------------------------------------------

    print("Study state...")

    select_custom_combobox(
        page,
        "formly_29_select_berlinovo_bundesland_der_hochschule_0",
        CONFIG["study_state"],
    )

    page.wait_for_timeout(700)

    # --------------------------------------------------------
    # University type
    # --------------------------------------------------------

    print("University type...")

    select_custom_combobox(
        page,
        "formly_30_select_berlinovo_art_der_hochschule_berlin_0",
        CONFIG["university_type"],
    )

    page.wait_for_timeout(700)

    # --------------------------------------------------------
    # University
    # --------------------------------------------------------

    print("University...")

    select_custom_combobox(
        page,
        "formly_33_select_berlinovo_name_fachhochschule_berlin_0",
        CONFIG["university"],
    )

    page.wait_for_timeout(700)

    # --------------------------------------------------------
    # Contract partner
    # --------------------------------------------------------

    print("Contract partner...")

    contract_checkbox = field(
        page,
        "formly_40_checkbox_$$_is_contract_partner_$$_0",
    )

    if not contract_checkbox.is_checked():
        contract_checkbox.check()

    if not contract_checkbox.is_checked():
        raise Exception(
            "Contract partner checkbox could not be checked."
        )

    # --------------------------------------------------------
    # Contract start
    # --------------------------------------------------------

    print("Contract start...")

    fill_field(
        page,
        "formly_7_input_berlinovo_gewuenschter_vertragsbeginn_0",
        CONFIG["contract_start"],
    )

    # --------------------------------------------------------
    # Rental duration
    # --------------------------------------------------------

    print("Rental duration...")

    fill_field(
        page,
        "formly_8_input_berlinovo_gewuenschte_mietdauer_in_monaten_0",
        CONFIG["rental_months"],
    )

    # --------------------------------------------------------
    # Housing type
    # --------------------------------------------------------

    print("Housing type...")

    select_custom_combobox(
        page,
        "formly_9_select_berlinovo_gewuenschte_wohnform_0",
        CONFIG["housing_type"],
    )

    # --------------------------------------------------------
    # Accessible apartment
    # --------------------------------------------------------

    print("Accessible apartment...")

    # 4 = Yes
    # 5 = No
    check_radio(page, 5)

    # --------------------------------------------------------
    # Additional note
    # --------------------------------------------------------

    print("Additional note...")

    note = field(
        page,
        "formly_11_textarea_berlinovo_zusaetzliche_bemerkung_0",
    )

    note.fill(
        CONFIG.get("additional_note", "")
    )

    # --------------------------------------------------------
    # Privacy
    # --------------------------------------------------------

    print("Privacy consent...")

    privacy = field(
        page,
        "formly_13_checkbox_berlinovo_bestaetigung_datenschutzhinweis_0",
    )

    if not privacy.is_checked():
        privacy.check()

    if not privacy.is_checked():
        raise Exception(
            "Privacy checkbox could not be checked."
        )

    # --------------------------------------------------------
    # VERIFY CUSTOM DROPDOWNS
    # --------------------------------------------------------

    print()
    print("Verifying dropdown selections...")

    verify_selection(
        page,
        "formly_17_select_$$_salutation_$$_0",
        CONFIG["salutation"],
    )

    verify_selection(
        page,
        "formly_21_select_$$_country_$$_2",
        CONFIG["country"],
    )

    verify_selection(
        page,
        "formly_23_select_berlinovo_herkunft_0",
        CONFIG["student_from"],
    )

    verify_selection(
        page,
        "formly_24_select_$$_place_of_birth_$$_0",
        CONFIG["nationality"],
    )

    verify_selection(
        page,
        "formly_29_select_berlinovo_bundesland_der_hochschule_0",
        CONFIG["study_state"],
    )

    verify_selection(
        page,
        "formly_30_select_berlinovo_art_der_hochschule_berlin_0",
        CONFIG["university_type"],
    )

    verify_selection(
        page,
        "formly_33_select_berlinovo_name_fachhochschule_berlin_0",
        CONFIG["university"],
    )

    verify_selection(
        page,
        "formly_9_select_berlinovo_gewuenschte_wohnform_0",
        CONFIG["housing_type"],
    )

    print("All dropdown selections verified.")

    # --------------------------------------------------------
    # VERIFY RADIOS
    # --------------------------------------------------------

    print("Verifying radio buttons...")

    radios = page.locator('input[type="radio"]')

    if not radios.nth(1).is_checked():
        raise Exception("English radio is not selected.")

    if not radios.nth(3).is_checked():
        raise Exception("Master radio is not selected.")

    if not radios.nth(5).is_checked():
        raise Exception(
            "Accessible = No radio is not selected."
        )

    print("All radio selections verified.")

    # --------------------------------------------------------
    # UPLOAD DOCUMENTS
    # --------------------------------------------------------

    print()
    print("Preparing document uploads...")

    files = page.locator('input[type="file"]')

    if files.count() < 3:
        raise Exception(
            f"Expected at least 3 file inputs, "
            f"found {files.count()}"
        )

    enrollment_file = CONFIG["enrollment_document"]
    passport_file = CONFIG["passport_document"]
    financial_file = CONFIG["income_document"]

    upload_file(
        files,
        0,
        enrollment_file,
    )

    upload_file(
        files,
        1,
        passport_file,
    )

    upload_file(
        files,
        2,
        financial_file,
    )

    page.wait_for_timeout(1000)

    print()
    print("Application form filled and verified.")
    print()


# ============================================================
# VALIDATION DIAGNOSTICS
# ============================================================

def print_validation_state(page):

    print()
    print("=" * 80)
    print("FORM VALIDATION STATE")
    print("=" * 80)

    # Native HTML validation.
    invalid = page.locator(
        "input:invalid, textarea:invalid, select:invalid"
    )

    print(
        "HTML INVALID FIELDS:",
        invalid.count()
    )

    for i in range(invalid.count()):
        try:
            element = invalid.nth(i)

            print(
                "INVALID:",
                element.get_attribute("id"),
                "|",
                element.get_attribute("name"),
                "|",
                element.get_attribute("value"),
            )

        except Exception:
            pass

    # ARIA validation.
    aria_invalid = page.locator(
        '[aria-invalid="true"]'
    )

    print(
        "ARIA INVALID FIELDS:",
        aria_invalid.count()
    )

    for i in range(aria_invalid.count()):
        try:
            element = aria_invalid.nth(i)

            print(
                "ARIA INVALID:",
                element.get_attribute("id"),
                "|",
                element.get_attribute("name"),
                "|",
                element.get_attribute("value"),
            )

        except Exception:
            pass

    # Visible validation messages.
    validation_elements = page.locator(
        '[class*="error"], '
        '[class*="invalid"], '
        '[class*="validation"], '
        "formly-validation-message"
    )

    print()
    print("VISIBLE VALIDATION MESSAGES:")

    found_message = False

    for i in range(validation_elements.count()):
        try:
            element = validation_elements.nth(i)

            if element.is_visible():
                text = element.inner_text().strip()

                if text:
                    print("-", text)
                    found_message = True

        except Exception:
            pass

    if not found_message:
        print("None detected.")

    print("=" * 80)
    print()


# ============================================================
# MAIN BOT
# ============================================================

print()
print("=" * 80)
print("BERLINOVO APPLICATION BOT")
print("=" * 80)
print(f"APPLICATIONS FOUND: {len(APPLICATIONS)}")
print("=" * 80)
print()


# Start fresh result file.
with open(
    "application_results.txt",
    "w",
    encoding="utf-8",
) as f:

    f.write(
        "BERLINOVO APPLICATION RESULTS\n"
    )

    f.write(
        "=" * 80 + "\n\n"
    )


with sync_playwright() as p:

    # ========================================================
    # LAUNCH ONE BROWSER WINDOW
    # ========================================================

    try:

        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized"
            ],
        )

        print("Using Google Chrome.")

    except Exception:

        print(
            "Google Chrome was not available."
        )

        print(
            "Using Playwright Chromium instead."
        )

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized"
            ],
        )

    # One browser context/session.
    context = browser.new_context(
        viewport={
            "width": 1440,
            "height": 1000,
        }
    )

    # ========================================================
    # MAIN LISTINGS TAB
    # ========================================================

    listings_page = context.new_page()

    print()
    print(
        "Opening Berlinovo listings page..."
    )

    listings_page.goto(
        BERLINOVO_LISTINGS_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    listings_page.wait_for_timeout(3000)

    print(
        "Berlinovo listings tab is OPEN."
    )

    print()
    print(
        "Starting applications..."
    )

    print()

    # ========================================================
    # COUNTERS
    # ========================================================

    submitted = 0
    skipped = 0
    errors = 0
    captcha_count = 0

    # ========================================================
    # PROCESS EVERY APPLICATION
    # ========================================================

    for number, item in enumerate(
        APPLICATIONS,
        1,
    ):

        listing_url = item["listing"]
        title = item["title"]
        application_url = item["application"]

        print()
        print("#" * 80)
        print(
            f"APPLICATION {number} OF "
            f"{len(APPLICATIONS)}"
        )
        print("#" * 80)

        print(
            f"TITLE: {title}"
        )

        print(
            f"LISTING: {listing_url}"
        )

        print(
            f"APPLICATION: {application_url}"
        )

        print()

        application_page = None

        try:

            # =================================================
            # OPEN APPLICATION IN NEW TAB
            # =================================================

            print(
                "Opening application in new tab..."
            )

            application_page = context.new_page()

            application_page.goto(
                application_url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            application_page.wait_for_timeout(
                2500
            )

            print(
                "Application page loaded."
            )

            # =================================================
            # CHECK CAPTCHA BEFORE FILLING
            # =================================================

            if visible_captcha_detected(
                application_page
            ):

                print()
                print(
                    "!!! ACTUAL CAPTCHA DETECTED !!!"
                )

                print(
                    "The bot will NOT bypass it."
                )

                print(
                    "Manual action is required."
                )

                text = application_page.locator(
                    "body"
                ).inner_text()

                application_page.screenshot(
                    path=(
                        f"captcha_application_"
                        f"{number}.png"
                    ),
                    full_page=True,
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "CAPTCHA_MANUAL_ACTION_REQUIRED",
                    text,
                )

                captcha_count += 1

                print(
                    "CAPTCHA screenshot saved."
                )

                print(
                    "Bot stopped for safety."
                )

                break

            # =================================================
            # FILL FORM
            # =================================================

            fill_application(
                application_page
            )

            # =================================================
            # CAPTCHA CHECK BEFORE SUBMIT
            # =================================================

            if visible_captcha_detected(
                application_page
            ):

                print()
                print(
                    "!!! ACTUAL CAPTCHA DETECTED "
                    "BEFORE SUBMIT !!!"
                )

                print(
                    "The bot will NOT bypass it."
                )

                text = application_page.locator(
                    "body"
                ).inner_text()

                application_page.screenshot(
                    path=(
                        f"captcha_application_"
                        f"{number}.png"
                    ),
                    full_page=True,
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "CAPTCHA_MANUAL_ACTION_REQUIRED",
                    text,
                )

                captcha_count += 1

                print(
                    "Bot stopped for safety."
                )

                break

            # =================================================
            # FINAL FORM CHECK
            # =================================================

            print()
            print(
                "Final form validation check..."
            )

            print_validation_state(
                application_page
            )

            # =================================================
            # SUBMIT
            # =================================================

            print(
                "Submitting application..."
            )

            submit_button = application_page.locator(
                "button[type=submit]"
            ).first

            if submit_button.count() == 0:
                raise Exception(
                    "Submit button not found."
                )

            if not submit_button.is_visible():
                raise Exception(
                    "Submit button is not visible."
                )

            # Click submit.
            submit_button.click()

            # =================================================
            # WAIT FOR RESULT
            # =================================================

            print(
                "Waiting for submission result..."
            )

            application_page.wait_for_timeout(
                5000
            )

            status = detect_result(
                application_page
            )

            text = application_page.locator(
                "body"
            ).inner_text()

            # =================================================
            # SUCCESS
            # =================================================

            if status == "SUBMITTED":

                submitted += 1

                print()
                print(
                    "SUCCESS: APPLICATION SUBMITTED"
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "SUBMITTED",
                    text,
                )

            # =================================================
            # DUPLICATE
            # =================================================

            elif status == "SKIPPED_DUPLICATE":

                skipped += 1

                print()
                print(
                    "SKIPPED: EMAIL ALREADY HAS "
                    "AN APPLICATION"
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "SKIPPED_DUPLICATE",
                    text,
                )

            # =================================================
            # CAPTCHA
            # =================================================

            elif status == "CAPTCHA":

                captcha_count += 1

                print()
                print(
                    "ACTUAL CAPTCHA DETECTED "
                    "AFTER SUBMIT."
                )

                print(
                    "The bot will NOT bypass it."
                )

                application_page.screenshot(
                    path=(
                        f"captcha_application_"
                        f"{number}.png"
                    ),
                    full_page=True,
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "CAPTCHA_MANUAL_ACTION_REQUIRED",
                    text,
                )

                print(
                    "Bot stopped."
                )

                break

            # =================================================
            # VALIDATION ERROR
            # =================================================

            elif status == "VALIDATION_ERROR":

                errors += 1

                print()
                print(
                    "ERROR: BERLINOVO FORM "
                    "VALIDATION FAILED"
                )

                print(
                    "The application was NOT "
                    "accepted."
                )

                print_validation_state(
                    application_page
                )

                application_page.screenshot(
                    path=(
                        f"validation_application_"
                        f"{number}.png"
                    ),
                    full_page=True,
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "VALIDATION_ERROR",
                    text,
                )

                print(
                    "Validation screenshot saved."
                )

                # Skip this application and continue with the next one.
                continue

            # =================================================
            # UNEXPECTED ERROR
            # =================================================

            else:

                errors += 1

                print()
                print(
                    "ERROR: UNEXPECTED RESULT"
                )

                print(
                    "The bot will save the page "
                    "and stop."
                )

                application_page.screenshot(
                    path=(
                        f"error_application_"
                        f"{number}.png"
                    ),
                    full_page=True,
                )

                save_result(
                    number,
                    title,
                    listing_url,
                    application_url,
                    "ERROR",
                    text,
                )

                break

        except Exception as e:

            errors += 1

            print()
            print(
                "ERROR:",
                e,
            )

            error_text = str(e)

            # Save screenshot.
            if application_page:

                try:

                    application_page.screenshot(
                        path=(
                            f"error_application_"
                            f"{number}.png"
                        ),
                        full_page=True,
                    )

                except Exception:
                    pass

                # Save page text.
                try:

                    error_text += (
                        "\n\nPAGE TEXT:\n"
                    )

                    error_text += (
                        application_page.locator(
                            "body"
                        ).inner_text()
                    )

                except Exception:
                    pass

            save_result(
                number,
                title,
                listing_url,
                application_url,
                "ERROR",
                error_text,
            )

            print()
            print(
                "Bot stopped because an "
                "unexpected error occurred."
            )

            break

        finally:

            # =================================================
            # CLOSE ONLY APPLICATION TAB
            # =================================================

            if application_page:

                try:

                    application_page.close()

                    print()
                    print(
                        "Application tab closed."
                    )

                except Exception:
                    pass

        # ====================================================
        # DELAY BEFORE NEXT APPLICATION
        # ====================================================

        if number < len(APPLICATIONS):

            print()
            print(
                "Waiting before next application..."
            )

            time.sleep(3)

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 80)
    print("BOT FINISHED")
    print("=" * 80)

    print(
        f"TOTAL APPLICATIONS: "
        f"{len(APPLICATIONS)}"
    )

    print(
        f"SUBMITTED: {submitted}"
    )

    print(
        f"SKIPPED (DUPLICATE): {skipped}"
    )

    print(
        f"CAPTCHA: {captcha_count}"
    )

    print(
        f"ERRORS: {errors}"
    )

    print("=" * 80)
    print()

    print(
        "The Berlinovo listings tab remains open."
    )

    print(
        "Results saved to: "
        "application_results.txt"
    )

    print()

    print(
        "The browser will remain open."
    )

    print(
        "Close it manually when finished."
    )

    print()

    # Keep browser open so the listings tab
    # remains available.
    input(
        "Press ENTER in Terminal to close "
        "the browser..."
    )

    browser.close()
