from twilio.rest import Client
import streamlit as st

def send_whatsapp_alert(message):
    try:
        client = Client(
            st.secrets["TWILIO_ACCOUNT_SID"],
            st.secrets["TWILIO_AUTH_TOKEN"]
        )

        msg = client.messages.create(
            from_=st.secrets["TWILIO_WHATSAPP_FROM"],
            to=st.secrets["OWNER_WHATSAPP"],
            body=message
        )

        return True

    except Exception as e:
        st.error(f"WhatsApp Alert Failed: {e}")
        return False
