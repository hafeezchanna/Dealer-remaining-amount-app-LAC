# Liberty Agro Chemicals – Dealer Payment Reminder System

This is a Streamlit web app for Liberty Agro Chemicals (Sukkur) to prepare personalized dealer payment reminders from the current dealer ledger.

## Included
- Current 29-Oct-2026 dealer dataset
- Dashboard with dealer count and total outstanding
- Dealer search
- Mobile-number filtering
- Personalized payment reminder
- WhatsApp Web button for each dealer
- Excel/CSV ledger import
- Password protection through Streamlit Secrets

## Important WhatsApp limitation
The app prepares and opens a WhatsApp Web chat with the personalized message. WhatsApp requires the operator to press **Send**. The app does not silently send bulk WhatsApp messages.

## Deploy on Streamlit Community Cloud
1. Create a **private GitHub repository**.
2. Upload all files in this folder, keeping `app.py` in the repository root and the `data` folder intact.
3. Open Streamlit Community Cloud and sign in with GitHub.
4. Create a new app, choose the repository, branch, and `app.py`.
5. Deploy.
6. In the app's settings, add a secret:
   APP_PASSWORD = "your-strong-password"
7. Restart the app.

## Security
The included dataset contains dealer names, phone numbers and financial balances. Keep the GitHub repository private and do not publish the ledger publicly.

## Future upgrade
For persistent sent/pending status across multiple computers, use a database or Google Sheets backend rather than local Streamlit session state.
