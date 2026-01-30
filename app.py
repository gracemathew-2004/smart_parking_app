import streamlit as st
from PIL import Image
import time
from twilio.rest import Client

# ===============================
# 🔐 TWILIO CONFIGURATION
# ===============================
# ❗ Replace with YOUR real values
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your_auth_token_here"

# Twilio Sandbox WhatsApp number (DO NOT CHANGE)
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"

# Your WhatsApp number (India example)
OWNER_WHATSAPP = "whatsapp:+91XXXXXXXXXX"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ===============================
# 🚨 ALERT FUNCTION
# ===============================
def send_whatsapp_alert(message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=OWNER_WHATSAPP
        )
        st.success("📲 WhatsApp Alert Sent Successfully!")
    except Exception as e:
        st.error(f"WhatsApp Alert Failed: {e}")

# ===============================
# 🧠 DUMMY SUSPICIOUS ACTIVITY LOGIC
# (Replace later with ML model)
# ===============================
def detect_suspicious_activity(image):
    # ⚠️ DEMO LOGIC
    # Assume every uploaded image is suspicious
    time.sleep(2)
    return True

# ===============================
# 🎨 STREAMLIT UI
# ===============================
st.set_page_config(page_title="Smart Parking & Theft Alert", layout="centered")

st.title("🚗 Smart Parking & Theft Alert System")
st.write("Upload CCTV image to detect suspicious activity and send alert")

# ===============================
# 📤 FILE UPLOAD
# ===============================
uploaded_file = st.file_uploader(
    "Upload CCTV Image",
    type=["jpg", "jpeg", "png"]
)

vehicle_number = st.text_input(
    "Enter Owner Vehicle Number (Example: TN09AB1234)"
)

parking_type = st.selectbox(
    "Select Parking Area Type",
    ["Restricted / No Parking Area", "Authorized Parking Area"]
)

start_monitoring = st.button("🚨 Start Monitoring")

# ===============================
# 🔍 MAIN LOGIC
# ===============================
if uploaded_file is not None and start_monitoring:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded CCTV Image", use_column_width=True)

    st.info("🔍 Monitoring started...")

    suspicious = detect_suspicious_activity(image)

    if suspicious:
        st.error("⚠️ Suspicious Activity Detected!")

        alert_message = f"""
🚨 ALERT: Suspicious Activity Detected!

Vehicle Number: {vehicle_number}
Parking Area: {parking_type}

Please check immediately.
        """

        send_whatsapp_alert(alert_message)

    else:
        st.success("✅ No suspicious activity detected.")

elif start_monitoring and uploaded_file is None:
    st.warning("Please upload an image before starting monitoring.")
