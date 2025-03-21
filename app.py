# import streamlit as st
# import qrcode
# from PIL import Image, ImageDraw
# import io
# import cv2
# import numpy as np
# import svgwrite
# from pyzbar.pyzbar import decode
# import pandas as pd
# import zipfile
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# import tempfile

# # ======================
# # Enhanced QR Generation
# # ======================

# def generate_svg_qr(data, size, fill_color, back_color):
#     """Generate QR code in vector SVG format"""
#     qr = qrcode.QRCode(version=1, box_size=10, border=1)
#     qr.add_data(data)
#     qr.make(fit=True)
    
#     # Create SVG drawing
#     dwg = svgwrite.Drawing(size=(f"{size}mm", f"{size}mm"))
#     dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=back_color))
    
#     # Convert QR matrix to SVG paths
#     box_size = size / (qr.modules_count + 2 * qr.border)
#     for y in range(qr.modules_count):
#         for x in range(qr.modules_count):
#             if qr.modules[y][x]:
#                 dwg.add(dwg.rect(
#                     insert=((x + qr.border) * box_size, 
#                     (y + qr.border) * box_size),
#                     size=(box_size, box_size),
#                     fill=fill_color
#                 ))
#     return dwg

# def process_bulk_qr(csv_file):
#     """Generate multiple QR codes from CSV data"""
#     df = pd.read_csv(csv_file)
#     if 'data' not in df.columns:
#         raise ValueError("CSV must contain 'data' column")
    
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
#         for index, row in df.iterrows():
#             qr_img = generate_advanced_qr(
#                 row['data'], 
#                 row.get('color', '#000000'),
#                 row.get('bg_color', '#FFFFFF'),
#                 300,
#                 qrcode.ERROR_CORRECT_M,
#                 None,
#                 'square'
#             )
#             img_buffer = io.BytesIO()
#             qr_img.save(img_buffer, format='PNG')
#             zip_file.writestr(f'qr_{index}.png', img_buffer.getvalue())
    
#     zip_buffer.seek(0)
#     return zip_buffer

# # ======================
# # Improved Helper Functions
# # ======================

# def hex_to_rgb(hex_color):
#     """Convert hex color to RGB tuple"""
#     hex_color = hex_color.lstrip('#')
#     return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# def apply_gradient(img, gradient_type, fill, back):
#     """Enhanced gradient application with proper color conversion"""
#     fill_rgb = hex_to_rgb(fill)
#     back_rgb = hex_to_rgb(back)
    
#     open_cv_image = np.array(img.convert('RGB'))
#     h, w = open_cv_image.shape[:2]
    
#     if gradient_type == "radial":
#         mask = np.zeros((h, w), dtype=np.uint8)
#         cv2.circle(mask, (w//2, h//2), min(w, h)//2, 255, -1)
        
#         gradient = np.zeros((h, w, 3), dtype=np.uint8)
#         for i in range(3):
#             gradient[:, :, i] = np.linspace(
#                 fill_rgb[i], 
#                 back_rgb[i], 
#                 w, 
#                 dtype=np.uint8
#             )
            
#         open_cv_image = cv2.bitwise_and(gradient, gradient, mask=mask)
    
#     return Image.fromarray(open_cv_image)

# # ======================
# # Complete Streamlit UI
# # ======================

# def main():
#     st.set_page_config(page_title="Super QR Pro", layout="wide")
    
#     # Sidebar Controls
#     with st.sidebar:
#         st.header("Advanced Settings")
#         content_type = st.selectbox(
#             "Content Type",
#             ["URL", "WiFi", "vCard", "Text", "Bulk"]
#         )
        
#         # Error Correction
#         error_correction = st.selectbox(
#             "Error Correction Level",
#             ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
#             index=1
#         )
#         ec_map = {
#             "L": qrcode.ERROR_CORRECT_L,
#             "M": qrcode.ERROR_CORRECT_M,
#             "Q": qrcode.ERROR_CORRECT_Q,
#             "H": qrcode.ERROR_CORRECT_H
#         }
#         ec = ec_map[error_correction[0]]
        
#         # Advanced Features
#         gradient = st.checkbox("Gradient Effect")
#         shape = st.selectbox("QR Shape", ["square", "circle", "rounded"])
#         logo = st.file_uploader("Center Logo (PNG)", type=["png"])
        
