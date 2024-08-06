import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import pytesseract
import re

# Function to create a unique folder for each user
def create_user_folder(base_folder, first_name, last_name, date_of_birth):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_folder = f"{first_name}_{last_name}_{date_of_birth}_{timestamp}"
        full_path = os.path.join(base_folder, user_folder)
        Path(full_path).mkdir(parents=True, exist_ok=True)
        return full_path
    except Exception as e:
        st.error(f"Error creating user folder: {e}")
        return None

# Function to save uploaded files
def save_uploaded_file(uploaded_file, folder_path):
    try:
        if uploaded_file is not None:
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None

# Function to extract data using Tesseract and regex
def extract_data_from_files(folder_path):
    try:
        data_dict = {}
        files = os.listdir(folder_path)
        for file_name in files:
            path = r"C:\Users\Omsai\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
            pytesseract.pytesseract.tesseract_cmd = path
            file_path = os.path.join(folder_path, file_name)
            text = pytesseract.image_to_string(file_path)

            if "TAX" in text or "Permanent Account Number" in text:
                pan_no = re.search("[A-Z]{5}\d{4}[A-Z]", text)
                if pan_no:
                    data_dict["PAN Number"] = pan_no.group()

            if re.search("Aadhaar", text):
                dob = re.search(r"(?<=DOB[:]\s)\d{1,2}[/]\d{1,2}[/]\d{2,4}|(?<=DOB\s[:]\s)\d{1,2}[/]\d{1,2}[/]\d{2,4}", text)
                adhar_no = re.search(r"\d{4}\s\d{4}\s\d{4}", text)
                gender = re.search(r"Male|Female", text, re.IGNORECASE)
                if dob:
                    data_dict["DOB"] = dob.group()
                if adhar_no:
                    data_dict["Aadhar Number"] = adhar_no.group()
                if gender:
                    data_dict["Gender"] = gender.group().capitalize()

            if re.search("Payslip|Salary slip", text, re.IGNORECASE):
                employee_name = re.search(r"[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+", text)
                employee_id = re.search(r"\d{7}", text)
                uan_no = re.search(r"\d{12}", text)
                net_pay = re.search(r"(?<=Net Payable €)[\d,.]+(?=[ (])", text)
                if employee_name:
                    data_dict["Employee Name"] = employee_name.group()
                if employee_id:
                    data_dict["Employee ID"] = employee_id.group()
                if uan_no:
                    data_dict["UAN Number"] = uan_no.group()
                if net_pay:
                    data_dict["Net Payable"] = net_pay.group()

        return data_dict
    except Exception as e:
        st.error(f"Error extracting data from files: {e}")
        return {}

# Function to save data to CSV
def save_data_to_csv(data_dict, csv_file_folder):
    try:
        csv_file = os.path.join(csv_file_folder, "Extracted_data.csv")
        new_entry = pd.DataFrame([data_dict])
        if os.path.exists(csv_file):
            existing_data = pd.read_csv(csv_file)
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        else:
            updated_data = new_entry
        updated_data.to_csv(csv_file, index=False)
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

# Function to save user data to Excel
def save_user_data_to_excel(first_name, last_name, date_of_birth, mobile_number, email_id, adhar_number, pan_card_number, excel_file_path):
    try:
        new_entry = pd.DataFrame({
            'First Name': [first_name],
            'Last Name': [last_name],
            'Date of Birth': [date_of_birth],
            'Mobile Number': [mobile_number],
            'Email ID': [email_id],
            'Adhar Number': [adhar_number],
            'PAN Card Number': [pan_card_number]
        })

        if os.path.exists(excel_file_path):
            existing_data = pd.read_excel(excel_file_path)
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        else:
            updated_data = new_entry

        updated_data.to_excel(excel_file_path, index=False)
    except Exception as e:
        st.error(f"Error saving user data to Excel: {e}")

def main():
    st.title('Share Market Account Opening Form')

    with st.form(key='account_form'):
        first_name = st.text_input('First Name')
        last_name = st.text_input('Last Name')
        date_of_birth = st.date_input('Date of Birth',min_value=datetime(1950,1,1),max_value=datetime.now())
        mobile_number = st.text_input('Mobile Number')
        email_id = st.text_input('Email ID')
        adhar_number = st.text_input('Adhar Number')
        pan_card_number = st.text_input('PAN Card Number')

        adhar_file = st.file_uploader('Upload Adhar', type=['pdf', 'jpg', 'png'])
        pan_file = st.file_uploader('Upload PAN Card', type=['pdf', 'jpg', 'png'])
        salary_slip_file = st.file_uploader('Upload Salary Slip', type=['pdf', 'jpg', 'png'])

        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        if not (first_name and last_name and date_of_birth and mobile_number and email_id and adhar_number and pan_card_number and adhar_file and pan_file and salary_slip_file):
            st.warning('Please fill all the mandatory fields and upload all required documents.')
        else:
            try:
                # Create user folder
                base_folder = "G:/Streamlit_Project/streamlit/App/User_Added_Documents"
                user_folder = create_user_folder(base_folder, first_name, last_name, date_of_birth)
                
                # Save uploaded files
                save_uploaded_file(adhar_file, user_folder)
                save_uploaded_file(pan_file, user_folder)
                save_uploaded_file(salary_slip_file, user_folder)

                # Extract data from uploaded files
                extracted_data = extract_data_from_files(user_folder)

                # Save extracted data to CSV
                csv_file_folder = "G:/Streamlit_Project/streamlit/App/CSV_File"
                save_data_to_csv(extracted_data, csv_file_folder)

                # Save user-entered data to Excel
                excel_file_path = "G:/Streamlit_Project/streamlit/App/user_data.xlsx"
                save_user_data_to_excel(first_name, last_name, date_of_birth, mobile_number, email_id, adhar_number, pan_card_number, excel_file_path)

                st.success('Your DMAT account application has been received! We appreciate your interest in opening an account with us.')

            except Exception as e:
                st.error(f"An error occurred during form submission: {e}")

if __name__ == "__main__":
    main()
