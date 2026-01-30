/**
 * 🛡️ PharmaGuard Auto-Updater
 * ----------------------------------------
 * This script runs on Google Apps Script servers.
 * It fetches the official EU CosIng Annex II file and pushes it to GitHub.
 * * Frequency: Runs every 30 minutes (via Triggers).
 */

function updateGithubData() {
  // 1. Configuration (Replace with your details)
  var githubToken = "YOUR_GITHUB_TOKEN_HERE"; // ⚠️ Keep this secret!
  var repoOwner = "ph-aya";
  var repoName = "PharmaGuard-Audit";
  var fileName = "banned.csv";
  
  // Official EU Source URL
  var sourceUrl = "https://ec.europa.eu/growth/tools-databases/cosing/pdf/COSING_Annex%20II_v2.csv";

  try {
    // 2. Fetch Data from EU
    var response = UrlFetchApp.fetch(sourceUrl);
    var csvContent = response.getContentText();
    var encodedContent = Utilities.base64Encode(csvContent);

    // 3. Get current file SHA (needed for update)
    var fileUrl = "https://api.github.com/repos/" + repoOwner + "/" + repoName + "/contents/" + fileName;
    var options = {
      "method": "get",
      "headers": { "Authorization": "Bearer " + githubToken }
    };
    
    var sha = null;
    try {
      var getResponse = UrlFetchApp.fetch(fileUrl, options);
      var fileData = JSON.parse(getResponse.getContentText());
      sha = fileData.sha;
    } catch (e) {
      Logger.log("File doesn't exist yet, creating new one.");
    }

    // 4. Push update to GitHub
    var payload = {
      "message": "Auto-sync: EU Database Update 🔄",
      "content": encodedContent,
      "branch": "main"
    };
    
    if (sha) {
      payload.sha = sha;
    }

    var putOptions = {
      "method": "put",
      "headers": {
        "Authorization": "Bearer " + githubToken,
        "Content-Type": "application/json"
      },
      "payload": JSON.stringify(payload)
    };

    UrlFetchApp.fetch(fileUrl, putOptions);
    Logger.log("✅ Success: Data synced with GitHub.");

  } catch (error) {
    Logger.log("❌ Error: " + error.toString());
  }
}
