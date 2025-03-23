import streamlit as st
import qrcode
import cv2
import numpy as np
import pandas as pd
import io
import zipfile
import openai
import firebase_admin
from firebase_admin import firestore
from PIL import Image

# Firebase Setup (Optional for Analytics)
firebase_admin.initialize_app()
db = firestore.client()

# Set OpenAI API Key (Replace with your key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# UI Improvements
st.set_page_config(page_title="QR Code Generator & Scanner", layout="wide")

st.title("📸 QR Code Generator & Scanner")
st.sidebar.header("📌 Choose an Option")
option = st.sidebar.radio("Select an action", ["Generate QR Code", "Bulk QR Generation", "Scan & AI Analysis"])

# QR Code Generator Function
def generate_qr(data, fill_color="black", back_color="white", logo_path=None):
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

    if logo_path:
        logo = Image.open(logo_path).resize((50, 50))
        img.paste(logo, ((img.size[0] - 50) // 2, (img.size[1] - 50) // 2), mask=logo if logo.mode == 'RGBA' else None)

    return img

# Generate QR Code
if option == "Generate QR Code":
    st.subheader("🎨 Customize & Generate QR Code")
    qr_type = st.selectbox("Select QR Type", ["Text/URL", "WiFi", "vCard", "Bitcoin", "Email", "SMS", "Geo Location", "Event"])
    
    qr_data = ""
    if qr_type == "WiFi":
        ssid = st.text_input("WiFi SSID")
        password = st.text_input("WiFi Password")
        security = st.selectbox("Security", ["WPA", "WEP", "None"])
        qr_data = f"WIFI:T:{security};S:{ssid};P:{password};;"
    elif qr_type == "vCard":
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        company = st.text_input("Company")
        qr_data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nORG:{company}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
    elif qr_type == "Bitcoin":
        address = st.text_input("Bitcoin Address")
        amount = st.text_input("Amount (Optional)")
        qr_data = f"bitcoin:{address}?amount={amount}"
    elif qr_type == "Email":
        email = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        body = st.text_area("Body")
        qr_data = f"mailto:{email}?subject={subject}&body={body}"
    elif qr_type == "SMS":
        phone = st.text_input("Phone Number")
        message = st.text_area("Message")
        qr_data = f"sms:{phone}?body={message}"
    elif qr_type == "Geo Location":
        lat = st.text_input("Latitude")
        lon = st.text_input("Longitude")
        qr_data = f"geo:{lat},{lon}"
    elif qr_type == "Event":
        event = st.text_input("Event Name")
        date = st.date_input("Date")
        qr_data = f"BEGIN:VEVENT\nSUMMARY:{event}\nDTSTART:{date}\nEND:VEVENT"
    else:
        qr_data = st.text_input("Enter text or URL")

    fg_color = st.color_picker("Pick QR Code Color", "#000000")
    bg_color = st.color_picker("Pick Background Color", "#FFFFFF")
    logo_file = st.file_uploader("Upload Logo (Optional)", type=["png", "jpg"])

    if st.button("Generate QR Code"):
        logo_path = io.BytesIO(logo_file.read()) if logo_file else None
        qr_img = generate_qr(qr_data, fg_color, bg_color, logo_path)

        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        st.image(qr_img, caption="Your QR Code", use_column_width=True)
        st.download_button("Download QR Code", buf.getvalue(), file_name="qr_code.png", mime="image/png")

        # Save to Firebase Analytics
        doc_ref = db.collection("qr_codes").add({"data": qr_data, "type": qr_type})
        st.success("QR Code saved to Firebase Analytics ✅")

# Bulk QR Code Generation
elif option == "Bulk QR Generation":
    st.subheader("📂 Upload CSV for Bulk QR Code Generation")
    csv_file = st.file_uploader("Upload CSV (Column: 'data')", type=["csv"])

    if csv_file:
        df = pd.read_csv(csv_file)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for index, row in df.iterrows():
                qr_img = generate_qr(row["data"])
                img_buffer = io.BytesIO()
                qr_img.save(img_buffer, format="PNG")
                zip_file.writestr(f"qrcode_{index}.png", img_buffer.getvalue())

        zip_buffer.seek(0)
        st.download_button("Download All QR Codes", zip_buffer, file_name="bulk_qr_codes.zip", mime="application/zip")

# QR Code Scanner & AI Analysis
elif option == "Scan & AI Analysis":
    st.subheader("🔍 Upload QR Code for Analysis")
    uploaded_qr = st.file_uploader("Choose a QR Code", type=["png", "jpg", "jpeg"])

    if uploaded_qr:
        file_bytes = np.asarray(bytearray(uploaded_qr.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        qr_text, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None:
            st.success(f"Decoded Data: {qr_text}")

            if st.button("Generate AI Description"):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": f"Describe this QR Code: {qr_text}"}]
                )
                st.write("AI Description:", response["choices"][0]["message"]["content"])

            # Save Scan Data to Firebase
            db.collection("qr_scans").add({"scanned_data": qr_text})
            st.success("Scan Data saved to Firebase ✅")
        else:
            st.error("No QR Code detected.")
