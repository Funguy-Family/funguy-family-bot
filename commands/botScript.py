import pytz
import gspread
from datetime import date, datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import os
class Spreadsheet():
    def __init__(self):
        """
        Establish credentials from `credentials/funguyfamily.json` and create sp.
        """

        # Junk solution for REplit since we cannot hide folders..
        # use environ
        variables_keys = {
            "type": os.environ.get("type"),
            "project_id": os.environ.get("project_id"),
            "private_key_id": os.environ.get("private_key_id"),
            "private_key": os.environ.get("private_key"),
            "client_email": os.environ.get("client_email"),
            "client_id": os.environ.get("client_id"),
            "auth_uri": os.environ.get("auth_uri"),
            "token_uri": os.environ.get("token_uri"),
            "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": os.environ.get("client_x509_cert_url")
        }        


        scope = ['https://www.googleapis.com/auth/drive']
        # credentials = ServiceAccountCredentials.from_json_keyfile_dict(variables_keys, scope)

        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/funguyfamily.json', scope)

        gc = gspread.authorize(credentials)    
        self.sp = gc.open('FunGuy_test')     

    # Spreadsheet Functions
    def create_worksheet(self, name: str):
        """
        Create a spreadsheet with only 1 column (userID).
        """
        assert (type(name) == str), "Worksheet name is not a string."
        workSheet = self.sp.add_worksheet(title=name, rows="1", cols="1")
        workSheet.append_row(["userID", "walletAddress", "numberOfFunGuys", "dateOfOldestFunGuy", "TSHY COIN"])

    def get_current_worksheet(self):
        """
        Check if you need to create a worksheet. Creates a new one for a new month.
        """
        utc = pytz.timezone('UTC')
        currentAirDropDate = datetime.now(utc)
        nameAirDropDate = str(currentAirDropDate.year) + '-' + str(currentAirDropDate.month) + '-01' 
        previousAirDropName = None

        # Check if we are in new month and need to create a new entry
        try:
            self.sp.worksheet(nameAirDropDate)  
            worksheet_list = self.sp.worksheets()
            previousAirDropName = worksheet_list[-2].title           
        except Exception:
            self.create_worksheet(nameAirDropDate)

        return {
            'airdrop_date': nameAirDropDate,
            'prev_airdrop_date': previousAirDropName
        }

    # Airdrop Functions
    def join_airdrop(self, userID: str):
        """
        Add user to airdrop.
        """
        response = self.check_user(userID)
        if not response['status']:
            return {
                'status': response['status'],
                'errMsg': response['errMsg'],
                'previousAirDropName': None
            }
        
        res = self.get_current_worksheet()

        workSheet = self.sp.worksheet(res['airdrop_date'])
        userIDRow = workSheet.find(userID)
        if userIDRow is None:
            workSheet.append_row([userID])

        return {
            'status': response['status'],
            'previousAirDropName': res['prev_airdrop_date']
        }
 
    def populate_last_month_values(self, airdrop_date: str):

        try:
            workSheetAirDrop = self.sp.worksheet(airdrop_date)
        except:
            return {
                'status': False,
                'errMsg': "Invalid form name."
            }

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
            'status': True
        }

    def calculate_TSHY_coin(self, airdrop_date: str):
        try:
            workSheetAirDrop = self.sp.worksheet(airdrop_date)
        except:
            return {
                'status': False,
                'errMsg': "Invalid form name."
            }
        
        listOfUserID = workSheetAirDrop.col_values(1)

        for i, userID in enumerate(listOfUserID, start=1):        
            if i == 1:
                continue
            userIDCell = workSheetAirDrop.find(userID)
            userIDCellRow = userIDCell.row

            numberOfFunGuys = workSheetAirDrop.cell(userIDCellRow,3).value
            dateOfOldestFunGuy = workSheetAirDrop.cell(userIDCellRow,4).value

            endDate = date.fromisoformat(airdrop_date)
            startDate = date.fromisoformat(dateOfOldestFunGuy)

            months = (endDate.year - startDate.year) * 12 + endDate.month - startDate.month + 1

            coins = (100 * int(numberOfFunGuys))*(1 + months/10)
 
            workSheetAirDrop.update_cell(i, 5, coins)

        return {
            'status': True
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
            }

        if(numberOfFunGuys):
            workSheet.update_cell(response['userIDRow'].row, 4, numberOfFunGuys)
        elif(dateOfOldestFunGuy):
            workSheet.update_cell(response['userIDRow'].row, 5, dateOfOldestFunGuy)
        return {
            'status': True,
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
                'errMsg': 'User not found.'
            }

        if walletAddress:
            walletAddressRow = workSheet.find(walletAddress)
            if not walletAddressRow and walletAddress:
                return {
                    'status': False,
                    'errMsg': 'Wallet address not found.'
                }

        return {
            'status': True,
            'userIDRow': userIDRow,
            'walletAddress': workSheet.cell(userIDRow.row, 3).value,
            'numFunguys': workSheet.cell(userIDRow.row, 4).value,
            'oldestDate': workSheet.cell(userIDRow.row, 5).value
        }

if __name__ == '__main__':
    sp = Spreadsheet()