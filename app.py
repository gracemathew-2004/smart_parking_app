# =========================
# SMART PARKING & THEFT ALERT SYSTEM
# =========================

import streamlit as st
import cv2
import numpy as np
import time
import pytesseract
from ultralytics import YOLO
from twilio.rest import Client
from PIL import Image

# =========================
# CONFIG
# =========================
SUSPICIOUS_TIME_LIMIT = 30  # seconds

# =========================
# LOAD YOLO MODEL
# =========================
@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt")   # lightweight, works on Streamlit Cloud

model = load_yolo()

# =========================
# TWILIO FUNCTIONS
# =========================
def send_whatsapp_alert(message):
    client = Client(
        st.secrets["TWILIO_ACCOUNT_SID"],
        st.secrets["TWILIO_AUTH_TOKEN"]
    )
    client.messages.create(
        from_=st.secrets["TWILIO_WHATSAPP_FROM"],
        to=st.secrets["OWNER_WHATSAPP"],
        body=message
    )

def send_sms_alert(message):
    client = Client(
        st.secrets["TWILIO_ACCOUNT_SID"],
        st.secrets["TWILIO_AUTH_TOKEN"]
    )
    client.messages.create(
        from_=st.secrets["TWILIO_SMS_FROM"],
        to=st.secrets["OWNER_SMS"],
        body=message
    )

# =========================
# OCR – NUMBER PLATE
# =========================
def read_number_plate(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    text = pytesseract.image_to_string(gray, config="--psm 7")
    return text.strip().replace(" ", "")

# =========================
# SUSPICIOUS ACTIVITY LOGIC
# =========================
def detect_suspicious(objects):
    suspicious_items = ["person", "knife", "stick", "crowbar"]
    for obj in objects:
        if obj in suspicious_items:
            return True
    return False

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Smart Parking & Theft Alert", layout="wide")
st.title("🚗 Smart Parking & Theft Alert System")

uploaded_file = st.file_uploader(
    "Upload CCTV Image / Video",
    type=["jpg", "png", "jpeg", "mp4"]
)

owner_vehicle_number = st.text_input("Enter OWNER Vehicle Number", placeholder="TN09AB1234")

parking_type = st.selectbox(
    "Select Parking Area Type",
    ["Authorized Parking Area", "Restricted / No Parking Area"]
)

start_btn = st.button("▶ Start Monitoring")

# =========================
# PROCESSING
# =========================
if start_btn and uploaded_file:

    st.info("Monitoring started...")
    start_time = time.time()
    alert_sent = False

    # -------------------------
    # IMAGE MODE
    # -------------------------
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file).convert("RGB")
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        results = model(frame)[0]
        detected_classes = []

        for box in results.boxes:
            cls = int(box.cls[0])
            detected_classes.append(model.names[cls])

        plate_text = read_number_plate(frame)

        # AUTHORIZED / UNAUTHORIZED
        if parking_type == "Restricted / No Parking Area":
            st.error("❌ Unauthorized Parking Detected")
            send_whatsapp_alert("🚨 Unauthorized parking detected!")
            send_sms_alert("Unauthorized parking detected!")
            alert_sent = True

        # OWNER VEHICLE CHECK
        if owner_vehicle_number and owner_vehicle_number in plate_text:
            st.success("✅ Owner vehicle detected – No alert")
        else:
            st.warning("⚠ Unknown vehicle detected")

        # SUSPICIOUS ACTIVITY TIMER
        while time.time() - start_time < SUSPICIOUS_TIME_LIMIT:
            if detect_suspicious(detected_classes):
                st.error("⚠ Suspicious activity detected!")
                send_whatsapp_alert("🚨 Suspicious activity near vehicle!")
                send_sms_alert("Suspicious activity detected!")
                alert_sent = True
                break
            time.sleep(1)

        if not alert_sent:
            st.success("✅ Monitoring completed – No threats detected")

    # -------------------------
    # VIDEO MODE (BASIC)
    # -------------------------
    else:
        st.warning("Video support is limited on cloud. Use image for best results.")
        send_whatsapp_alert("ℹ Video uploaded. Please review manually.")
        send_sms_alert("Video uploaded for monitoring.")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("AI-based Smart Parking & Theft Alert System")
