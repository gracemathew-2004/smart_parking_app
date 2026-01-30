import streamlit as st
import time
from twilio.rest import Client

# ---------------- CONFIG ----------------
SUSPICIOUS_TIME = 30  # seconds

# Twilio credentials (from Streamlit Secrets)
ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox number
TO_WHATSAPP = st.secrets["OWNER_WHATSAPP"]  # your WhatsApp number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---------------- FUNCTIONS ----------------
def send_whatsapp_alert(vehicle_no):
    message = f"🚨 ALERT!\nSuspicious activity detected near vehicle: {vehicle_no}"
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )

# ---------------- UI ----------------
st.set_page_config(page_title="Smart Parking & Theft Alert", layout="centered")
st.title("🚗 Smart Parking & Theft Alert System")

st.markdown("### Upload CCTV Image / Video")
uploaded_file = st.file_uploader("Upload file", type=["jpg", "png", "mp4"])

vehicle_no = st.text_input("Enter OWNER Vehicle Number (Example: TN09AB1234)")

area_type = st.selectbox(
    "Select Parking Area Type",
    ["Authorized Parking Area", "Restricted / No Parking Area"]
)

start_monitor = st.button("Start Monitoring")

# ---------------- LOGIC ----------------
if start_monitor and uploaded_file and vehicle_no:
    st.success("Monitoring started...")
    timer_placeholder = st.empty()

    start_time = time.time()

    while True:
        elapsed = int(time.time() - start_time)
        timer_placeholder.info(f"⏱ Time elapsed: {elapsed} seconds")

        if area_type == "Restricted / No Parking Area" and elapsed >= SUSPICIOUS_TIME:
            st.error("🚨 Suspicious Activity Detected!")
            send_whatsapp_alert(vehicle_no)
            st.success("WhatsApp Alert Sent to Owner!")
            break

        if elapsed >= SUSPICIOUS_TIME:
            st.success("✅ No suspicious activity. Authorized behavior.")
            break

        time.sleep(1)

else:
    st.warning("Please upload file and enter vehicle number.")
