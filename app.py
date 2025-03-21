import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io
import cv2
import numpy as np
import svgwrite
from pyzbar.pyzbar import decode
import pandas as pd
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile

# ======================
# Enhanced QR Generation
# ======================

def generate_svg_qr(data, size, fill_color, back_color):
    """Generate QR code in vector SVG format"""
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(size=(f"{size}mm", f"{size}mm"))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=back_color))
    
    # Convert QR matrix to SVG paths
    box_size = size / (qr.modules_count + 2 * qr.border)
    for y in range(qr.modules_count):
        for x in range(qr.modules_count):
            if qr.modules[y][x]:
                dwg.add(dwg.rect(
                    insert=((x + qr.border) * box_size, 
                    (y + qr.border) * box_size),
                    size=(box_size, box_size),
                    fill=fill_color
                ))
    return dwg

def process_bulk_qr(csv_file):
    """Generate multiple QR codes from CSV data"""
    df = pd.read_csv(csv_file)
    if 'data' not in df.columns:
        raise ValueError("CSV must contain 'data' column")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for index, row in df.iterrows():
            qr_img = generate_advanced_qr(
                row['data'], 
                row.get('color', '#000000'),
                row.get('bg_color', '#FFFFFF'),
                300,
                qrcode.ERROR_CORRECT_M,
                None,
                'square'
            )
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            zip_file.writestr(f'qr_{index}.png', img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# ======================
# Improved Helper Functions
# ======================

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_gradient(img, gradient_type, fill, back):
    """Enhanced gradient application with proper color conversion"""
    fill_rgb = hex_to_rgb(fill)
    back_rgb = hex_to_rgb(back)
    
    open_cv_image = np.array(img.convert('RGB'))
    h, w = open_cv_image.shape[:2]
    
    if gradient_type == "radial":
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (w//2, h//2), min(w, h)//2, 255, -1)
        
        gradient = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(3):
            gradient[:, :, i] = np.linspace(
                fill_rgb[i], 
                back_rgb[i], 
                w, 
                dtype=np.uint8
            )
            
        open_cv_image = cv2.bitwise_and(gradient, gradient, mask=mask)
    
    return Image.fromarray(open_cv_image)

# ======================
# Complete Streamlit UI
# ======================

def main():
    st.set_page_config(page_title="Super QR Pro", layout="wide")
    
    # Sidebar Controls
    with st.sidebar:
        st.header("Advanced Settings")
        content_type = st.selectbox(
            "Content Type",
            ["URL", "WiFi", "vCard", "Text", "Bulk"]
        )
        
        # Error Correction
        error_correction = st.selectbox(
            "Error Correction Level",
            ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
            index=1
        )
        ec_map = {
            "L": qrcode.ERROR_CORRECT_L,
            "M": qrcode.ERROR_CORRECT_M,
            "Q": qrcode.ERROR_CORRECT_Q,
            "H": qrcode.ERROR_CORRECT_H
        }
        ec = ec_map[error_correction[0]]
        
        # Advanced Features
        gradient = st.checkbox("Gradient Effect")
        shape = st.selectbox("QR Shape", ["square", "circle", "rounded"])
        logo = st.file_uploader("Center Logo (PNG)", type=["png"])
        
        # Bulk Processing
        if content_type == "Bulk":
            bulk_csv = st.file_uploader("Bulk CSV", type=["csv"])
        else:
            bulk_csv = None

    # Main Interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Configuration")
        
        # Dynamic Content Input
        if content_type == "Bulk":
            st.info("Upload CSV with 'data' column and optional 'color', 'bg_color' columns")
        else:
            if content_type == "URL":
                data = st.text_input("URL", "https://")
                utm_source = st.text_input("UTM Source", "")
                if utm_source:
                    data += f"?utm_source={utm_source}&utm_medium=qr"
            elif content_type == "WiFi":
                ssid = st.text_input("SSID")
                password = st.text_input("Password")
                encryption = st.selectbox("Encryption", ["WPA", "WEP", "nopass"])
                data = generate_wifi_qr(ssid, password, encryption)
            elif content_type == "vCard":
                name = st.text_input("Full Name")
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                data = generate_vcard(name, phone, email)
            else:
                data = st.text_area("Text Content")
        
        # Style Customization
        if content_type != "Bulk":
            fill_color = st.color_picker("Primary Color", "#000000")
            back_color = st.color_picker("Background Color", "#FFFFFF")
            size = st.slider("QR Size (px)", 100, 1000, 300)
            real_time = st.checkbox("Real-time Preview", True)

    with col2:
        st.header("Output")
        
        if content_type == "Bulk":
            if bulk_csv and st.button("Generate Bulk QRs"):
                with st.spinner("Processing batch..."):
                    try:
                        zip_buffer = process_bulk_qr(bulk_csv)
                        st.success(f"Generated {len(pd.read_csv(bulk_csv))} QR codes")
                        st.download_button(
                            label="Download ZIP",
                            data=zip_buffer,
                            file_name="qr_batch.zip",
                            mime="application/zip"
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            if data and (real_time or st.button("Generate QR")):
                with st.spinner("Generating advanced QR code..."):
                    try:
                        qr_img = generate_advanced_qr(
                            data, fill_color, back_color, size, ec,
                            logo, shape, gradient
                        )
                        
                        # Preview
                        st.image(qr_img, use_column_width=True)
                        
                        # Export Options
                        export_format = st.radio("Export Format", ["PNG", "SVG", "PDF"])
                        buf = io.BytesIO()
                        
                        if export_format == "PNG":
                            qr_img.save(buf, format="PNG")
                            mime_type = "image/png"
                        elif export_format == "SVG":
                            dwg = generate_svg_qr(data, size, fill_color, back_color)
                            dwg.saveas(buf)
                            mime_type = "image/svg+xml"
                        else:  # PDF
                            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                                qr_img.save(tmp.name)
                                img = ImageReader(tmp.name)
                                c = canvas.Canvas(buf, pagesize=letter)
                                img_width, img_height = img.getSize()
                                c.drawImage(img, 50, 50, width=img_width, height=img_height)
                                c.save()
                            mime_type = "application/pdf"
                        
                        # Download Button
                        st.download_button(
                            label=f"Download {export_format}",
                            data=buf.getvalue(),
                            file_name=f"qr_code.{export_format.lower()}",
                            mime=mime_type
                        )
                        
                        # Validation
                        decoded = decode(np.array(qr_img.convert('RGB')))
                        if decoded:
                            st.success(f"Decoded content: {decoded[0].data.decode()}")
                        else:
                            st.warning("QR code failed validation scan")
                            
                    except Exception as e:
                        st.error(f"Generation error: {str(e)}")

if __name__ == "__main__":
    main()
