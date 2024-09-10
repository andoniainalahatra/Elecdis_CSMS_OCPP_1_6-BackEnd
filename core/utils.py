from fastapi import UploadFile
import io
import csv

DELETED_STATE = 1
DEFAULT_STATE = 0
DEFAULT_USER_PASSWORD = "password"

async def get_datas_from_csv(file: UploadFile):
    json_data = []
    content = await file.read()
    csv_file = io.StringIO(content.decode('utf-8'))

    # Read the first row to check if it's a header
    first_row = next(csv.reader(csv_file))
    csv_file.seek(0)  # Reset the file pointer to the beginning

    # Determine if the first row is a header
    is_header = all(any(c.isalpha() for c in cell) for cell in first_row)

    if is_header:
        reader = csv.DictReader(csv_file)
    else:
        # If there's no header, manually assign headers
        headers = ["col1", "col2", "col3", "col4"]  # Customize as needed
        reader = csv.DictReader(csv_file, fieldnames=headers)

    for row in reader:
        json_data.append(row)
    return json_data