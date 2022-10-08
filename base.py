# MIT License

# Polymart Verification Bot Base
# Version 3.1.2 (oss/main)

# A bot that allow you to do ownership verification
# Configurable though YAML-based config
# Note: I wrote this in 1 day, code is very bad, but it works lol

# Requires aiohttp, discord-py-interactions and ruamel.yaml, install them with pip3

# Check the config for a brief idea how to use this thing

from ruamel import yaml
from pathlib import Path
import aiohttp
import random
import json
import interactions
import os
import datetime

config = Path('config.yml')
yaml1 = yaml.YAML(typ='safe')
configData = yaml1.load(config)

# Bot version
# Don't change this unless PR
# major.minor.patch
bot_version = "3.1.2"

# <closed/oss> / <git branch>
# Don't change this unless you make a closed fork or change git branch
bot_branch = "oss/main"

# Don't change this 
base_url = "https://api.polymart.org"

# Also don't touch this
resourceList = {}

# Config stuff
token = configData['discord-bot-token']
service = configData['service']
server_id = configData['discord-server-id']
global_api_key = configData['global-api-key']
activity = configData['activity']
channelRestrict = configData['channel']

class PolymartAPI:
   async def generateVerifyURL():
       url = base_url + "/v1/generateUserVerifyURL"
       arg = {'service':service}
       token = None
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             token = json.loads(str(await r.text()))['response']['result']['url']
             return token

   async def verifyUser(token):
       url = base_url + "/v1/verifyUser"
       arg = {'service':service,'token':token}
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             id = json.loads(str(await r.text()))['response']['result']['user']['id']
             return id

   async def getUserData(api_key, user_id):
       url = base_url + "/v1/getUserData"
       arg = {'api_key':api_key,'user_id':user_id}
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
              return json.loads(str(await r.text()))

   async def getResourceUserData(api_key, resource_id, user_id):
       url = base_url + "/v1/getResourceUserData"
       arg = {'api_key':api_key,'resource_id':resource_id,'user_id':user_id}
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
             return json.loads(str(await r.text()))

class Resource:
    resourceName = None
    resourceID = None
    resourceRoleID = None
    resourceIcon = None
    resourceSpecificKey = None
    def __init__(self, resourceName, resourceID, resourceRoleID, resourceIcon, resourceSpecificKey):
        self.resourceName = resourceName
        self.resourceID = resourceID
        self.resourceRoleID = resourceRoleID
        self.resourceIcon = resourceIcon
        self.resourceSpecificKey = resourceSpecificKey
    def getResourceName(self):
        return self.resourceName
    def getResourceID(self):
        return self.resourceID
    def getResourceRoleID(self):
        return self.resourceRoleID
    def getResourceIcon(self):
        return self.resourceIcon
    def getResourceSpecificKey(self):
        return self.resourceSpecificKey

print("This bot is licensed under MIT license")
print("Bot Token: " + token)
bot = interactions.Client(token=token, presence=interactions.ClientPresence(activities=[interactions.PresenceActivity(name=activity, type=interactions.PresenceActivityType.GAME)]))

# Commands