#         # Bulk Processing
#         if content_type == "Bulk":
#             bulk_csv = st.file_uploader("Bulk CSV", type=["csv"])
#         else:
#             bulk_csv = None

#     # Main Interface
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.header("Configuration")
        
#         # Dynamic Content Input
#         if content_type == "Bulk":
#             st.info("Upload CSV with 'data' column and optional 'color', 'bg_color' columns")
#         else:
#             if content_type == "URL":
#                 data = st.text_input("URL", "https://")
#                 utm_source = st.text_input("UTM Source", "")
#                 if utm_source:
#                     data += f"?utm_source={utm_source}&utm_medium=qr"
#             elif content_type == "WiFi":
#                 ssid = st.text_input("SSID")
#                 password = st.text_input("Password")
#                 encryption = st.selectbox("Encryption", ["WPA", "WEP", "nopass"])
#                 data = generate_wifi_qr(ssid, password, encryption)
#             elif content_type == "vCard":
#                 name = st.text_input("Full Name")
#                 phone = st.text_input("Phone")
#                 email = st.text_input("Email")
#                 data = generate_vcard(name, phone, email)
#             else:
#                 data = st.text_area("Text Content")
        
#         # Style Customization
#         if content_type != "Bulk":
#             fill_color = st.color_picker("Primary Color", "#000000")
#             back_color = st.color_picker("Background Color", "#FFFFFF")
#             size = st.slider("QR Size (px)", 100, 1000, 300)
#             real_time = st.checkbox("Real-time Preview", True)

#     with col2:
#         st.header("Output")
        
#         if content_type == "Bulk":
#             if bulk_csv and st.button("Generate Bulk QRs"):
#                 with st.spinner("Processing batch..."):
#                     try:
#                         zip_buffer = process_bulk_qr(bulk_csv)
#                         st.success(f"Generated {len(pd.read_csv(bulk_csv))} QR codes")
#                         st.download_button(
#                             label="Download ZIP",
#                             data=zip_buffer,
#                             file_name="qr_batch.zip",
#                             mime="application/zip"
#                         )
#                     except Exception as e:
#                         st.error(f"Error: {str(e)}")
#         else:
#             if data and (real_time or st.button("Generate QR")):
#                 with st.spinner("Generating advanced QR code..."):
#                     try:
#                         qr_img = generate_advanced_qr(
#                             data, fill_color, back_color, size, ec,
#                             logo, shape, gradient
#                         )
                        
#                         # Preview
#                         st.image(qr_img, use_column_width=True)
                        
#                         # Export Options
#                         export_format = st.radio("Export Format", ["PNG", "SVG", "PDF"])
#                         buf = io.BytesIO()
                        
#                         if export_format == "PNG":
#                             qr_img.save(buf, format="PNG")
#                             mime_type = "image/png"
#                         elif export_format == "SVG":
#                             dwg = generate_svg_qr(data, size, fill_color, back_color)
#                             dwg.saveas(buf)
#                             mime_type = "image/svg+xml"
#                         else:  # PDF
#                             with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
#                                 qr_img.save(tmp.name)
#                                 img = ImageReader(tmp.name)
#                                 c = canvas.Canvas(buf, pagesize=letter)
#                                 img_width, img_height = img.getSize()
#                                 c.drawImage(img, 50, 50, width=img_width, height=img_height)
#                                 c.save()
#                             mime_type = "application/pdf"
                        
#                         # Download Button
#                         st.download_button(
#                             label=f"Download {export_format}",
#                             data=buf.getvalue(),
#                             file_name=f"qr_code.{export_format.lower()}",
#                             mime=mime_type
#                         )
                        
#                         # Validation
#                         decoded = decode(np.array(qr_img.convert('RGB')))
#                         if decoded:
#                             st.success(f"Decoded content: {decoded[0].data.decode()}")
#                         else:
#                             st.warning("QR code failed validation scan")
                            
#                     except Exception as e:
#                         st.error(f"Generation error: {str(e)}")

# if __name__ == "__main__":
#     main()



































# import streamlit as st
# import qrcode
# from PIL import Image, ImageDraw
# import io
# import numpy as np
# import svgwrite
# from pyzbar.pyzbar import decode
# import pandas as pd
# import zipfile
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# import tempfile

