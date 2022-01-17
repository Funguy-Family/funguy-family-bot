import discord
import json
from datetime import date
from commands.botScript import Spreadsheet
import os
from keep_alive import keep_alive

##############
# To do, make bot only send messages in channel "bot-spam" 
##############

class FunguyBot(discord.Client):
  def __init__(self, admins):
    super().__init__()
    self.sp = Spreadsheet()
    self.admins = admins
    self.newMonth = None

  async def on_ready(self):
    print('Logged on as', self.user)

  async def on_message(self, message):
    """
      Bot Commands
    """
    # try:
    if message.content.startswith('!funguy'):
      content = [i for i in message.content.split(' ') if i != '']
      embed = discord.Embed(title="No Command Detected",
                              description="Type !funguy help for more information.",
                              color=discord.Color.red())
      if len(content) > 1:
        if content[1] == 'help':
          embed = discord.Embed(title="Options",
                                description="`help`\nLists available options.\n\n`joindrop`\nJoin the monthly airdrop!\n\n`add <wallet address> <number of Funguys> <oldest date holding Funguy NFT>`\nAdd new user to the database.\n\n`update [+/-<number of Funguys>/<oldest date holding Funguy NFT (year-month-day)>]`\nUpdate your Funguy collection information!\n\n`view`\nCheck how many Funguy points you have for the airdrop.",
                                color=discord.Color.blue())
          embed.set_author(name='| Funguy Help Menu', icon_url=message.author.avatar_url)

        elif content[1] == 'joindrop':
          res = self.sp.join_airdrop(str(message.author.id))

          if res['status']:
            description = 'Successfully joined airdrop! Good luck!'
            color = discord.Color.green()

            # If new month, populate airdrop columns
            if res['previousAirDropName']:
              self.newMonth = res['previousAirDropName']

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
            args1 = self.check_update_arguments(str(content[3]))
            args2 = self.check_update_arguments(str(content[4]))

            if args1 is not None and args2 is not None:
              res = self.sp.insert_user(message.author.id, message.author.name + "#" + message.author.discriminator, content[2], args1, str(args2))

              if res['status']:
                description = 'Successfully added! You have ' + str(res['numFunguys']) + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
                color = discord.Color.green()
              else:
                description = 'Something went wrong adding you. ' + res['errMsg']
                color = discord.Color.red()
            else:
              description = 'Something went wrong adding you. Please check your arguments.'
              color = discord.Color.red()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Insert User', icon_url=message.author.avatar_url)

        elif content[1] == 'update':
          if len(content) != 3:
            description = 'Insufficient arguments. Please include either the number of Funguys you\'ve added or the earliest date you\'ve been holding Funguy NFTs.'
            color = discord.Color.blue()
          else:
            args = self.check_update_arguments(content[2])
            if args:
              if type(args) == int:
                res = self.sp.update_user(message.author.id, args, None)
              else:
                res = self.sp.update_user(message.author.id, None, str(args))
              if res['status']:
                description = 'Successfully updated your status! You now have **' + res['numFunguys'] + ' Funguys**, with the oldest one being **' + res['oldestDate'] + '**.'
                color = discord.Color.green()
              else:
                description = 'Something went wrong updating your Funguys. ' + res['errMsg']
                color = discord.Color.red()
            else:
              description = 'One of your parameters are incorrect. Please check to make sure you\'re updating the number of Funguys you have (e.g. +2) or updating how long you\'ve been holding Funguys (e.g. 2020-12-1).'
              color = discord.Color.blue()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Update Funguys', icon_url=message.author.avatar_url)

        elif content[1] == 'view':
          res = self.sp.check_user(message.author.id)
          if res['status']:
            description = 'Your wallet address: __' + res['walletAddress'] + '__ has **' + res['numFunguys'] + ' Funguys**, with the oldest one being **' + res['oldestDate'] + '**.'
            color = discord.Color.green()
          else:
            description = 'Something went wrong retrieving your information. ' + res['errMsg']
            color = discord.Color.red()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Check Funguys', icon_url=message.author.avatar_url)

        elif content[1] == 'calculate':
          if message.author.id in self.admins:
            if len(content) != 3:
              description = 'Insufficient arguments. Please include the Airdrop month you want to calculate in the following format: YYYY-MM-01.'
              color = discord.Color.blue()
            else:
              res = self.sp.calculate_TSHY_coin(message.author.id, content[2])
              if res['status']:
                description = "Calculated $TSHY drops. Please check form to verify values."
                color = discord.Color.green()
              else:
                description = 'Something went wrong calculating the $TSHY coins. ' + res['errMsg']
                color = discord.Color.red()              
          else:
            description = 'You are not authorize to use this command. Please contact a mod if you think this is an error.'
            color = discord.Color.red()          

          embed = discord.Embed(description=description,
                                color=color)    
          embed.set_author(name='| Calculate Monthly Drops', icon_url=message.author.avatar_url)

        elif content[1] == 'populate':
          if message.author.id in self.admins:
            if len(content) != 3:
              description = 'Insufficient arguments. Please include the Airdrop month you want to calculate in the following format: YYYY-MM-01.'
              color = discord.Color.blue()
            else:
              res = self.sp.populate_last_month_values(message.author.id, content[2])
              if res['status']:
                description="Populated information. Please check form to verify values."
                color = discord.Color.green()
              else:
                description = 'Something went wrong populating information. ' + res['errMsg']
                color = discord.Color.red()              
          else:
            description = 'You are not authorize to use this command. Please contact a mod if you think this is an error.'
            color = discord.Color.red()   

          embed = discord.Embed(description=description,
                      color=color)         
          embed.set_author(name='| Populate Monthly Drops Manually', icon_url=message.author.avatar_url)

      await message.channel.send(embed=embed)

      if self.newMonth:
        embed = discord.Embed(description='Funguy Bot is doing some calculation for last month! If you type a new command, it might take a little bit of time!',
                              color=discord.Color.orange())       
        embed.set_author(name='| Populate Monthly Drops Automatically')

        await message.channel.send(embed=embed)

        res = self.sp.populate_last_month_values(self.newMonth)

        embed = discord.Embed(description='Calculations are done!',
                              color=discord.Color.green())
        embed.set_author(name='| Populate Monthly Drops Automatically')

        self.newMonth = None

    # except:
    #   embed = discord.Embed(description="Something went wrong with the server. Contact mod",
    #                         color=discord.Color.red())
    #   embed.set_author(name='| Server Error')      
    #   await message.channel.send(embed=embed)

  def check_update_arguments(self, input):
    try:
      return int(input)
    except:
      try:
        split_input = input.split('-')

        if len(split_input) == 3:
          year = int(split_input[0])
          month = int(split_input[1])
          day = int(split_input[2])
          
          assert (year <= date.today().year)
          assert (1 <= month <= 12)
          assert (1 <= day <= 31)
          
          return date(year, month, day)
        else:
          raise Exception('Not a valid date input.')
      except:
        return None

if __name__ == '__main__':
  # keep_alive()

  # admins = os.getenv('admins')
  # discord_token = os.getenv('discord_token')
  
  # FunguyBot(admins).run(discord_token)

  f = open('credentials/funguyfamily.json')
  data = json.load(f)

  FunguyBot(data['admins']).run(data['discord_token'])
  