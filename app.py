import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from twilio.rest import Client
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Smart Parking & Theft Alert System",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Smart Parking & Theft Alert System")
st.write("YOLO-based vehicle monitoring with SMS & WhatsApp alerts")

# ------------------ LOAD YOLO MODEL ------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")  # lightweight & fast

model = load_model()

# ------------------ TWILIO CLIENT ------------------
client = Client(
    st.secrets["TWILIO_ACCOUNT_SID"],
    st.secrets["TWILIO_AUTH_TOKEN"]
)

# ------------------ ALERT FUNCTIONS ------------------
def send_whatsapp_alert(message):
    try:
        client.messages.create(
            from_=st.secrets["TWILIO_WHATSAPP_FROM"],
            to=st.secrets["OWNER_WHATSAPP"],
            body=message
        )
        st.success("✅ WhatsApp alert sent")
    except Exception as e:
        st.error(f"❌ WhatsApp alert failed: {e}")

def send_sms_alert(message):
    try:
        client.messages.create(
            from_=st.secrets["TWILIO_SMS_FROM"],
            to=st.secrets["OWNER_SMS"],
            body=message
        )
        st.success("✅ SMS alert sent")
    except Exception as e:
        st.error(f"❌ SMS alert failed: {e}")

# ------------------ FILE UPLOAD ------------------
st.subheader("📤 Upload CCTV Image")
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)

owner_vehicle_number = st.text_input(
    "Enter OWNER Vehicle Number (Example: TN09AB1234)"
)

area_type = st.selectbox(
    "Select Parking Area Type",
    ["Normal Parking Area", "Restricted / No Parking Area"]
)

start = st.button("▶ Start Monitoring")

# ------------------ MAIN LOGIC ------------------
if start and uploaded_file is not None and owner_vehicle_number != "":
    st.info("🔍 Monitoring started...")
    
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    results = model(img_array)
    annotated_img = results[0].plot()

    st.image(annotated_img, caption="Processed CCTV Image", use_column_width=True)

    detected_classes = results[0].boxes.cls.tolist()
    class_names = results[0].names

    vehicles_detected = [
        class_names[int(cls)]
        for cls in detected_classes
        if class_names[int(cls)] in ["car", "motorcycle", "bus", "truck"]
    ]

    st.write("### 🚘 Detected Vehicles:")
    st.write(vehicles_detected if vehicles_detected else "No vehicles detected")

    suspicious = False
    reason = ""

    if area_type == "Restricted / No Parking Area" and len(vehicles_detected) > 0:
        suspicious = True
        reason = "Vehicle detected in RESTRICTED area"

    if len(vehicles_detected) > 0:
        suspicious = True
        reason = "Vehicle movement detected near parking area"

    # ------------------ ALERT ------------------
    if suspicious:
        st.warning("⚠ Suspicious Activity Detected!")

        alert_message = f"""
🚨 THEFT ALERT 🚨

Vehicle Number: {owner_vehicle_number}
Reason: {reason}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

Immediate action required!
"""

        send_whatsapp_alert(alert_message)
        send_sms_alert(alert_message)

    else:
        st.success("✅ No suspicious activity detected")

elif start:
    st.error("❗ Please upload an image and enter vehicle number")
