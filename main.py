import discord
import json
from commands.botScript import Spreadsheet

class FunguyBot(discord.Client):
  def __init__(self):
    super().__init__()
    self.sp = Spreadsheet()

  async def on_ready(self):
    print('Logged on as', self.user)

  async def on_message(self, message):
    if message.content.startswith('!funguy'):
      content = [i for i in message.content.split(' ') if len(i) > 1]
      if 1 < len(content):
        if content[1] == 'help':
          embed = discord.Embed(title="Options",
                                description="`help`\nLists available options.\n\n`joindrop <walletAddress>`\nJoin the monthly airdrop!\n\n`update`\nUpdate your Funguy collection count!\n\n`view`\nCheck how many Funguy points you have for the airdrop.",
                                color=discord.Color.blue())
          embed.set_author(name='| Funguy Help Menu', icon_url=message.author.avatar_url)

        elif content[1] == 'joindrop':
          if len(content) != 3:
            description = 'Insufficient arguments. Please include your wallet address'
            color = discord.Color.blue()
          else:
            res = self.sp.join_airdrop(str(message.author.id), content[2])

            if res['status']:
              description = 'Successfully joined airdrop! Good luck!'
              color = discord.Color.green()
            else:
              description = 'Failed to join. ' + res['errMsg']
              color = discord.Color.red()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Joining Airdrop', icon_url=message.author.avatar_url)

        elif content[1] == 'update':
          if len(content) != 5:
            description = 'Insufficient arguments. Please include your wallet address, number of Funguys you\'ve added, and the oldest Funguy you have.'
            color = discord.Color.blue()
          else:
            res = self.sp.update_user(str(message.author.id), content[2], content[3], content[4])
            if res['status']:
              description = 'Successfully updated your status! You now have ' + res['numFunguys'] + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
              color = discord.Color.green()
            else:
              description = 'Something went wrong updating your Funguys. ' + res['errMsg']
              color = discord.Color.red()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Update Funguys', icon_url=message.author.avatar_url)

        elif content[1] == 'view':
          if len(content) != 3:
            description = 'Insufficient arguments. Please include your wallet address'
            color = discord.Color.blue()
          else:
            res = self.sp.check_user(str(message.author.id), content[2])
            if res['status']:
              description = 'You have ' + res['numFunguys'] + ' Funguys, with the oldest one being ' + res['oldestDate'] + '.'
              color = discord.Color.green()
            else:
              description = 'Something went wrong retrieving your information. ' + res['errMsg']
              color = discord.Color.red()

          embed = discord.Embed(description=description,
                                color=color)
          embed.set_author(name='| Check Funguys', icon_url=message.author.avatar_url)

      else:
        embed = discord.Embed(title="No Command Detected",
                              description="Type !funguy help for more information.",
                              color=discord.Color.red())

      await message.channel.send(embed=embed)

if __name__ == '__main__':
  f = open('credentials/funguyfamily.json')
  data = json.load(f)
  
  FunguyBot().run(data['discord_token'])
  