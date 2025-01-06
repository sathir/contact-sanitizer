import pandas as pd
import re
import base64
import requests
from io import BytesIO
from tqdm import tqdm
import zipfile
import os
tqdm.pandas()

# Load the CSV file
file_path = 'contacts.csv'  # Input CSV file
contacts_df = pd.read_csv(file_path, dtype=str)

# Define phone labels
phone_labels = ["Mobile", "Home", "Work", "Fax", "Other", "Main"]

# Clean and preprocess phone numbers
def clean_phone_numbers(df, max_phones=6):
    """
    Cleans phone numbers by removing spaces, parentheses, and adjusting formats.
    """
    for i in range(1, max_phones + 1):
        value_column = f"Phone {i} - Value"
        if value_column in df.columns:
            df[value_column] = (
                df[value_column]
                .astype(str)
                .apply(lambda x: x.strip() if x.lower() != "nan" else "")
                .str.replace(r"\s+", "", regex=True)
                .str.replace(r"[()]+", "", regex=True)
                .str.replace(r"^\+94", "0", regex=True)
                .str.replace(r"^94", "0", regex=True)
            )
            df[value_column] = df[value_column].apply(
                lambda x: '0' + x if isinstance(x, str) and len(x) == 9 else x
            )
    return df

# Capitalize string values
def capitalize_strings(value):
    """
    Capitalizes the first letter of strings. If the value is not a string or NaN, it is returned as an empty string.
    """
    if isinstance(value, str) and value.strip():
        return value[0].upper() + value[1:] if value[0].islower() else value
    return ""

# Distribute phone numbers split by ':::' across available columns
def distribute_phone_values(row, max_phones=6):
    """
    Distributes phone numbers separated by ':::' into available phone columns.
    Updates corresponding label columns with 'Mobile' if empty.
    """
    for i in range(1, max_phones + 1):
        value_column = f"Phone {i} - Value"
        label_column = f"Phone {i} - Label"

        if value_column in row and isinstance(row[value_column], str) and ':::' in row[value_column]:
            values = row[value_column].split(":::")
            row[value_column] = values.pop(0)
            for value in values:
                for j in range(i + 1, max_phones + 1):
                    next_value_column = f"Phone {j} - Value"
                    next_label_column = f"Phone {j} - Label"
                    if next_value_column in row and (pd.isna(row[next_value_column]) or row[next_value_column] == ""):
                        row[next_value_column] = value.strip()
                        row[next_label_column] = "Mobile"
                        break
    return row

# Clear empty or invalid phone values and corresponding labels
def clear_empty_phone_labels(row, max_phones=6):
    """
    Clears labels for phone fields where the value is NaN or empty.
    """
    for i in range(1, max_phones + 1):
        value_column = f"Phone {i} - Value"
        label_column = f"Phone {i} - Label"
        if pd.isna(row[value_column]) or row[value_column] == "":
            row[label_column] = ""
    return row

# Dynamically update phone labels based on predefined labels
def update_phone_labels(df, max_phones=6):
    """
    Assigns phone labels dynamically based on predefined labels if not already present.
    """
    for i in range(1, max_phones + 1):
        value_column = f"Phone {i} - Value"
        label_column = f"Phone {i} - Label"
        if value_column in df.columns and label_column in df.columns:
            df[label_column] = df.apply(
                lambda row: phone_labels[i - 1] if pd.notna(row[value_column]) and row[value_column] != "" else row[label_column],
                axis=1
            )
    return df

# Encode a photo from a URL into Base64
def encode_photo_from_url(photo_url):
    """
    Downloads the photo from the given URL and encodes it as Base64.
    """
    try:
        response = requests.get(photo_url, timeout=5)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        return base64.b64encode(image_data.read()).decode('utf-8')
    except Exception as e:
        print(f"Error downloading or encoding photo from URL: {photo_url} - {e}")
        return None

# Extract and format categories
def extract_categories(categories_field):
    """
    Extracts and formats all categories from the provided field value.
    """
    if not categories_field or categories_field.lower() == 'nan':
        return "myContacts"
    categories = [cat.strip() for cat in categories_field.split(" ::: ") if cat.strip()]
    return ",".join(categories) if categories else "myContacts"

