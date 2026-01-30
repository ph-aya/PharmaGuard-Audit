---

## ⚙️ The Automation Engine (Google Apps Script)

Behind the scenes, this project uses a **Google Apps Script** to keep the data fresh without manual intervention. The script `update_script.gs` runs on Google servers and performs the following:

1.  **Fetches** the latest CSV directly from the European Commission website.
2.  **Encodes** the data to Base64.
3.  **Pushes** the update to this GitHub repository via API.

### 🔧 How to replicate the automation:
If you want to run your own auto-updater:
1.  Create a new project in [Google Apps Script](https://script.google.com/).
2.  Copy the code from [`update_script.gs`](./update_script.gs).
3.  Replace `repoOwner`, `repoName`, and `githubToken` with your own credentials.
4.  Set a **Time-driven Trigger** to run `updateGithubData` every 30 minutes (or as needed).

> **Note:** Never commit your actual GitHub Token to the public repository! Use environment variables or keep it private within the Apps Script dashboard.
