# Contact Cleanup and vCard Generator

## Overview
**Repository Name**: `contact-sanitizer`

This project is designed to address common issues faced by users dealing with improperly formatted contacts, particularly for Sri Lankan numbers. It solves problems like missing country codes for WhatsApp functionality, moving contacts between Google accounts while preserving photos, and ensuring compatibility with services like iCloud and Google Contacts.

By cleaning, formatting, and enhancing contact data, this tool makes it easier to manage contacts and avoid errors during upload or syncing.

## Features

- **Phone Number Cleaning**: Fixes Sri Lankan phone numbers missing the country code (`+94`) and formats them properly.
- **Photo Embedding**: Downloads photos linked in the `Photo` field using HTTP `GET` requests, encodes them in Base64, and embeds them into the vCard file for compatibility with platforms like iCloud.
- **Dynamic Label Assignment**: Automatically assigns labels (e.g., Mobile, Home, Work) to phone numbers.
- **Batch Processing**: Saves contacts in batches of 100 to ensure smooth uploading to Google Contacts, avoiding errors with larger files.
- **Google Contacts Compatibility**: Adheres to Google Contacts limitations, including a maximum of six phone numbers per contact.
- **Multi-Platform Support**: Generates vCard files that can be imported to various platforms, including iCloud and Google Contacts.

## Ideal Use Cases

1. **Fixing Sri Lankan Contact Numbers**:

   - Many users save Sri Lankan contacts in improper formats (e.g., missing the country code).
   - When switching WhatsApp to a foreign number, these contacts may not appear.

2. **Migrating Google Contacts**:

   - Users downloading contacts from one Google account and uploading them to another often lose contact photos due to photos being saved as links.
   - This tool downloads those photos and embeds them in vCard files, ensuring compatibility across platforms.

3. **Ensuring Compatibility**:

   - Supports Google Contacts' six-phone-number-per-contact limitation.
   - Handles contacts in batches of 100 for smooth uploading, preventing errors during bulk uploads.

## Prerequisites

- Python 3.7 or later
- Required libraries:
  - `pandas`
  - `tqdm`
  - `requests`

To install the dependencies, run:

```bash
pip install pandas tqdm requests
```

## Usage

1. **Prepare the CSV File**:

   - Name the input file `contacts.csv` and place it in the script directory.
   - Ensure the file contains the following columns (where applicable):
     - `First Name`, `Middle Name`, `Last Name`
     - `Phone 1 - Value`, `Phone 1 - Label`, ..., `Phone 6 - Value`, `Phone 6 - Label`
     - `E-mail 1 - Value`, `E-mail 1 - Label`, ..., `E-mail 2 - Value`, `E-mail 2 - Label`
     - `Address 1 - Street`, `Address 1 - City`, `Address 1 - Country`
     - `Labels`, `Photo`

2. **Run the Script**:
   Execute the script:

   ```bash
   python contact_cleanup.py
   ```

3. **Outputs**:

   - A cleaned and formatted CSV file named `updated_contacts.csv`.
   - vCard files generated in batches of 100 (e.g., `contacts_batch_1.vcf`, `contacts_batch_2.vcf`, etc.).
   - A ZIP file named `vcard_batches.zip` containing all vCard files for easy upload.

## How It Works

1. **Data Cleaning**:

   - Removes spaces, parentheses, and other unnecessary characters from phone numbers.
   - Converts numbers to the standard format `+94 XX XXX XXXX`.

2. **Dynamic Label Assignment**:

   - Automatically assigns predefined labels (`Mobile`, `Home`, `Work`, `Fax`, `Other`, `Main`) to phone numbers based on their order.

3. **Photo Embedding**:

   - Downloads photos from URLs in the `Photo` field and encodes them as Base64 for embedding in vCard files.

4. **Batch Processing**:

   - Splits contacts into batches of 100 to prevent upload errors when importing to Google Contacts.

## Example

Input CSV (sample):

| First Name | Last Name | Phone 1 - Value | Phone 2 - Value | Phone 3 - Value | Phone 4 - Value | Phone 5 - Value | Phone 6 - Value | E-mail 1 - Value        | E-mail 2 - Value      | Photo                          |
| ---------- | --------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | ----------------------- | -------------------- | ----------------------------- |
| John       | Doe       | 0771234567      | 0772345678      | 0773456789      | 0774567890      | 0775678901      | 0776789012      | john.doe@workplace.com  | john.doe@example.com | https://example.com/john.jpg |
| Jane       | Smith     | 0719876543      | 0723456789      |                 |                 |                 |                 | jane.smith@workplace.com |                      | https://example.com/jane.jpg |

Output vCard (sample):

```
BEGIN:VCARD
VERSION:3.0
N:Doe;John;;;
FN:John Doe
TEL;TYPE=Mobile:+94 77 123 4567
TEL;TYPE=Home:+94 77 234 5678
TEL;TYPE=Work:+94 77 345 6789
TEL;TYPE=Fax:+94 77 456 7890
TEL;TYPE=Other:+94 77 567 8901
TEL;TYPE=Main:+94 77 678 9012
EMAIL;TYPE=Work:john.doe@workplace.com
EMAIL;TYPE=Home:john.doe@example.com
PHOTO;ENCODING=b;TYPE=JPEG:/9j/4AAQSkZJRgABAQEAAAAAAAD/2wCEAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVDUpKy0fAkM2JyggkKHBRYoKD/8QAHQEAAgICAwEAAAAAAAAAAAAAAAQCAwUGBwgICQoL/8QANhEAAQMCAwYBAQYDBAMBAQABAgADEQQSIQUTMUEGIkFhByJxgaEiFCNCUoLh8CQzYnKCkqOywdEUYkX/2gAMAwEAAhEDEQA/APkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/9k=
END:VCARD
```

```
BEGIN:VCARD
VERSION:3.0
N:Smith;Jane;;;
FN:Jane Smith
TEL;TYPE=Mobile:+94 71 987 6543
TEL;TYPE=Mobile:+94 72 345 6789
END:VCARD
```

## Limitations

- **Maximum of 6 Phone Numbers**:

  - Google Contacts supports only six phone numbers per contact, so this tool adheres to that limit.

- **Batch Size**:

  - Contacts are processed in batches of 100 to ensure smooth uploading.

## Contributions

Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request.

## Author

Developed by Mansoor M. Sathir.
https://github.com/sathir