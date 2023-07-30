import string

import gspread

from .config import (SPREADSHEET_ID,
                     CREDENTIALS,
                     COMPARISON_SPREADSHEET_ID)
from database import TOURNAMENT_TYPES



class Connect:
    """Base class for the sheet with the users data"""


    def __init__(self, spreadsheet_id: str, *args, **kwargs) -> None:
        self.gc = gspread.service_account_from_dict(CREDENTIALS,
                                                    client_factory=gspread.BackoffClient)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_id)



class Users(Connect):
    """Class for the work with the data in the admin worksheet with the all users"""

    CELLS_COLS = {
        "username": "A",
        "chat_id": "B",
        "nickname": "C",
        "score": "D"
    }
    SHEET_NAME = "Пользователи"


    def __init__(self, *args, **kwargs):
        super().__init__(SPREADSHEET_ID)
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)


    def add_user(self, chat_id: str,
                 username: str,
                 nickname: str = '',
                 score: int = 0) -> None:
        # add user in table
        users = self.worksheet.col_values(2)
        if chat_id not in users:
            row = len(users) + 1
            self.worksheet.update(
                f'{self.CELLS_COLS["username"]}{row}',
                [[username, chat_id, nickname, score]]
            )
        

    def update_nickname(self, new_nick: str,
                        chat_id: str = None) -> None:
        # update nickname in the table
        cell = self.worksheet.find(chat_id, in_column=2)
        self.worksheet.update_cell(row=cell.row, col=3, value=new_nick)
    


class Rating(Connect):
    """
    Class for the work with the participants of the current tournament
    in the worksheet with the raiting of participants
    """
    CELLS_COLS = {
        "nickname": "A",
        "score": "B",
        "tourn_type": "C"
    }
    LENGTH = len(CELLS_COLS)
    BETWEEN = 1
    OFFSET = LENGTH + BETWEEN
    SHEET_NAME = "Текущий рейтинг"


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SPREADSHEET_ID)
        self.cells = string.ascii_uppercase
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)


    def _get_column(self, column: str,
                    tourn_type: str) -> str:
        assert tourn_type in TOURNAMENT_TYPES, 'Unknown tournament type'

        if tourn_type == 'FAST':
            return self.CELLS_COLS[column]
        elif tourn_type == 'STANDART':
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET]
        else:
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET * 2]


    def register_participant(self, nickname: str,
                             tournaments: list[str]) -> None | bool:
        # registration the participant to the next tournament

        update_data = []
        for type_ in TOURNAMENT_TYPES:
            col = self._get_column('nickname', type_)

            tourn_type_cell = self.worksheet.find(type_, in_row=1)
            participants = self.worksheet.col_values(tourn_type_cell.col)
            row = len(participants) + 1

            for tourn in tournaments:
                if type_ in tourn:
                    update_data.append(
                        {'range': f'{col}{row}', 'values': [[nickname, 0, tourn]]}
                    )
                    row += 1

        self.worksheet.batch_update(update_data)


    def update_nickname(self, new_nick: str, old_nick: str) -> None:
        # update nickname in the table
        cells = self.worksheet.findall(old_nick)
        for cell in cells:
            self.worksheet.update_cell(row=cell.row, col=cell.col, value=new_nick)



class Comparison(Connect):
    """Class for the work with the comparison list of users"""

    CHAT_ID_COLUMN = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(COMPARISON_SPREADSHEET_ID)
        self.wss = self.spreadsheet.worksheets()

    
    def get_user_tournaments(self, chat_id: str) -> list[str]:
        data = []
        for ws in self.wss:
            if chat_id in ws.col_values(self.CHAT_ID_COLUMN):
                data.append(ws.title.upper())
                
        return data