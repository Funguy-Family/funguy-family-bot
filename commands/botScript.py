import pytz
import gspread
from datetime import date, datetime, timedelta
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
        workSheet.append_row(["userID", "walletAddress", "numberOfFunGuys", "dateOfOldestFunGuy", "TSHY COIN"])

    def get_current_worksheet(self):
        """
        Check if you need to create a worksheet. Creates a new one for a new month.
        """
        utc = pytz.timezone('UTC')
        currentAirDropDate = datetime.now(utc)
        nameAirDropDate = str(currentAirDropDate.year) + '-' + str(currentAirDropDate.month) + '-01' 
        newMonth = False

        # Check if we are in new month and need to create a new entry
        try:
            self.sp.worksheet(nameAirDropDate)  
            newMonth = True
        except Exception:
            self.create_worksheet(nameAirDropDate)

        return [nameAirDropDate, newMonth]

    # Airdrop Functions
    def join_airdrop(self, userID: str) -> bool:
        """
        Add user to airdrop.
        """
        response = self.check_user(userID)
        if not response['status']:
            return {
                'status': response['status'],
                'errMsg': response['errMsg'],
                'newMonth': None
            }
        
        nameAirDropDate = self.get_current_worksheet()
        nameAirDropDateName = nameAirDropDate[0]

        workSheet = self.sp.worksheet(nameAirDropDateName)
        userIDRow = workSheet.find(response.userID)
        if userIDRow is None:
            workSheet.append_row([response.userID])
            
        return {
            'status': response['status'],
            'errMsg': response['errMsg'],
            'newMonth': nameAirDropDateName[1]
        }
 
    def populate_last_month_values(self, nameAirDropDate):
        workSheetAirDrop = self.sp.worksheet(nameAirDropDate)
        workSheetUserID = self.sp.worksheet("UserTbl")
        listOfUserID = workSheetAirDrop.col_values(1)

        for i, userID in enumerate(listOfUserID, start=1):        
            if i == 1:
                continue
            userIDCell = workSheetUserID.find(userID)
            userIDCellRow = userIDCell.row

            walletAddress = workSheetUserID.cell(userIDCellRow,3).value
            numberOfFunGuys = workSheetUserID.cell(userIDCellRow,4).value
            dateOfOldestFunGuy = workSheetUserID.cell(userIDCellRow,5).value

            workSheetAirDrop.update("B"+str(i) + ":D"+str(i), [[walletAddress,numberOfFunGuys,dateOfOldestFunGuy]])

        return {
            'status': True,
            'errMsg': None,
            'nameAirDropDate': nameAirDropDate
        }

    def calculate_TSHY_coin(self, nameAirDropDate):
        workSheetAirDrop = self.sp.worksheet(nameAirDropDate)

        listOfUserID = workSheetAirDrop.col_values(1)

        for i, userID in enumerate(listOfUserID, start=1):        
            if i == 1:
                continue
            userIDCell = workSheetAirDrop.find(userID)
            userIDCellRow = userIDCell.row

            numberOfFunGuys = workSheetAirDrop.cell(userIDCellRow,3).value
            dateOfOldestFunGuy = workSheetAirDrop.cell(userIDCellRow,4).value

            endDate = date.fromisoformat(nameAirDropDate)
            startDate = date.fromisoformat(dateOfOldestFunGuy)

            months = (endDate.year - startDate.year) * 12 + endDate.month - startDate.month + 1

            coins = (100 * int(numberOfFunGuys))*(1 + months/10)
 
            workSheetAirDrop.update_cell(i, 5, coins)

        return {
            'status': True,
            'errMsg': None,
            'nameAirDropDate': nameAirDropDate
        }

    # User Function
    def insert_user(self, userID: int, discordID: str, walletAddress: str, numberOfFunGuys: int, dateOfOldestFunGuy: date)-> str:
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

    def update_user(self, userID: int, numberOfFunGuys: int = None, dateOfOldestFunGuy: date = None) -> str:
        """
        Update Funguy status of the Discord user.
        """
        workSheet = self.sp.worksheet("UserTbl")
        response = self.check_user(userID)

        if not response['status']:
            return {
                'status': False,
                'errMsg': response['errMsg'],
                'numFunguys': -1,
                'oldestDate': -1
            }

        if(numberOfFunGuys):
            workSheet.update_cell(response['userIDRow'].row, 4, numberOfFunGuys)
        elif(dateOfOldestFunGuy):
            workSheet.update_cell(response['userIDRow'].row, 5, dateOfOldestFunGuy)
        return {
            'status': True,
            'errMsg': None,
            'numFunguys': workSheet.cell(response['userIDRow'].row, 4).value,
            'oldestDate': response['oldestDate']
        }

    def check_user(self, userID: str, walletAddress: str = None):
        """
        Returns the user's number of Funguys and the oldestDate of their Funguy.
        """
        workSheet = self.sp.worksheet("UserTbl")
        userIDRow = workSheet.find(str(userID))
        

        if not userIDRow:
            return {
                'status': False,
                'errMsg': 'User not found.',
                'discordIDRow': -1,
                'numFunguys': -1,
                'oldestDate': -1
            }

        if walletAddress:
            walletAddressRow = workSheet.find(walletAddress)
            if not walletAddressRow and walletAddress:
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
            'oldestDate': workSheet.cell(userIDRow.row, 5).value,
            'walletAddress': workSheet.cell(userIDRow.row, 3).value
        }

if __name__ == '__main__':
    sp = Spreadsheet()
    print(sp.check_user(1))