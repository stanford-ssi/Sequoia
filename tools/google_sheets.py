import pickle
import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleSheet:
    """
    Credit/Reference: https://developers.google.com/sheets/api/quickstart/python 
    """

    # don't accidentally edit
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self, spreadsheet_id, spreadsheet_range):
        self.id = spreadsheet_id
        self.range = spreadsheet_range

    def json_from_rows(self, key_column, filename):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if os.path.exists('google_token.pickle'):
            with open('google_token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('google_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.id,
                                    range=self.range).execute()

        rows = result.get('values', [])

        self.row_dictionaries = {}
        
        if not rows:
            raise ValueError('No data found.')

        else:
            titles = rows[0]
            for row in rows[1:]:

                # don't put mid-level headers empty rows in the dictionary
                if len(row) < 2:
                    continue

                else:
                    row_dictionary = {}
                    for i, elem in enumerate(row):
                        row_dictionary[titles[i]] = elem
                    
                    self.row_dictionaries[row[key_column]] = row_dictionary

        with open(filename, 'w') as f:
            json.dump(self.row_dictionaries, f, indent=4)

sequoia =  "1LgfZWeo7Q2KEg5C1LhN5yxGT8s4gFGmod-ak6bNA-iM"
test_sheet = "1GD2QhM9BpuDSCVsicsmwg_Z9OEOug9FfT5S2eYPCZZQ"

sheet = GoogleSheet(sequoia, "Requirements_Working!B2:G")
sheet.json_from_rows(0, "google_issues.json")