# 🛡️ PharmaGuard: EU Compliance Auditor

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Compliance](https://img.shields.io/badge/Standard-EU%20CosIng%20Annex%20II-green?style=for-the-badge)](https://ec.europa.eu/growth/sectors/cosmetics/cosing_en)

**PharmaGuard** is a robust, real-time auditing tool designed to screen cosmetic formulations against the official **EU CosIng Annex II** list of prohibited substances. It serves as a digital safety net for pharmacists, regulatory affairs specialists, and consumers.

---

## 🚀 Key Features

* **Live Database Sync:** Automatically fetches the latest banned substances list (Annex II) every 30 minutes via GitHub Pipeline.
* **Deep Search Protocol:** Detects banned ingredients hidden within complex chemical strings (Substring Matching).
* **Alias Detection System:** Identifies toxic substances hiding behind common trade names (e.g., *Formalin* → *Formaldehyde*, *Lilial* → *Butylphenyl Methylpropional*).
* **Smart Safety Filter:** Prevents false positives by recognizing safe common chemicals (e.g., *Aqua*, *Alcohol*, *Ammonia*).
* **Fuzzy Logic Engine:** Detects typos and spelling errors in ingredient lists (e.g., *Chlroform* detected as *Chloroform*).
* **CAS Number Recognition:** Audits ingredients based on their unique Chemical Abstracts Service (CAS) IDs.

---

## 🛠️ How It Works

The system operates on a multi-layer filtration logic:
1.  **Level 0 (Immunity):** Checks if the ingredient is on the verified `SAFE_LIST` (e.g., Water, Glycerin).
2.  **Level 1 (Aliases):** Checks against a dictionary of known dangerous synonyms.
3.  **Level 2 (Identity):** Checks for exact matches by Name or CAS Number.
4.  **Level 3 (Deep Scan):** Scans for the ingredient inside long chemical descriptions.
5.  **Level 4 (Fuzzy Match):** Uses Levenshtein distance to find misspellings.

---

## 💻 Installation & Usage

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

## ⚠️ Disclaimer
This tool is intended for educational and preliminary auditing purposes. While it syncs with official EU data, final compliance verification should always be cross-referenced with the latest official publications from the European Commission.

---
*Developed by Ph. Aya | Powered by Python & Streamlit*