# # ======================

# def generate_advanced_qr(data, fill_color, back_color, size, ec, logo=None, shape="square", gradient=False):
#     """Generate a customized QR code."""
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=ec,
#         box_size=10,
#         border=1
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
    
#     # Create Image object for QR code
#     img = qr.make_image(fill=fill_color, back_color=back_color)
    
#     if logo:
#         logo_img = Image.open(logo)
#         # Optional: place logo in the center
#         logo_size = int(img.size[0] / 4)  # Set logo size (1/4th of QR)
#         logo_img.thumbnail((logo_size, logo_size))
#         logo_pos = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
#         img.paste(logo_img, logo_pos, logo_img.convert('RGBA'))
    
#     if gradient:
#         img = apply_gradient(img, "radial", fill_color, back_color)
    
#     return img

# # ======================

# def generate_wifi_qr(ssid, password, encryption):
#     """Generate WiFi QR Code"""
#     if encryption == "nopass":
#         data = f"WIFI:T:;S:{ssid};;"
#     else:
#         data = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
#     return generate_advanced_qr(data, "#000000", "#FFFFFF", 300, qrcode.ERROR_CORRECT_M)

# # ======================

# def generate_vcard(name, phone, email):
#     """Generate vCard QR Code"""
#     vcard_data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
#     return generate_advanced_qr(vcard_data, "#000000", "#FFFFFF", 300, qrcode.ERROR_CORRECT_M)

# # ======================

# def process_bulk_qr(csv_file):
#     """Generate multiple QR codes from CSV data"""
#     df = pd.read_csv(csv_file)
#     if 'data' not in df.columns:
#         raise ValueError("CSV must contain 'data' column")
    
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
#         for index, row in df.iterrows():
#             qr_img = generate_advanced_qr(
#                 row['data'], 
#                 row.get('color', '#000000'),
#                 row.get('bg_color', '#FFFFFF'),
#                 300,
#                 qrcode.ERROR_CORRECT_M,
#                 None,
#                 'square'
#             )
#             img_buffer = io.BytesIO()
#             qr_img.save(img_buffer, format='PNG')
#             zip_file.writestr(f'qr_{index}.png', img_buffer.getvalue())
    
#     zip_buffer.seek(0)
#     return zip_buffer

# # ======================

# def main():
#     st.set_page_config(page_title="Super QR Pro", layout="wide")
    
#     # Sidebar Controls
#     with st.sidebar:
#         st.header("Advanced Settings")
#         content_type = st.selectbox(
#             "Content Type",
#             ["URL", "WiFi", "vCard", "Text", "Bulk"]
#         )
        
#         # Error Correction
#         error_correction = st.selectbox(
#             "Error Correction Level",
#             ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
#             index=1
#         )
#         ec_map = {
#             "L": qrcode.ERROR_CORRECT_L,
#             "M": qrcode.ERROR_CORRECT_M,
#             "Q": qrcode.ERROR_CORRECT_Q,
#             "H": qrcode.ERROR_CORRECT_H
#         }
#         ec = ec_map[error_correction[0]]
        
#         # Advanced Features
#         gradient = st.checkbox("Gradient Effect")
#         shape = st.selectbox("QR Shape", ["square", "circle", "rounded"])
#         logo = st.file_uploader("Center Logo (PNG)", type=["png"])
        
#         # Bulk Processing
#         if content_type == "Bulk":
#             bulk_csv = st.file_uploader("Bulk CSV", type=["csv"])
#         else:
#             bulk_csv = None

#     # Main Interface
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.header("Configuration")
        
#         # Dynamic Content Input
#         if content_type == "Bulk":
#             st.info("Upload CSV with 'data' column and optional 'color', 'bg_color' columns")
#         else:
#             if content_type == "URL":
#                 data = st.text_input("URL", "https://")
#                 utm_source = st.text_input("UTM Source", "")
#                 if utm_source:
#                     data += f"?utm_source={utm_source}&utm_medium=qr"
#             elif content_type == "WiFi":
#                 ssid = st.text_input("SSID")
#                 password = st.text_input("Password")
#                 encryption = st.selectbox("Encryption", ["WPA", "WEP", "nopass"])
#                 data = generate_wifi_qr(ssid, password, encryption)
#             elif content_type == "vCard":
#                 name = st.text_input("Full Name")
#                 phone = st.text_input("Phone")
#                 email = st.text_input("Email")
#                 data = generate_vcard(name, phone, email)
#             else:
#                 data = st.text_area("Text Content")
        
