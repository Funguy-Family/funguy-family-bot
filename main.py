import discord
import json
from datetime import date
from commands.botScript import Spreadsheet


##############
# To do, make bot only send messages in channel "bot-spam" 
##############

class FunguyBot(discord.Client):
  def __init__(self, admins):
    super().__init__()
    self.sp = Spreadsheet()
    self.admins = admins

  async def on_ready(self):
    print('Logged on as', self.user)

  async def on_message(self, message):
    """
      Bot Commands
    """
    if message.content.startswith('!funguy'):
      content = [i for i in message.content.split(' ') if i != '']
      embed = discord.Embed(title="No Command Detected",
                              description="Type !funguy help for more information.",
                              color=discord.Color.red())

      if content[1] == 'help':
        embed = discord.Embed(title="Options",
                              description="`help`\nLists available options.\n\n`joindrop`\nJoin the monthly airdrop!\n\n`add <wallet address> <number of Funguys> <oldest date holding Funguy NFT>`\nAdd new user to the database.\n\n`update [+/-<number of Funguys>/<oldest date holding Funguy NFT>]`\nUpdate your Funguy collection count!\n\n`view`\nCheck how many Funguy points you have for the airdrop.",
                              color=discord.Color.blue())
        embed.set_author(name='| Funguy Help Menu', icon_url=message.author.avatar_url)

      elif content[1] == 'joindrop':
        res = self.sp.join_airdrop(message.author.id)

        if res['status']:
          description = 'Successfully joined airdrop! Good luck!'
          color = discord.Color.green()

          #################3
          # To DO:
          #################
          # Joind_airdrop return newMonth
          # If true, that means we are in new month and you need to call this function
          # populate_last_month_values(nameAirDropDate)
          # Join_airdrop returns the previousAirDropName, use that for the populate_last_month_values(nameAirDropDate)
          
        else:
          description = 'Failed to join. ' + res['errMsg']
          color = discord.Color.red()

        embed = discord.Embed(description=description,
                              color=color)
        embed.set_author(name='| Joining Airdrop', icon_url=message.author.avatar_url)

      elif content[1] == 'add':
        if len(content) != 5:
          description = 'Insufficient arguments. Please include your wallet address, number of Funguys you\'ve added, and the oldest Funguy you have.'
          color = discord.Color.blue()
        else:
          
          #################3
          # To DO:
          #################
          # Check if right order of parameters
          
          res = self.sp.insert_user(message.author.id, message.author.name + "#" + message.author.discriminator, content[2], content[3], content[4])
          if res['status']:
            description = 'Successfully added! You have ' + res['numFunguys'] + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
            color = discord.Color.green()
          else:
            description = 'Something went wrong adding you. ' + res['errMsg']
            color = discord.Color.red()

        embed = discord.Embed(description=description,
                              color=color)
        embed.set_author(name='| Insert User', icon_url=message.author.avatar_url)

      elif content[1] == 'update':
        if len(content) != 3:
          description = 'Insufficient arguments. Please include either the number of Funguys you\'ve added or the earliest date you\'ve been holding Funguy NFTs.'
          color = discord.Color.blue()
        else:

          #############3
          # Update to do time fix TODO
          #############

          if self.check_update_arguments(content[2]):
            res = self.sp.update_user(message.author.id, content[2])
            if res['status']:
              description = 'Successfully updated your status! You now have ' + res['numFunguys'] + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
              color = discord.Color.green()
            else:
              description = 'Something went wrong updating your Funguys. ' + res['errMsg']
              color = discord.Color.red()
          else:
            description = 'One of your parameters are incorrect. Please check to make sure you\'re updating the number of Funguys you have (e.g. +2) or updating how long you\'ve been holding Funguys (e.g. 12/1/2020).'
            color = discord.Color.blue()

        embed = discord.Embed(description=description,
                              color=color)
        embed.set_author(name='| Update Funguys', icon_url=message.author.avatar_url)

      #########33
      # TODO
      ###########3
      # Add wallet addrss to description too


      elif content[1] == 'view':
        res = self.sp.check_user(message.author.id)
        if res['status']:
          description = 'You have ' + res['numFunguys'] + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
          color = discord.Color.green()
        else:
          description = 'Something went wrong retrieving your information. ' + res['errMsg']
          color = discord.Color.red()

        embed = discord.Embed(description=description,
                              color=color)
        embed.set_author(name='| Check Funguys', icon_url=message.author.avatar_url)

      #############
      # Todo, add calcualte function
      #############
      elif content[1] == 'calculate' and message.author.id in self.admins:
        # insert Frendy function here
        embed = discord.Embed(description="Calculated $TSHY drops.",
                              color=discord.Color.green())  
        embed.set_author(name='| Calculate Monthly Drops', icon_url=message.author.avatar_url)

      ##########
      # Also add fucntion to call populate_last_month_values for admin only
      #####

      await message.channel.send(embed=embed)

  def check_update_arguments(self, input):
    if input.startsWith('+-'):
      try:
        int(input[1:])
        return True
      except:
        return False
    
    try:
      ########3
      # Todo
      #######
      # make sure datetime is like yyyy-mm-dd
      
      date(input)
      return True
    except:
      return False

if __name__ == '__main__':
  f = open('credentials/funguyfamily.json')
  data = json.load(f)
  
  FunguyBot(data['admins']).run(data['discord_token'])
  