# Generate vCard for a single contact
def create_vcard(row):
    """
    Creates a vCard string for a single contact.
    """
    vcard = ["BEGIN:VCARD", "VERSION:3.0"]

    first_name = str(row.get('First Name', ""))
    middle_name = str(row.get('Middle Name', ""))
    last_name = str(row.get('Last Name', ""))
    if first_name or last_name:
        vcard.append(f"N:{last_name};{first_name};{middle_name};;")
        vcard.append(f"FN:{' '.join(filter(None, [first_name, middle_name, last_name]))}")
    else:
        return None

    if nickname := row.get('Nickname'):
        vcard.append(f"NICKNAME:{nickname}")

    if org_name := row.get('Organization Name'):
        vcard.append(f"ORG:{org_name}")

    if birthday := row.get('Birthday'):
        vcard.append(f"BDAY:{birthday}")

    if notes := row.get('Notes'):
        vcard.append(f"NOTE:{notes}")

    for i in range(1, 7):
        phone_value = row.get(f'Phone {i} - Value', "")
        phone_label = row.get(f'Phone {i} - Label', "")
        if phone_value:
            vcard.append(f"TEL;TYPE={phone_label or 'Mobile'}:{phone_value}")

    for i in range(1, 3):
        email_value = row.get(f'E-mail {i} - Value', "")
        email_label = row.get(f'E-mail {i} - Label', "")
        if email_value:
            vcard.append(f"EMAIL;TYPE={email_label or 'Other'}:{email_value.lower()}")

    address = "".join(
        [row.get('Address 1 - Street', ""), row.get('Address 1 - City', ""), row.get('Address 1 - Country', "")]
    )
    if address:
        vcard.append(f"ADR:;;{address};;")

    categories = extract_categories(row.get('Labels', ""))
    vcard.append(f"CATEGORIES:{categories}")

    if photo_url := row.get('Photo'):
        if encoded_photo := encode_photo_from_url(photo_url):
            vcard.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{encoded_photo}")

    vcard.append("END:VCARD")
    return "\n".join(vcard)

# Apply cleaning and formatting functions
print("Cleaning phone numbers...")
contacts_df = clean_phone_numbers(contacts_df)
print("Capitalizing strings...")
contacts_df = contacts_df.apply(lambda col: col.map(capitalize_strings))
print("Distributing phone numbers...")
contacts_df = contacts_df.progress_apply(lambda row: distribute_phone_values(row), axis=1)
print("Clearing empty phone labels...")
contacts_df = contacts_df.progress_apply(lambda row: clear_empty_phone_labels(row), axis=1)
print("Updating phone labels dynamically...")
contacts_df = update_phone_labels(contacts_df)

# Save updated CSV
updated_file_path = 'updated_contacts.csv'
contacts_df.to_csv(updated_file_path, index=False)
print(f"Cleaned and formatted data saved to {updated_file_path}")

# Generate vCards in batches
batch_size = 100
total_batches = (len(contacts_df) + batch_size - 1) // batch_size  # Calculate total number of batches
print("Generating vCards...")

vcard_files = []
for batch_number, start in tqdm(enumerate(range(0, len(contacts_df), batch_size), start=1), total=total_batches, desc="Processing batches"):
    batch_file = f'contacts_batch_{batch_number}.vcf'
    with open(batch_file, 'w', encoding='utf-8') as vcf:
        for _, row in contacts_df.iloc[start:start + batch_size].iterrows():
            if vcard := create_vcard(row):
                vcf.write(vcard + "\n")
    print(f"Batch file created: {batch_file}")
    vcard_files.append(batch_file)

# Create a ZIP file of all vCard files
zip_file_name = 'vcard_batches.zip'
with zipfile.ZipFile(zip_file_name, 'w') as zipf:
    for file in vcard_files:
        zipf.write(file)
        os.remove(file)  # Remove individual files after adding to zip

print(f"All vCard batch files have been zipped into {zip_file_name}.")