#         # Style Customization
#         if content_type != "Bulk":
#             fill_color = st.color_picker("Primary Color", "#000000")
#             back_color = st.color_picker("Background Color", "#FFFFFF")
#             size = st.slider("QR Size (px)", 100, 1000, 300)
#             real_time = st.checkbox("Real-time Preview", True)

#     with col2:
#         st.header("Output")
        
#         if content_type == "Bulk":
#             if bulk_csv and st.button("Generate Bulk QRs"):
#                 with st.spinner("Processing batch..."):
#                     try:
#                         zip_buffer = process_bulk_qr(bulk_csv)
#                         st.success(f"Generated {len(pd.read_csv(bulk_csv))} QR codes")
#                         st.download_button(
#                             label="Download ZIP",
#                             data=zip_buffer,
#                             file_name="qr_batch.zip",
#                             mime="application/zip"
#                         )
#                     except Exception as e:
#                         st.error(f"Error: {str(e)}")
#         else:
#             if data and (real_time or st.button("Generate QR")):
#                 with st.spinner("Generating advanced QR code..."):
#                     try:
#                         qr_img = generate_advanced_qr(
#                             data, fill_color, back_color, size, ec,
#                             logo, shape, gradient
#                         )
                        
#                         # Preview
#                         st.image(qr_img, use_column_width=True)
                        
#                         # Export Options
#                         export_format = st.radio("Export Format", ["PNG", "SVG", "PDF"])


# # Add other code handling to finish up as needed.






import streamlit as st
import qrcode
from PIL import Image
import io

# Function to generate QR code
def generate_qr_code(data, version=1, box_size=10, border=5, logo=None):
    qr = qrcode.QRCode(
        version=version,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,  # Controls the pixel size of each box
        border=border,  # Controls the thickness of the border
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    if logo:
        # Add logo to the center
        logo = Image.open(logo)
        logo = logo.convert("RGBA")
        img = img.convert("RGBA")
        img.paste(logo, (int((img.width - logo.width) / 2), int((img.height - logo.height) / 2)), logo)

    return img

# Streamlit app
st.title("Powerful QR Code Generator")

st.markdown("""
This is a powerful QR Code Generator that supports customizations such as logos, QR code size, and error correction levels. 
You can also download your QR Code as an image.
""")

# User inputs
data = st.text_input("Enter Data for QR Code:", "https://www.example.com")
version = st.slider("QR Code Version (size):", min_value=1, max_value=40, value=1)
box_size = st.slider("Box Size:", min_value=5, max_value=20, value=10)
border = st.slider("Border Size:", min_value=1, max_value=10, value=5)

logo = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])

# Generate QR code
if st.button("Generate QR Code"):
    if data:
        qr_image = generate_qr_code(data, version, box_size, border, logo)

        # Show the QR code
        st.image(qr_image, caption="Generated QR Code", use_column_width=True)

        # Convert to bytes for download
        buf = io.BytesIO()
        qr_image.save(buf, format="PNG")
        buf.seek(0)

        st.download_button("Download QR Code", buf, file_name="qr_code.png", mime="image/png")
    else:
        st.error("Please enter valid data for the QR code.")

# Advanced options
st.sidebar.header("Advanced Options")
error_correction = st.sidebar.radio("Error Correction Level:", ("Low", "Medium", "High", "Very High"))

error_correction_map = {
    "Low": qrcode.constants.ERROR_CORRECT_L,
    "Medium": qrcode.constants.ERROR_CORRECT_M,
    "High": qrcode.constants.ERROR_CORRECT_Q,
    "Very High": qrcode.constants.ERROR_CORRECT_H
}

# Change error correction based on selection
if st.button("Generate with Custom Error Correction"):
    if data:
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction_map[error_correction],
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        
        # Show the QR code with custom error correction
        st.image(img, caption="Generated QR Code with Custom Error Correction", use_column_width=True)
    else:
        st.error("Please enter valid data for the QR code.")

