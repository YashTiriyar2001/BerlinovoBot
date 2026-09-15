# 🏠 Berlinovo Application Bot

A Playwright-based automation bot for applying to Berlinovo student housing listings.

The bot automatically discovers available Berlinovo apartments, filters listings based on configurable criteria, fills out application forms, uploads required documents, submits applications, and records the result of each application.

> ⚠️ **Important:** This project is intended for personal automation and educational purposes. It does not bypass CAPTCHA, website security, rate limits, or other access controls. If a CAPTCHA appears, it requires manual handling.

---

## ✨ Features

- 🔎 Automatically discovers Berlinovo apartment listings
- 💶 Filters apartments by maximum monthly rent
- 🚫 Supports excluding specific listings
- 📝 Automatically fills application forms
- 📄 Uploads enrollment, passport, and financial documents
- 🌍 Handles Berlinovo's custom dropdown fields
- 👤 Stores applicant information in a configurable JSON file
- 🔄 Detects duplicate applications
- 🤖 Detects CAPTCHA and stops for manual handling
- ⚠️ Detects form validation errors
- 📊 Records application results
- 🗂️ Opens each application in a separate browser tab
- 🌐 Keeps the main Berlinovo listings tab open
- 🔐 Keeps sensitive personal information out of Git

---

## 🛠️ Tech Stack

- **Python 3**
- **Playwright**
- **Chromium / Google Chrome**
- **JSON**
- **Git & GitHub**

---

## 📁 Project Structure

```text
BerlinovoBot/
│
├── final_bot.py
├── config.json
├── filter_applications.py
│
├── inspect_all_listings.py
├── inspect_application_links.py
├── inspect_berlin.py
├── inspect_complete.py
├── inspect_dropdown.py
├── inspect_dropdowns.py
├── inspect_form.py
├── inspect_listings.py
├── inspect_pagination.py
├── inspect_remaining.py
│
├── diagnose_form.py
├── submit_one.py
├── test_fill.py
│
├── .gitignore
├── README.md
└── ...
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone git@github.com:YashTiriyar2001/BerlinovoBot.git
cd BerlinovoBot
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

## 3. Activate the virtual environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## 4. Install Playwright

```bash
pip install playwright
```

## 5. Install Chromium

```bash
python -m playwright install chromium
```

---

# ⚙️ Configuration

The bot uses `config.json` to store applicant information and document paths.

Before running the bot, edit:

```text
config.json
```

### Example

```json
{
  "first_name": "YOUR_FIRST_NAME",
  "last_name": "YOUR_LAST_NAME",
  "email": "your@email.com",
  "salutation": "Herr (Mr)",
  "date_of_birth": "DD.MM.YYYY",
  "street": "YOUR_STREET",
  "house_number": "YOUR_HOUSE_NUMBER",
  "postal_code": "YOUR_POSTAL_CODE",
  "city": "YOUR_CITY",
  "country": "Indien",
  "mobile": "YOUR_MOBILE",
  "student_from": "einem Land außerhalb der EU (from a non-EU country)",
  "nationality": "Indien",
  "communication_language": "English",
  "study_level": "Master",
  "study_state": "Berlin",
  "university_type": "Fachhochschule (University of applied sciences)",
  "university": "Hochschule für Technik und Wirtschaft Berlin (HTW)",
  "contract_partner": true,
  "contract_start": "DD.MM.YYYY",
  "rental_months": 12,
  "housing_type": "Keine Präferenz (No Preference)",
  "accessible": "No",
  "additional_note": "",
  "privacy_consent": true,
  "enrollment_document": "/path/to/enrollment.pdf",
  "passport_document": "/path/to/passport.pdf",
  "income_document": "/path/to/income.pdf"
}
```

> 💡 Replace the example values with your own information before running the bot.

---

## 📄 Document Paths

The following fields must point to the documents you want to upload:

```text
enrollment_document
passport_document
income_document
```

For example:

```json
"enrollment_document": "/Users/username/Documents/enrollment.pdf"
```

Make sure the files exist at the specified paths before starting the bot.

---

# ▶️ Running the Bot

After configuring `config.json`, run:

```bash
python final_bot.py
```

The bot will:

1. Open the Berlinovo listings page
2. Discover available listings
3. Filter listings according to the configured criteria
4. Open each application in a new browser tab
5. Fill in the application form
6. Upload the required documents
7. Validate the form
8. Submit the application
9. Detect the submission result
10. Close only the application tab
11. Continue with the next eligible listing
12. Save the application result

---

# 💶 Rent Filtering

The bot supports filtering apartments by maximum monthly rent.

For example:

```python
MAX_RENT = 600
```

Apartments with a rent above the configured maximum are skipped.

Specific apartments can also be excluded when required.

---

# 🔄 Duplicate Applications

If Berlinovo reports that an application already exists for the configured email address, the bot marks the application as:

```text
SKIPPED_DUPLICATE
```

The application tab is then closed and the bot continues with the next listing.

---

# 🧩 Error Handling

The bot can identify several application outcomes:

| Status | Description |
|---|---|
| `SUBMITTED` | Application was successfully submitted |
| `SKIPPED_DUPLICATE` | An application already exists for the email address |
| `VALIDATION_ERROR` | Berlinovo rejected the form because of a validation issue |
| `CAPTCHA` | CAPTCHA was detected and requires manual handling |
| `ERROR` | An unexpected error occurred |

When possible, the bot continues processing the remaining eligible listings instead of stopping the entire run.

---

# 🤖 CAPTCHA

This project **does not bypass CAPTCHA**.

If a CAPTCHA is detected, the bot stops processing that application and requires manual handling.

> 🚫 Do not attempt to circumvent CAPTCHA or other website security mechanisms.

---

# 📊 Results

Application results are saved locally in:

```text
application_results.txt
```

The bot may also generate screenshots and debugging files while running.

These generated files are excluded from Git using `.gitignore`.

---

# 🔐 Privacy & Security

This project handles personal information and uploaded documents.

**Never publish sensitive personal information to a public GitHub repository.**

Do not commit:

- Passport information
- Financial documents
- Personal addresses
- Phone numbers
- Private email addresses
- Application results
- Uploaded documents
- Personal screenshots

The following files and directories are excluded from Git:

```text
.venv/
config.json
*.png
results/
application_results.txt
```

Users should configure their own local `config.json` before running the bot.

---

# ⚠️ Responsible Use

This project automates interactions with a third-party housing website.

Users are responsible for:

- Reviewing their information before submission
- Ensuring submitted information is accurate
- Respecting Berlinovo's terms and policies
- Respecting website rate limits
- Avoiding excessive requests
- Protecting personal information and documents
- Handling CAPTCHA manually

Automation should **not** be used to bypass security controls, CAPTCHA, rate limits, or other technical restrictions.

---

# 📌 Disclaimer

This project is an independently developed automation tool and is **not affiliated with, sponsored by, or endorsed by Berlinovo or Wohnungshelden**.

The author does not guarantee that the bot will continue to work if the Berlinovo website or application forms change.

**Use this software at your own risk.**

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# ⭐ Contributing

Contributions, bug reports, and improvements are welcome.

If you find a problem:

1. Open an issue
2. Describe the problem
3. Include relevant error messages
4. Provide steps to reproduce the issue when possible

> 🔒 Never include passwords, personal information, passports, financial documents, or other sensitive data in issues or pull requests.

---

# 👨‍💻 Author

**Yash Tiriyar**

Built with **Python + Playwright**.
