from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/funguyfamily.json', scope)

gc = gspread.authorize(credentials)

#first worksheet = 0
class spreadSheet():

    def __init__(self, sp):
        self.sp = sp 

    #===============
    # create a new spreadSheet
    # with only one column (UserID)
    #===============
    def createWorkSheet(self, name):
        workSheet = self.sp.add_worksheet(title=name, rows="1", cols="1")
        workSheet.append_row(["userID"])

    def insertNewUser(self, discordID: str, walletAddress: str, numberOfFunGuys: int, dateOfOldestFunGuy: datetime)-> str:
        workSheet = self.sp.worksheet("UserTbl")
        discordIDRow = workSheet.find(discordID)
        walletAddressRow = workSheet.find(walletAddress)

        # If your discordID is already used.
        if(discordIDRow is not None):
            return "This discord user is already being used"
        
        elif(walletAddressRow is not None):
            return "This wallet address is already being used"

        # If the wallet and discordId has never being used, add a new user
        workSheet.append_row([len(workSheet.get_all_values()), discordID, walletAddress, numberOfFunGuys, dateOfOldestFunGuy])



sp = spreadSheet(gc.open('FunGuy_test'))
sp.insertNewUser("PringlesOriginas#396812", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE12221","test","test")
#sp.createWorkSheet("Testing")

