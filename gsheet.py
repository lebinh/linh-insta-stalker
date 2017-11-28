import gspread
from gspread.utils import rowcol_to_a1
from oauth2client.service_account import ServiceAccountCredentials


def connect(json_keyfile):
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    return gspread.authorize(credentials)


def index_ignore_case(values_list, search_value):
    search_value = search_value.strip().lower()
    for idx, value in enumerate(values_list):
        if value.strip().lower() == search_value:
            return idx
    raise ValueError("'{}' is not in list".format(search_value))


class TrackingSheet(object):
    def __init__(self, client, doc_name, sheet_name='Sheet1',
                 header_row=1, record_start_row=None,
                 username_col='username', follower_col='followers',
                 likes_col='likes', comments_col='comments',
                 updated_col='last updated'):
        self.client = client
        self.dirty_cells = []
        self.doc_name = doc_name
        self.sheet_name = sheet_name
        self.sheet = client.open(doc_name).worksheet(sheet_name)
        self.header_row = self.sheet.row_values(header_row)
        self.record_start_row = record_start_row if record_start_row is not None else header_row + 1
        try:
            # +1 as gspread lib use a 1-based index
            self.column_map = {
                'username': index_ignore_case(self.header_row, username_col) + 1,
                'followers': index_ignore_case(self.header_row, follower_col) + 1,
                'likes': index_ignore_case(self.header_row, likes_col) + 1,
                'comments': index_ignore_case(self.header_row, comments_col) + 1,
                'updated': index_ignore_case(self.header_row, updated_col) + 1,
            }
        except ValueError as e:
            raise ValueError('cannot find column: {} of headers'.format(e))

    def __repr__(self):
        return "<TrackingSheet name='{}' sheet='{}'>".format(self.doc_name, self.sheet_name)

    def records(self):
        col_count = self.sheet.col_count
        for row_id in range(self.record_start_row, self.sheet.row_count):
            row_start_cell = rowcol_to_a1(row_id, 1)
            row_end_cell = rowcol_to_a1(row_id, col_count)
            row_cells = self.sheet.range('{}:{}'.format(row_start_cell, row_end_cell))

            # stop upon first empty row
            if not any(cell.value for cell in row_cells):
                break

            yield TrackingRecord(self, row_id, row_cells)

    def update_cells(self, cells):
        self.sheet.update_cells(cells)


class TrackingRecord(object):
    def __init__(self, sheet, row, row_cells):
        self.sheet = sheet
        self.row = row
        self.cells = {}
        for key in sheet.column_map:
            # -1 here as the column map value is 1-based index and we need 0-based index here
            self.cells[key] = row_cells[sheet.column_map[key] - 1]

    def __repr__(self):
        return "<TrackingRecord fields={}>".format(self.fields)

    def __getattr__(self, item):
        return self.fields[item]

    @property
    def fields(self):
        return dict((k, self.cells[k].value) for k in self.cells)

    def update(self, **kwargs):
        for key in kwargs:
            if key not in self.fields:
                raise ValueError('cannot update unknown field: {}'.format(key))
        updated_cells = []
        for key, value in kwargs.items():
            self.cells[key].value = value
            updated_cells.append(self.cells[key])
        self.sheet.update_cells(updated_cells)