@bot.command(
    name="verify",
    description="Verify ownership of plugins",
    scope=server_id
)
async def verify(ctx: interactions.CommandContext):
   channel_id = ctx.channel.id
   if channelRestrict is not None:
       if channelRestrict != channel_id:
           errEmbed = interactions.Embed(description=":x: Sorry, you cannot use this command in this channel!")
           await ctx.send(embeds=errEmbed, ephemeral=True)
           return
   getTokenButton = interactions.Button(
        style=interactions.ButtonStyle.LINK,
        label="Get Token",
        url=await PolymartAPI.generateVerifyURL()
   )
   verifyButton = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Verify",
        custom_id="verify"
   )
   cancelButton = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="Cancel",
        custom_id="cancel"
   )
   row = interactions.ActionRow(
    components=[getTokenButton, verifyButton, cancelButton]
   )
   infoEmbed = interactions.Embed(title="Hi there!", description="Hi there " + str(ctx.author) + "! This form is here to help you get started! \n\nTo get started, click the **Get Token** button and it will automatically open a link. \nLogin into your Polymart account and it will generate a token. \nCopy that token and click the **Verify** button, enter your token and let the bot handle the rest! \n\nIf you have bought a plugin after verification and would like to get verified for that plugin, just do verify again! \n\nIf you ran this command by accident, click to the **Cancel** button to cancel this form.", color=0x33a343)
   infoEmbed.set_footer(text="Requested by " + str(ctx.author) + " at " + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")) + "  |  Bot version " + bot_version + " (" + bot_branch + ")")
   await ctx.send(embeds=infoEmbed, components=row)

@bot.component("verify")
async def verify(ctx):
    message = ctx.message
    if ctx.author.id != message.interaction.user.id:
       infoEmbed = interactions.Embed(description=":x: Sorry, This verification form is for " + str(message.interaction.user) + "! Please run **/verify** if you want to verify yourself.")
       await ctx.send(embeds=infoEmbed, ephemeral=True)
       return
    tokenInput = interactions.TextInput(
        style=interactions.TextStyleType.SHORT,
        label="Enter your Polymart token",
        custom_id="user_token",
    )
    modal = interactions.Modal(
        title="Your Polymart Token",
        custom_id="user_token_response",
        components=[tokenInput],
    )
    await ctx.popup(modal)

@bot.component("cancel")
async def cancel(ctx):
    message = ctx.message
    if ctx.author.id != message.interaction.user.id:
       infoEmbed = interactions.Embed(description=":x: Sorry, This verification form is for " + str(message.interaction.user) + "! Please run **/verify** if you want to verify yourself.")
       await ctx.send(embeds=infoEmbed, ephemeral=True)
       return
    embed = interactions.Embed(description=":white_check_mark: Cancelled verification for " + str(message.interaction.user) + "!")
    await ctx.edit(embeds=embed, components=None)
    finalEmbed = interactions.Embed(description=":white_check_mark: Cancelled successfully!")
    await ctx.send(embeds=finalEmbed, ephemeral=True)

@bot.modal("user_token_response")
async def user_token_response(ctx, response: str):
    await ctx.defer()
    token = response
    member = ctx.member
    user_name, user_id = await getUser(token, global_api_key)
    base_success_text_part_1 = "Username: " + user_name + "\nUser ID: " + user_id + "\n\nStatus:"
    base_success_text_part_2 = "\n\nVerification Successfully!"
    final_success_text = ""
    await getAllResources()
    for r in resourceList:
        specificKey = global_api_key
        if resourceList[r].getResourceSpecificKey() is not None:
            specificKey = r.getResourceSpecificKey()
        final_success_text += "\n" + resourceList[r].getResourceIcon() + " **" + resourceList[r].getResourceName() + "**: " + str(await checkAndVerify(ctx, specificKey, resourceList[r].getResourceID(), token, resourceList[r].getResourceRoleID()))
    text = base_success_text_part_1 + final_success_text + base_success_text_part_2
    text2 = text.replace("False", ":x:")
    text3 = text2.replace("True", ":white_check_mark:")
    text4 = text3.replace("None", "")
    embed = interactions.Embed(title="Verification Summary for User " + str(ctx.author), description=text4, color=0x33a343)
    embed.set_footer(text="Requested by " + str(ctx.author) + " at " + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")) + "  |  Bot version " + bot_version + " (" + bot_branch + ")")
    embed.set_thumbnail(url=member.user.avatar_url)
    await ctx.edit(embeds=embed, components=None)
    finalEmbed = interactions.Embed(description=":white_check_mark: Verified " + str(ctx.author) + " successfully!")
    await ctx.send(embeds=finalEmbed)
    
async def getUser(user_token, api_key):
    user_id = await PolymartAPI.verifyUser(user_token)
    user_data = await PolymartAPI.getUserData(api_key, user_id)
    user_name = user_data['response']['user']['username']
    return user_name, user_id
    
async def checkAndVerify(context, api_key, resource_id, user_token, verified_role_id):
    user_id = await PolymartAPI.verifyUser(user_token)
    user_data = await PolymartAPI.getUserData(api_key, user_id)
    resource_user_data = await PolymartAPI.getResourceUserData(api_key, resource_id, user_id)
    if context.author.roles and verified_role_id not in context.author.roles or not context.author.roles:
        if resource_user_data['response']['resource']['purchaseValid']:
            await context.author.add_role(verified_role_id, server_id)
            return True
        else:
            return False
    elif context.author.roles and verified_role_id in context.author.roles:
            return True

async def getAllResources():
    resourceFile = Path('resources.yml')
    resourceData = yaml1.load(resourceFile)
    for r in resourceData:
        resource = resourceData[r]
        resourceConf = Resource(resource['resource-name'], resource['resource-id'], resource['discord-role-id'], resource['icon'], resource['api-key'])
        resourceList[r] = resourceConf
            
bot.start()
