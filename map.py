import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Function to format employee IDs
def format_emp_id(emp_id):
    if pd.isna(emp_id) or emp_id == '-':
        return np.nan
    try:
        emp_id = int(emp_id)  # Convert to integer to remove decimal places
        return str(emp_id).zfill(4)  # Add leading zeros if necessary
    except ValueError:
        return np.nan  # Return NaN for any non-numeric values

# Function to process the data
def process_file(uploaded_file):
    # Read the uploaded file
    df = pd.read_excel(uploaded_file)

    # Columns to keep
    columns_to_keep = ['Branch', 'Branch ID', 'State', 'AM', 'AM Emp ID', 'DM',
                       'DM Emp ID', 'RM', 'RM Emp ID', 'SH', 'SH Emp ID', 'ZM', 'ZM Emp ID',
                       'Senior ZH', 'Senior ZH Emp ID', 'SCH Name', 'SCH EMP ID']
    df = df[columns_to_keep]

    # Define common columns and role sets
    common_columns = ['Branch', 'Branch ID', 'State']
    role_columns = {
        'AM': ['AM', 'AM Emp ID'],
        'DM': ['DM', 'DM Emp ID'],
        'RM': ['RM', 'RM Emp ID'],
        'SH': ['SH', 'SH Emp ID'],
        'ZM': ['ZM', 'ZM Emp ID'],
        'ZH': ['Senior ZH', 'Senior ZH Emp ID'],
        'CM': ['SCH Name', 'SCH EMP ID']
    }

    # Create a list to hold the new DataFrame segments
    segments = []

    # Iterate over each role and its corresponding columns
    for role, cols in role_columns.items():
        segment = df[common_columns + cols].copy()
        segment.columns = common_columns + ['Name', 'Emp ID']
        segment['Role'] = role
        segment['Emp ID'] = segment['Emp ID'].apply(format_emp_id)
        segments.append(segment)

    # Concatenate all the segments vertically
    new_df = pd.concat(segments, ignore_index=True)

    # Remove rows where 'Emp ID' is NaN or not numeric
    new_df = new_df[pd.notna(new_df['Emp ID']) & new_df['Emp ID'].str.isnumeric()]

    # Add new columns
    new_df['Role_Emp_ID'] = 'SM' + new_df['Emp ID']
    new_df['Branch ID'] = new_df['Branch ID'].astype(str)
    new_df['Role_Emp_ID'] = new_df["Role_Emp_ID"].astype(str)
    new_df['Unique code'] = new_df['Role_Emp_ID'] + new_df['Branch ID']
    new_df['Role'] = new_df['Role'].replace('ZH', 'ZM')

    return new_df

# Streamlit App
def main():
    st.title("Branch Role Mapping Tool")

    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

    if uploaded_file:
        st.success("File uploaded successfully!")
        
        # Generate Output Button
        if st.button("Generate Output"):
            processed_data = process_file(uploaded_file)

            # Display processed data
            st.subheader("Processed Data")
            st.dataframe(processed_data)

            # Prepare Excel for download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                processed_data.to_excel(writer, index=False, sheet_name='Mapping')
            output.seek(0)

            # Download Output Button
            st.download_button(
                label="Download Output",
                data=output,
                file_name="Mapping.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()

