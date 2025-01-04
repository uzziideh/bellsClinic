
import streamlit as st
from fpdf import FPDF
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime

# Load student data from CSV
STUDENT_DATABASE = pd.read_csv("testdata.csv")

def generate_qr_code(data):
    """Generate a QR code from the provided data."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    
    # Save QR code as a BytesIO object
    qr_buffer = BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer

def generate_pdf(matric_number, fullname, dept, result, qr_code):
    """Generate a PDF report with the QR code."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Logo
    pdf.image("logo.jpeg", x=80, y=10, w=35)
    pdf.ln(40)  # Space after logo
    
    # Header
    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(0, 10, "Bells University of Technology, Ota", ln=True, align="C")
    pdf.cell(0, 10, "Substance Abuse Screening Report", ln=True, align="C")
    
    pdf.ln(10)  # Space after header
    
    # Content
    pdf.set_font("Arial", size=12)
    details = [
        f"Matric Number/Hospital Number: {matric_number}",
        f"Full Name: {fullname}",
        f"Department: {dept}",
        f"Substance abuse screening: {result}"
    ]
    
    for detail in details:
        pdf.cell(0, 10, detail, ln=True)
    
    pdf.ln(10)  # Space before QR code

    # Add QR code to the PDF
    qr_code_path = "temp_qr_code.png"
    with open(qr_code_path, "wb") as f:
        f.write(qr_code.getvalue())
    pdf.image(qr_code_path, x=80, y=120, w=50)  # Adjust placement and size of the QR code

    # Timestamp watermark
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Arial", "I", size=8)
    pdf.set_text_color(128, 128, 128)
    pdf.set_y(-30)
    pdf.cell(0, 10, f"Generated on: {timestamp}", align="C", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

def main():
    st.set_page_config(page_title= "BellsTech", 
                       page_icon="logo.jpeg", 
                       layout="centered", 
                       initial_sidebar_state="auto", 
                       menu_items=None)

    st.sidebar.title("INSTRUCTION")
    st.sidebar.markdown("""
        **Welcome to the BellsTech Clinic App!**

        This app allows you to verify your substance abuse screening status.

        **To use this app:**

        1. Enter your mat number or hospital number (Newly admitted students only).
        2. Click the 'Generate Report' button.
        3. Click the 'Download Report' button.

        **Note:** 
            Forging of your substance abuse screening report will result in two semesters expulsion from the university.

        For any questions or assistance, please contact the University's Clinic.
    """)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(' ')

    with col2:
        st.image("logo.jpeg")
    with col3:
        st.write(' ')
    st.markdown("""
        <h3 style='text-align: center;'>Bells University of Technology, Ota </h3>
        <h4 style='text-align: center;'>Substance Abuse Screening Report Generator</h4>
    """, unsafe_allow_html=True) 
    st.markdown('---')
  
    matric_number =st.text_input("Enter your Mat Number/Hospital Number")
    if st.button("Generate Report"):
        if not matric_number:
            st.error("Please select a matric number.")
            return
        
        # Query the database
        student_data = STUDENT_DATABASE.loc[STUDENT_DATABASE['Matric Number'] == matric_number]
        
        if student_data.empty:
            st.error("Matric number not found or medical test not completed.")
            return
        
        # Extract student details
        student = student_data.iloc[0]
        fullname = student["Fullname"]
        dept = student["Dept"]
        result = student["RESULT"]
        
        st.markdown("---")
        # Display student details
        st.success("Report generated successfully!")
        st.write("### Student Details")
        st.write(f"**Matric Number/Hospital Number:** {matric_number}")
        st.write(f"**Full Name:** {fullname}")
        st.write(f"**Department:** {dept}")
        st.write(f"**Substance abuse screening:** {result}")
        
        # Generate QR code with student information
        qr_code_data = f"Matric Number: {matric_number}\nFull Name: {fullname}\nDepartment: {dept}\nResult: {result}"
        qr_code = generate_qr_code(qr_code_data)
        
        # Generate and download the report
        pdf_data = generate_pdf(matric_number, fullname, dept, result, qr_code)
        st.markdown("---")
        st.download_button(
            label="Download Report",
            data=pdf_data,
            file_name=f"{matric_number}_report.pdf",
            mime="application/pdf"
        )
        st.markdown("---")
if __name__ == "__main__":
    main()
