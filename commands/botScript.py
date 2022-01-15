import pytz
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

class Spreadsheet():
    def __init__(self):
        """
        Establish credentials from `credentials/funguyfamily.json` and create sp.
        """
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/funguyfamily.json', scope)

        gc = gspread.authorize(credentials)    
        self.sp = gc.open('FunGuy_test')     

    # Spreadsheet Functions
    def create_worksheet(self, name: str):
        """
        Create a spreadsheet with only 1 column (userID).
        """
        assert (type(name) == str), "Worksheet name is not a string."
        # TODO: add err check if worksheet name already exist
        workSheet = self.sp.add_worksheet(title=name, rows="1", cols="1")
        workSheet.append_row(["userID"])

    def get_current_worksheet(self):
        """
        Check if you need to create a worksheet. Creates a new one for a new month.
        """
        utc = pytz.timezone('UTC')
        currentAirDropDate = datetime.now(utc)
        nameAirDropDate = str(currentAirDropDate.year) + '-' + str(currentAirDropDate.month)

        # Check if we are in new month and need to create a new entry
        try:
            self.sp.worksheet(nameAirDropDate)  
        except Exception:
            self.create_worksheet(nameAirDropDate)

        return nameAirDropDate

    # Airdrop Functions
    def join_airdrop(self, discordID: str, walletAddress: str) -> bool:
        """
        Add user to airdrop.
        """
        response = self.check_user(discordID, walletAddress)
        if not response['status']:
            return {
                'status': response['status'],
                'errMsg': response['errMsg']
            }
        
        nameAirDropDate = self.get_current_worksheet()
        workSheet = self.sp.worksheet(nameAirDropDate)
        userIDRow = workSheet.find(response.userID)
        if userIDRow is None:
            workSheet.append_row([response.userID])
            
        return {
            'status': response['status'],
            'errMsg': response['errMsg']
        }
 
    # User Function
    def insert_user(self, userID: int, discordID: str, walletAddress: str, numberOfFunGuys: int, dateOfOldestFunGuy: datetime)-> str:
        """
        Guarantees that there is only one Discord user and only one wallet with that address.
        """
        workSheet = self.sp.worksheet("UserTbl")
        response = self.check_user(userID, walletAddress)

        if response['status']:
            return {
                'status': False,
                'errMsg': 'User already exists.',
                'numFunguys': response['numFunguys'],
                'oldestDate': response['oldestDate']
            }

        # If the wallet and DiscordId has never being used, add a new user
        workSheet.append_row([str(userID), discordID, walletAddress, numberOfFunGuys, dateOfOldestFunGuy])

        return {
            'status': True,
            'errMsg': None,
            'numFunguys': numberOfFunGuys,
            'oldestDate': dateOfOldestFunGuy,
        }

    def update_user(self, userID: int, walletAddress: str, numberOfFunGuys: int) -> str:
        """
        Update Funguy status of the Discord user.
        """
        workSheet = self.sp.worksheet("UserTbl")
        response = self.check_user(userID, walletAddress)

        if not response['status']:
            return {
                'status': False,
                'errMsg': response['errMsg'],
                'numFunguys': -1,
                'oldestDate': -1
            }

        workSheet.update_cell(response['userIDRow'].row, 4, numberOfFunGuys)

        return {
            'status': True,
            'errMsg': None,
            'numFunguys': workSheet.cell(response['userIDRow'].row, 4).value,
            'oldestDate': response['oldestDate']
        }

    def check_user(self, userID: str, walletAddress: str):
        """
        Returns the user's number of Funguys and the oldestDate of their Funguy.
        """
        workSheet = self.sp.worksheet("UserTbl")
        userIDRow = workSheet.find(str(userID))
        walletAddressRow = workSheet.find(walletAddress)

        if not userIDRow:
            return {
                'status': False,
                'errMsg': 'User not found.',
                'discordIDRow': -1,
                'numFunguys': -1,
                'oldestDate': -1
            }

        if not walletAddressRow:
            return {
                'status': False,
                'errMsg': 'Wallet address not found.',
                'discordIDRow': -1,
                'numFunguys': -1,
                'oldestDate': -1
            }

        return {
            'status': True,
            'errMsg': None,
            'userIDRow': userIDRow,
            'numFunguys': workSheet.cell(userIDRow.row, 4).value,
            'oldestDate': workSheet.cell(userIDRow.row, 5).value
        }

if __name__ == '__main__':
    sp = Spreadsheet()
