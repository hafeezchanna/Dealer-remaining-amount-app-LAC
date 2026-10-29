
import io
import re
from urllib.parse import quote
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Liberty Agro Chemicals – Dealer Payment Reminder",
    page_icon="💳",
    layout="wide",
)

st.markdown("""
<style>
:root {
    --lac-green: #1f6b3a;
    --lac-gold: #c99a2e;
}
.main-title {
    text-align: center;
    color: var(--lac-green);
    font-size: 2.1rem;
    font-weight: 800;
    margin-bottom: 0.1rem;
}
.sub-title {
    text-align: center;
    color: #8b6a20;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.card {
    border: 1px solid #d9d9d9;
    border-radius: 12px;
    padding: 14px;
    background: #ffffff;
}
.small-muted {
    color: #666;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")

def login_gate():
    if not APP_PASSWORD:
        return True
    if st.session_state.get("authenticated"):
        return True
    st.markdown('<div class="main-title">LIBERTY AGRO CHEMICALS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Dealer Payment Reminder System</div>', unsafe_allow_html=True)
    pwd = st.text_input("Enter app password", type="password")
    if st.button("Login", type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

login_gate()

st.markdown('<div class="main-title">LIBERTY AGRO CHEMICALS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Dealer Payment Reminder System • Sukkur</div>', unsafe_allow_html=True)

DATA_FILE = "data/dealers.csv"

@st.cache_data
def load_default():
    df = pd.read_csv(DATA_FILE, dtype=str)
    for c in ["Debit", "Credit", "Remaining Amount"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def normalize_mobile(v):
    if pd.isna(v):
        return ""
    s = re.sub(r"\D", "", str(v))
    if s.startswith("92"):
        return s
    if s.startswith("0") and len(s) >= 10:
        return "92" + s[1:]
    if len(s) == 10 and s.startswith("3"):
        return "92" + s
    return s

def message_for(row):
    name = str(row.get("Dealer Name", "")).strip() or "Dealer"
    amount = float(row.get("Remaining Amount", 0) or 0)
    amount_txt = f"{amount:,.0f}"
    return (
        f"Assalam-o-Alaikum {name},\n\n"
        "LIBERTY AGRO CHEMICALS\n"
        "Payment Reminder / Account Reference\n\n"
        f"According to our ledger, your remaining outstanding balance is Rs. {amount_txt}/-.\n\n"
        "Kindly clear the outstanding payment at your earliest convenience "
        "and share the payment confirmation with us.\n\n"
        "Thank you for your cooperation.\n\n"
        "Regards,\n"
        "Liberty Agro Chemicals\n"
        "Sukkur"
    )

def whatsapp_url(row):
    phone = normalize_mobile(row.get("Mobile", ""))
    msg = quote(message_for(row))
    if not phone:
        return ""
    return f"https://web.whatsapp.com/send?phone={phone}&text={msg}"

def clean_imported(df):
    aliases = {
        "A/c No": ["A/c No", "A/C No", "Account No", "Account Number", "A/c"],
        "Dealer Name": ["Dealer Name", "Dealer", "Name", "Customer Name"],
        "Mobile": ["Mobile", "Mobile No", "Phone", "Contact", "Cell"],
        "Debit": ["Debit", "Dr", "Debit Amount"],
        "Credit": ["Credit", "Cr", "Credit Amount"],
        "Remaining Amount": ["Remaining Amount", "Balance", "Outstanding", "Remaining", "Net Balance"],
    }
    out = pd.DataFrame()
    for target, names in aliases.items():
        found = next((n for n in names if n in df.columns), None)
        out[target] = df[found] if found else ""
    for c in ["Debit", "Credit", "Remaining Amount"]:
        out[c] = pd.to_numeric(
            out[c].astype(str).str.replace(",", "", regex=False).str.replace("Rs.", "", regex=False),
            errors="coerce"
        ).fillna(0)
    if (out["Remaining Amount"] <= 0).all() and "Debit" in out.columns and "Credit" in out.columns:
        out["Remaining Amount"] = out["Debit"] - out["Credit"]
    out = out[out["Remaining Amount"] > 0].copy()
    return out.reset_index(drop=True)

df = load_default()

with st.sidebar:
    st.header("Control Panel")
    search = st.text_input("Search dealer / mobile / A/c", "")
    status = st.selectbox("Filter", ["All Outstanding", "With Mobile", "Missing Mobile"])
    st.divider()
    st.subheader("Update Ledger")
    uploaded = st.file_uploader(
        "Upload PDF, Excel or CSV",
        type=["pdf", "xlsx", "xls", "csv"],
        help="For best results use Excel/CSV with dealer, mobile, debit, credit and balance columns."
    )
    if uploaded:
        name = uploaded.name.lower()
        try:
            if name.endswith(".csv"):
                new_df = clean_imported(pd.read_csv(uploaded, dtype=str))
                if len(new_df):
                    df = new_df
                    st.success(f"Loaded {len(df)} outstanding dealers.")
                else:
                    st.error("No positive outstanding balances were detected.")
            elif name.endswith((".xlsx", ".xls")):
                new_df = clean_imported(pd.read_excel(uploaded, dtype=str))
                if len(new_df):
                    df = new_df
                    st.success(f"Loaded {len(df)} outstanding dealers.")
                else:
                    st.error("No positive outstanding balances were detected.")
            else:
                st.warning("PDF upload is supported for future parser expansion. For this release, upload the ledger as Excel/CSV for reliable column matching.")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    st.caption("WhatsApp messages are prepared in your browser. WhatsApp still requires the user to press Send; this app does not silently bulk-send messages.")

if search:
    q = search.lower()
    mask = (
        df["Dealer Name"].astype(str).str.lower().str.contains(q, na=False)
        | df["Mobile"].astype(str).str.lower().str.contains(q, na=False)
        | df["A/c No"].astype(str).str.lower().str.contains(q, na=False)
    )
    view = df[mask].copy()
else:
    view = df.copy()

if status == "With Mobile":
    view = view[view["Mobile"].astype(str).str.strip() != ""]
elif status == "Missing Mobile":
    view = view[view["Mobile"].astype(str).str.strip() == ""]

total = float(df["Remaining Amount"].sum())
count = len(df)
with_mobile = int((df["Mobile"].astype(str).str.strip() != "").sum())

c1, c2, c3 = st.columns(3)
c1.metric("Outstanding Dealers", f"{count:,}")
c2.metric("Total Outstanding", f"Rs. {total:,.0f}")
c3.metric("Dealers With Mobile", f"{with_mobile:,}")

st.info("Tip: use the search box to find a dealer, then click **SEND WHATSAPP**. The message opens in WhatsApp Web with the exact outstanding amount already filled.")

st.subheader("Dealer Payment Reminders")

# Avoid a huge table with HTML forms. Use a compact, reliable row-by-row workflow.
display_cols = ["A/c No", "Dealer Name", "Mobile", "Remaining Amount"]
for idx, row in view.reset_index(drop=True).iterrows():
    amount = float(row["Remaining Amount"])
    mobile = normalize_mobile(row["Mobile"])
    left, mid, amount_col, action = st.columns([1.0, 3.0, 1.5, 1.4])
    with left:
        st.write(str(row["A/c No"]))
    with mid:
        st.write(f"**{row['Dealer Name']}**")
        st.caption(str(row["Mobile"]) if str(row["Mobile"]).strip() else "No mobile number")
    with amount_col:
        st.write(f"**Rs. {amount:,.0f}**")
    with action:
        url = whatsapp_url(row)
        if url:
            st.link_button("SEND WHATSAPP", url, use_container_width=True)
        else:
            st.button("NO MOBILE", disabled=True, key=f"nomobile_{idx}", use_container_width=True)
    with st.expander(f"View message — {row['Dealer Name']}"):
        st.text_area(
            "Personalized message",
            message_for(row),
            height=210,
            key=f"msg_{idx}",
        )
    st.divider()

st.caption(
    "Current starter dataset: the uploaded Liberty Agro Chemicals dealer ledger dated 29-Oct-2026. "
    "Only positive outstanding balances are shown."
)
