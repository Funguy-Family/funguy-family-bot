from datetime import datetime
import pytz

import gspread
from oauth2client.service_account import ServiceAccountCredentials





#first worksheet = 0
class spreadSheet():

    def __init__(self):
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/funguyfamily.json', scope)

        gc = gspread.authorize(credentials)    
        self.sp = gc.open('FunGuy_test')     
        
    '''
        Spread Sheet Functions
    '''

    #===============
    # create a new spreadSheet
    # with only one column (UserID)
    #===============
    # To do: add error check if worksheet name already exist
    def createWorkSheet(self, name):
        workSheet = self.sp.add_worksheet(title=name, rows="1", cols="1")
        workSheet.append_row(["userID"])
    
    def doWeNeedToCreatedWorkSheet(self):
        utc = pytz.timezone('UTC')
        currentAirDropDate = datetime.now(utc)
        nameAirDropDate = str(currentAirDropDate.year) + '-' + str(currentAirDropDate.month)
    
        # Check if we are in new month and need to create a new entry
        try:
            self.sp.worksheet(nameAirDropDate)  
            isItCreated = True        
        except Exception:
            isItCreated = False

        if(not isItCreated):
            self.createWorkSheet(nameAirDropDate)  

        return nameAirDropDate
    '''
        Signing to AirDrop
    '''

    def joinAirDrop(self, discordID, walletAddress):

        userIDList = self.checkUser(discordID, walletAddress)
        userID = userIDList[1]
        if(userID == -1):
            return "Could not find UserID, please create a new entry beforing joininig"
        
        nameAirDropDate = self.doWeNeedToCreatedWorkSheet()

        workSheet = self.sp.worksheet(nameAirDropDate)
        
        userIDRow = workSheet.find(userID)

        if(userIDRow is None):
            workSheet.append_row([userID])
            
        return "You were added successfully"

    def didIJoinAirDrop(self, discordID, walletAddress):

        userIDList = self.checkUser(discordID, walletAddress)
        userID = userIDList[1]
        if(userID == -1):
            return "Could not find this user in UserTbl, please create a new entry beforing joininig"
        
        nameAirDropDate = self.doWeNeedToCreatedWorkSheet()

        workSheet = self.sp.worksheet(nameAirDropDate)
        
        userIDRow = workSheet.find(userID)

        if(userIDRow is None):
            return "You have not joined this airDrop: " + nameAirDropDate

        return "You already joined this airDrop: " + nameAirDropDate

    
    '''
        User functions
    '''
    
    #===============
    # Guarantees that there is only one DiscordUser and only one wallet with that address
    #===============
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

        return "Inserted new User"

    def updateUser(self, discordID: str, walletAddress: str, numberOfFunGuys: int, dateOfOldestFunGuy: datetime) -> str:
        workSheet = self.sp.worksheet("UserTbl")
        discordIDRow = workSheet.find(discordID)
        walletAddressRow = workSheet.find(walletAddress)

        # If your discordID is already used.
        if(discordIDRow is None):
            return "This discordUser is not an existing user"
        
        elif(walletAddressRow is None):
            return "This wallet address does not exist"
        
        elif(discordIDRow.row != walletAddressRow.row):
            return "This discordID does not match this Wallet"

 
        workSheet.update_cell(discordIDRow.row, 4, numberOfFunGuys)
        workSheet.update_cell(discordIDRow.row, 5, dateOfOldestFunGuy)

        return "updated new user"

    def checkUser(self, discordID: str, walletAddress: str):
        workSheet = self.sp.worksheet("UserTbl")
        discordIDRow = workSheet.find(discordID)
        walletAddressRow = workSheet.find(walletAddress)

        if(discordIDRow.row == walletAddressRow.row):
            return  "Your numberOfFunGuys is" + workSheet.cell(discordIDRow.row, 4).value + " and your oldestDate is " + workSheet.cell(discordIDRow.row, 5).value, workSheet.cell(discordIDRow.row, 1).value
        else:
            return "We couldn't find your information.", -1

sp = spreadSheet()
#print(sp.didIJoinAirDrop("PringlesOriginas#39682", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE1"))


#print(sp.joinAirDrop("PringlesOriginas#39682", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE1"))
#print(sp.checkUser("PringlesOriginas#3968", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE"))

#print(sp.updateUser("PringlesOriginas#3968", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE","8",'12/01/23'))

#sp.insertNewUser("PringlesOriginas#396812", "0xf7ea4da94Ef718DB72E96f692be43236FEb36ECE12221","6","huly")
#sp.createWorkSheet("Testing")

