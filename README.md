# 🛡️ PharmaGuard: EU Compliance Auditor

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Compliance](https://img.shields.io/badge/Standard-EU%20CosIng%20Annex%20II-green?style=for-the-badge)](https://ec.europa.eu/growth/sectors/cosmetics/cosing_en)
[![Automation](https://img.shields.io/badge/Automation-Google%20Apps%20Script-yellow?style=for-the-badge&logo=google)](https://script.google.com/)

**PharmaGuard** is a robust, production-grade auditing tool designed to screen cosmetic formulations against the official **EU CosIng Annex II** list of prohibited substances. It utilizes a hybrid detection engine combining exact matching, fuzzy logic, deep substring scanning, and an intelligent safety filter to ensure high accuracy with zero false positives.

---

## 🌟 Why PharmaGuard?

Regulatory compliance in the cosmetic industry is complex. Lists change, names are disguised, and human error is common. PharmaGuard solves this by:
1.  **Eliminating Manual Checks:** Automates the cross-referencing process.
2.  **Stopping "Trojan Horse" Ingredients:** Detects banned substances hidden inside complex chemical names.
3.  **Recognizing Aliases:** Identifies toxic chemicals hiding behind trade names (e.g., *Formalin*).
4.  **Protecting Safe Ingredients:** Uses a "Safe List" to prevent false alarms on common ingredients like Water or Alcohol.

---

## 🚀 Key Features (V6.1)

### 1. 🧠 Intelligent Filtration Engine
The system processes every ingredient through a 5-layer security protocol:
* **Layer 0 (Immunity):** Checks against a curated `SAFE_LIST` (e.g., *Aqua, Glycerin, Ammonia*) to prevent false positives.
* **Layer 1 (Alias Hunter):** Detects dangerous synonyms using a custom dictionary (e.g., *Wood Alcohol* → *Methanol*).
* **Layer 2 (CAS Verification):** Audits based on unique Chemical Abstracts Service (CAS) numbers (e.g., *80-54-6*).
* **Layer 3 (Deep Scan):** Uses substring analysis to find banned substances hidden within long chemical descriptions (e.g., finding *Mercury* inside *Ammoniated Mercury*).
* **Layer 4 (Typo Guard):** Uses Fuzzy Logic (Levenshtein distance) to catch misspellings (e.g., *Chlroform*).

### 2. 🔄 Auto-Sync Pipeline (Google -> GitHub)
The database is never stale. A **Google Apps Script** bot runs on a serverless trigger every 30 minutes to:
1.  Fetch the latest CSV from the **European Commission** servers.
2.  Process and encode the data.
3.  Push updates directly to this repository via the GitHub API.

---

## 📂 Project Structure

* `app.py`: The main Streamlit application containing the audit logic and UI.
* `banned.csv`: The live database of prohibited substances (Auto-updated).
* `update_script.gs`: The Google Apps Script code responsible for the automation pipeline.
* `requirements.txt`: Python dependencies.

---

## ⚙️ The Automation Engine (How to Replicate)

This project includes the automation script `update_script.gs` for educational purposes. If you wish to set up your own auto-updater:

1.  **Create a Script:** Go to [Google Apps Script](https://script.google.com/) and create a new project.
2.  **Copy Code:** Copy the content of [`update_script.gs`](./update_script.gs) from this repo.
3.  **Configure:**
    * Replace `repoOwner` and `repoName` with your GitHub details.
    * Generate a **GitHub Personal Access Token** (with `repo` scope) and add it to the script.
4.  **Set Trigger:** In the Apps Script dashboard, go to **Triggers** > **Add Trigger** > Select `updateGithubData` > Select **Time-driven** > **Every 30 minutes**.

> **Security Note:** Never commit your actual GitHub Token to a public repository.

---

## 🛠️ Installation & Local Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ph-aya/PharmaGuard-Audit.git](https://github.com/ph-aya/PharmaGuard-Audit.git)
    cd PharmaGuard-Audit
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

---

## 🧪 Testing Scenarios (Validation)

PharmaGuard has been stress-tested against the following scenarios:

| Test Case | Input Example | Expected Result | Logic Used |
| :--- | :--- | :--- | :--- |
| **Safe List** | `Aqua, Alcohol Denat` | ✅ PASSED | Layer 0 (Immunity) |
| **Alias Attack** | `Formalin, Wood Alcohol` | 🚫 FAILED | Layer 1 (Alias Check) |
| **CAS Code** | `84-74-2` (Phthalate) | 🚫 FAILED | Layer 2 (CAS Match) |
| **Hidden Toxin** | `...contains Mercury...` | 🚫 FAILED | Layer 3 (Deep Scan) |
| **Typo** | `Chlroform` | ❓ SUSPICIOUS | Layer 4 (Fuzzy Logic) |

---

## ⚠️ Disclaimer
This tool is intended for professional auditing assistance. While it syncs with official EU data, final regulatory compliance should always be cross-referenced with the latest official publications from the European Commission (CosIng).

---
*Developed by Eng. Aya | Powered by Python, Streamlit & Google Cloud*
