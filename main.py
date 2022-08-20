import os
import pickle
import sqlite3

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

# Allows read/write access to the user's sheets and their properties.
SPREADSHEET_ID = '*******************'  # TODO: change this to the copy of the spreadsheet template
SHEET_TEMPLATE_ID = 1822551224  # the sheet ids stay the same when copied


def get_sheets_service(file_name):
    """
    Returns the service for Google Sheets, given a credential file.
    The service allows for interactions with Google Sheets.

    Code from: https://developers.google.com/sheets/api/quickstart/python

    :param file_name: file name of the credentials JSON
    :return: a Google Sheets service
    """
    if not os.path.exists(file_name):
        raise NotImplementedError(f"Couldn't find credentials at {file_name}."
                                  f"See https://developers.google.com/workspace/guides/create-credentials"
                                  f"for creating a credential file.")
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            sheets = 'https://www.googleapis.com/auth/spreadsheets'
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=file_name, scopes=[sheets])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = discovery.build('sheets', 'v4', credentials=creds)
    return service


def get_duplicate_sheet_request(sheet_id, name, insert_index):
    """
    Returns the request to duplicate the template (see SHEET_TEMPLATE_ID)

    :param sheet_id: id of the new sheet
    :param name: name of the new sheet
    :param insert_index: index where the sheet should be inserted
    :return: a DuplicateSheetRequest
    """
    return {
        'duplicateSheet': {
            'sourceSheetId': SHEET_TEMPLATE_ID,
            'insertSheetIndex': insert_index,
            'newSheetName': name,
            'newSheetId': sheet_id
        }
    }


def get_module_catalogue_query(program_id):
    """
    Returns an SQL query to get the module catalogue for a study program

    :param program_id: id of the study program
    :return: SQL query as a string
    """
    base_url = "https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/beschreibung/anzeigen.html"

    # sql concatenation strings
    module_id = "' || m.id || '"
    module_version = "' || m.version || '"
    label = "' || m.title || '"

    url = f"{base_url}?number={module_id}&version={module_version}"
    module_link = f"'=HYPERLINK(\"{url}\"; \"{label}\")'"

    return f"SELECT " \
           f"sa.title, " \
           f"sap.title, " \
           f"{module_link}, " \
           f"m.id, " \
           f"m.version, " \
           f"m.ects, " \
           f"m.exam_type, " \
           f"group_concat(DISTINCT mp.type) " \
           f"FROM programs p " \
           f"JOIN study_areas sa ON sa.program_id = p.id " \
           f"JOIN modules_study_areas msa ON msa.study_area_id = sa.id " \
           f"JOIN modules m ON m.id = msa.module_id AND m.version = msa.module_version " \
           f"LEFT JOIN module_parts mp ON mp.module_id = m.id AND mp.module_version = m.version " \
           f"JOIN study_areas sap ON sap.id = sa.parent_id " \
           f"WHERE p.id = {program_id} " \
           f"GROUP BY m.id, m.version, sa.id " \
           f"ORDER BY sa.id"


def get_module_catalogue_link(program_id, sheet_name):
    """
    Returns a Google Sheets hyperlink for the module catalogue of a study program.

    :param program_id: study program
    :param sheet_name: sheet name of the study program
    :return: Google Sheets `=HYPERLINK(<url>, <label>)`-string to the program's module catalogue
    """
    base_url = "https://moseskonto.tu-berlin.de/moses/modultransfersystem/studiengaenge/anzeigenKombiniert.html"
    url = f"{base_url}?id='{str(program_id)}"
    label = f"Moses: Modulliste {sheet_name}"
    return f"=HYPERLINK(\"{url}\"; \"{label}\")"


def get_module_catalogue(modules):
    """
    Returns module catalogue in the spreadsheet's format.

    :param modules: list of module tuples for a study program
    :return: module catalogue in the spreadsheet's format (compare "Rechte Tabelle" in spreadsheet)
    """
    color = 0
    cur_sa = ''
    cur_sap = ''
    module_catalogue = []

    for module in modules:
        if cur_sa != module[0] or cur_sap != module[1]:
            color += 1
            cur_sa = module[0]
            cur_sap = module[1]

            # add divider for study area
            title = f"{str(color)}: {cur_sa}\n[aus {cur_sap}]"
            module_catalogue.append([title])  # + [] * 7)
        module_catalogue.append(['', color] + list(module[2:]))
    return module_catalogue


def add_study_program(service, program, insert_index, module_catalogue):
    """
    Adds a new sheet for a study program and fills it with its module catalogue.

    :param service: Google Sheets service used for interaction
    :param program: 3-tuple of program: (id, name, degree)
    :param insert_index: index where the sheet should be inserted
    :param module_catalogue: module catalogue data for the study program
    """
    program_id, program_name, degree = program
    sheet_name = f"{program_name}{degree[-8:]}"

    # create new sheet for program
    new_sheet_rq = {
        'requests': [get_duplicate_sheet_request(sheet_id=program_id, name=sheet_name, insert_index=insert_index)]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=new_sheet_rq
    ).execute()

    # fill in table name
    insert_table_name_rq = {
        "values": [[get_module_catalogue_link(program_id=program_id, sheet_name=sheet_name)]],
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_name + '!K2',
        valueInputOption="USER_ENTERED",
        body=insert_table_name_rq
    ).execute()

    # fill in module catalogue
    insert_module_catalogue_rq = {
        "values": module_catalogue
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_name + '!I4',
        valueInputOption="USER_ENTERED",
        body=insert_module_catalogue_rq
    ).execute()


def add_all_study_programs(sheets_service, spreadsheet, cursor):
    """
    Generates a sheet for every study program.

    :param sheets_service: Google Sheets service used for interaction
    :param spreadsheet: spreadsheet that is modified
    :param cursor: cursor for sqlite database
    """
    # get all study programs
    cursor.execute("SELECT * FROM programs ORDER BY title DESC, degree DESC")
    programs = cursor.fetchall()

    # create a sheet for every study program
    for program in programs:
        program_id = program[0]
        insert_index = len(spreadsheet['sheets'])

        # get module catalogue for study program
        cursor.execute(get_module_catalogue_query(program_id))
        module_catalogue = get_module_catalogue(cursor.fetchall())

        # add study program
        add_study_program(sheets_service, program, insert_index, module_catalogue)


def main():
    # connect to spreadsheet
    sheets_service = get_sheets_service('credentials.json')
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()

    # connect to database
    sql_conn = sqlite3.connect('mts.sqlite')
    sql_cursor = sql_conn.cursor()

    # fill spreadsheet with database
    add_all_study_programs(sheets_service, spreadsheet, sql_cursor)


if __name__ == '__main__':
    main()
