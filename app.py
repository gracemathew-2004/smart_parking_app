import streamlit as st
from PIL import Image
import time
from twilio.rest import Client
from ultralytics import YOLO

# ===============================
# 🔐 TWILIO CONFIGURATION
# ===============================
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your_auth_token_here"

TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"   # Twilio sandbox
TWILIO_SMS_FROM = "+1XXXXXXXXXX"                 # Twilio SMS number

OWNER_WHATSAPP = "whatsapp:+91XXXXXXXXXX"
OWNER_SMS = "+91XXXXXXXXXX"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ===============================
# 📲 ALERT FUNCTIONS
# ===============================
def send_whatsapp_alert(message):
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_FROM,
        to=OWNER_WHATSAPP
    )

def send_sms_alert(message):
    client.messages.create(
        body=message,
        from_=TWILIO_SMS_FROM,
        to=OWNER_SMS
    )

# ===============================
# 🧠 LOAD YOLO MODEL
# ===============================
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")   # lightweight YOLO model

model = load_model()

# ===============================
# 🔍 THEFT DETECTION LOGIC
# ===============================
def detect_theft(image):
    results = model(image)

    detected_objects = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            detected_objects.append(label)

    # 🚨 Simple theft logic
    suspicious_objects = ["person", "knife", "scissors", "backpack"]

    for obj in detected_objects:
        if obj in suspicious_objects:
            return True, detected_objects

    return False, detected_objects

# ===============================
# 🎨 STREAMLIT UI
# ===============================
st.set_page_config(page_title="Smart Parking & Theft Alert", layout="centered")

st.title("🚗 Smart Parking & Theft Alert System (ML Powered)")
st.caption("YOLO-based theft detection with SMS & WhatsApp alerts")

uploaded_file = st.file_uploader(
    "📤 Upload CCTV Image",
    type=["jpg", "jpeg", "png"]
)

vehicle_number = st.text_input(
    "🚘 Owner Vehicle Number (Example: TN09AB1234)"
)

parking_type = st.selectbox(
    "🅿️ Parking Area Type",
    ["Restricted / No Parking Area", "Authorized Parking Area"]
)

start = st.button("🚨 Start Monitoring")

# ===============================
# 🚀 MAIN PIPELINE
# ===============================
if start:

    if uploaded_file is None:
        st.warning("Please upload a CCTV image.")
        st.stop()

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded CCTV Image", use_column_width=True)

    with st.spinner("🔍 Analyzing image using YOLO..."):
        time.sleep(2)
        suspicious, objects = detect_theft(image)

    st.write("### 🔎 Detected Objects:")
    st.write(objects)

    if suspicious:
        st.error("🚨 THEFT / SUSPICIOUS ACTIVITY DETECTED!")

        alert_msg = f"""
🚨 SMART PARKING ALERT 🚨

Suspicious Activity Detected!

Vehicle Number: {vehicle_number}
Parking Area: {parking_type}
Detected Objects: {objects}

Please take immediate action.
        """

        send_whatsapp_alert(alert_msg)
        send_sms_alert(alert_msg)

        st.success("📲 Alert sent via WhatsApp & SMS")

    else:
        st.success("✅ No suspicious activity detected")
