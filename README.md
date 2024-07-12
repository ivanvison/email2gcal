# Gmail Email to Google Calendar Yearly Recurrent Event

This repository contains a script to automate the process of transferring specific events from emails in a Gmail account to a Google Calendar, making them recurrent yearly based on the email content.


## Context

Users enter their birth dates on a website, which sends this information to an email account. Previously, these events had to be manually added to a Google Calendar. The email body includes:
- **Name:** ABC DEF
- **Date:** dd-mm-yyyy

There was no out-of-the-box / quick solution, especially one integrated with WordPress.


## Solution

This script automates the entire process using ChatGPT and GitHub Copilot for code generation. The configuration file remains hidden for security.


### Features

- **Environment Variables:** Loads from a `.env` file.
- **Gmail Connection:** Uses provided email and password.
- **Email Fetching:** Retrieves new (unseen) emails from the inbox.
- **Email Parsing:** Extracts specific patterns (names and dates) from the email body.
- **Duplicate Check:** Ensures no duplicate events using a CSV file.
- **Email Deletion:** Removes processed emails.
- **Google Calendar Authentication:** Uses OAuth credentials stored in `token.pickle` or generates new ones if necessary.
- **Event Creation:** Adds non-duplicate events to Google Calendar.


### Process Overview

1. **Connect to Gmail:** Authenticate using environment variables.
2. **Fetch Emails:** Retrieve unseen emails from the inbox.
3. **Parse Emails:** Extract event details using regex.
4. **Check Duplicates:** Compare against a local CSV file.
5. **Update CSV:** Add new events to the CSV file.
6. **Delete Emails:** Remove processed emails to keep the inbox clean.
7. **Google Calendar Authentication:** Use OAuth credentials.
8. **Read CSV:** Check for existing events in Google Calendar.
9. **Create Events:** Add new events to Google Calendar.

*The main reason why I'm saving everything in a CSV (which is a step that could be saved) is to triple check after the process is done in case that is needed.*

### Prompt

After several iterations, the ideal prompt message is:

"I need a Python script that automates transferring specific events from emails in a Gmail account to a Google Calendar. The script should:

1. Connect to Gmail using credentials stored in environment variables.
2. Fetch new (unseen) emails.
3. Parse email body for event details.
4. Check for duplicates using a local CSV file.
5. Add non-duplicate events to the CSV.
6. Delete processed emails.
7. Authenticate with Google Calendar using OAuth credentials.
8. Check for existing events in Google Calendar.
9. Create new events for non-duplicates.
10. Structure the script with a main function for smooth processing.

Additional requirements:

- Use environment variables for sensitive information.
- Handle HTML emails accurately.
- Include error handling for network/authentication issues.
- Ensure events recur annually.

Could you help me create this Python script with comments and best practices?"


### Additional Notes

Creating the final product involved merging individual processes. Additional steps included deleting all duplicate events for the year (script not included)

Total development time was approximately between 12 hours between tweaking and testing, saving around 1 minute and potentially 10 clicks per email.

*The part that took the most, at least for me, was the calendar interaction, yearly reccurency with full day events.*

---
### Structure for Ignored Files

**.env**
- GMAIL_ACCOUNT_EMAIL=
- GMAIL_ACCOUNT_PASSWORD="password here"
- GOOGLE_CALENDAR_ID=

**google_client_secret.json**
- {"installed":{"client_id":"XXX","project_id":"XXX","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"XXX","redirect_uris":["http://localhost"]}}

**tokek.pickle**
- *Not needed. File gets created automatically after authentication*



## Next Steps

1. Deploy the script on a server with a cron job; or
2. Integrate the code into WordPress to handle event additions directly every time a date is submitted. 