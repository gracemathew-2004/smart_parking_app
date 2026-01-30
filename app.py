# ===============================
# SMART PARKING & THEFT ALERT APP
# ===============================

import streamlit as st
import cv2
import numpy as np
import os
from ultralytics import YOLO
from twilio.rest import Client
from PIL import Image
import tempfile
import time

# -------------------------------
# STREAMLIT CONFIG
# -------------------------------
st.set_page_config(
    page_title="Smart Parking & Theft Alert System",
    layout="wide"
)

st.title("🚗 Smart Parking & Theft Alert System")

# -------------------------------
# LOAD TWILIO SECRETS
# -------------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # whatsapp:+14155238886
OWNER_WHATSAPP = os.getenv("OWNER_WHATSAPP")              # whatsapp:+91xxxxxxxxxx
TWILIO_SMS_FROM = os.getenv("TWILIO_SMS_FROM")            # optional
OWNER_SMS = os.getenv("OWNER_SMS")                        # optional

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, OWNER_WHATSAPP]):
    st.error("❌ Twilio secrets not loaded. Check Streamlit → Settings → Secrets.")
    st.stop()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# -------------------------------
# LOAD YOLO MODEL
# -------------------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")  # lightweight, works on Streamlit Cloud

model = load_model()

# COCO classes considered suspicious near vehicles
SUSPICIOUS_CLASSES = ["person", "knife", "scissors", "backpack"]

# -------------------------------
# ALERT FUNCTIONS
# -------------------------------
def send_whatsapp_alert(message):
    client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=OWNER_WHATSAPP,
        body=message
    )

def send_sms_alert(message):
    if TWILIO_SMS_FROM and OWNER_SMS:
        client.messages.create(
            from_=TWILIO_SMS_FROM,
            to=OWNER_SMS,
            body=message
        )

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("⚙️ Configuration")

owner_vehicle = st.sidebar.text_input(
    "Owner Vehicle Number",
    placeholder="TN09AB1234"
)

parking_type = st.sidebar.selectbox(
    "Parking Area Type",
    ["Authorized Parking Area", "Restricted / No Parking Area"]
)

alert_mode = st.sidebar.multiselect(
    "Alert Mode",
    ["WhatsApp", "SMS"],
    default=["WhatsApp"]
)

monitor_time = st.sidebar.slider(
    "Monitoring Duration (seconds)",
    min_value=10,
    max_value=120,
    value=30
)

# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload CCTV Image or Video",
    type=["jpg", "jpeg", "png", "mp4"]
)

# -------------------------------
# DETECTION LOGIC
# -------------------------------
def detect_suspicious(frame):
    results = model(frame, conf=0.4)
    suspicious_found = False

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            if label in SUSPICIOUS_CLASSES:
                suspicious_found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return suspicious_found, frame

# -------------------------------
# START MONITORING
# -------------------------------
if st.button("▶️ Start Monitoring"):

    if uploaded_file is None:
        st.warning("Please upload an image or video.")
        st.stop()

    st.info("🔍 Monitoring started...")

    suspicious_detected = False

    # ---------- IMAGE ----------
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        frame = np.array(image)

        suspicious_detected, output = detect_suspicious(frame)
        st.image(output, caption="Processed Image", use_column_width=True)

    # ---------- VIDEO ----------
    else:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        cap = cv2.VideoCapture(tfile.name)
        start_time = time.time()

        frame_placeholder = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            suspicious, processed = detect_suspicious(frame)
            if suspicious:
                suspicious_detected = True

            frame_placeholder.image(processed, channels="BGR")

            if time.time() - start_time > monitor_time:
                break

        cap.release()

    # ---------------------------
    # ALERT DECISION
    # ---------------------------
    if suspicious_detected or parking_type == "Restricted / No Parking Area":
        alert_msg = f"""🚨 ALERT!
Suspicious Activity Detected

Vehicle: {owner_vehicle or 'Unknown'}
Area: {parking_type}

Immediate attention required.
"""

        if "WhatsApp" in alert_mode:
            send_whatsapp_alert(alert_msg)

        if "SMS" in alert_mode:
            send_sms_alert(alert_msg)

        st.error("🚨 Suspicious Activity Detected! Alert Sent.")

    else:
        st.success("✅ No suspicious activity detected.")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("AI-based Smart Parking & Theft Detection System")
