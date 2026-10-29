# Quick Deployment Checklist

## GitHub
- Create a new PRIVATE repository, e.g. `liberty-dealer-payment-system`
- Upload:
  - app.py
  - requirements.txt
  - README.md
  - data/dealers.csv
  - .streamlit/config.toml

## Streamlit Community Cloud
- Sign in with GitHub
- Create app
- Select your private repository
- Main file: `app.py`
- Deploy

## Password
In Streamlit app settings -> Secrets, add:

APP_PASSWORD = "CHANGE-THIS-PASSWORD"

Save, then reboot the app.

## WhatsApp
Each dealer has a `SEND WHATSAPP` button. It opens WhatsApp Web with the dealer's number and personalized reminder. The operator presses Send.
