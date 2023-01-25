# PolymartBase
# Licensed under MIT license

# Code is not-so-great, but it works!

from ruamel import yaml
from pathlib import Path
import aiohttp
import random
import json
import interactions
import os
import datetime

yaml1 = yaml.YAML(typ='safe')
configData = yaml1.load(Path('config.yml'))
resourceData = yaml1.load(Path('resources.yml'))

# Bot version
# i'm a bit fucked with versioning rn
bot_version = "3.2.0"

# Git branch and whether it is open source or closed source
bot_branch = "oss/main"

# Used internally
resourceList = {}

def verbose(msg):
    if configData['debug']['verbose'] == True:
        time = datetime.datetime.now().strftime('%H:%M:%S')
        print("[" + str(time) + " - VERBOSE] " + msg)

class PolymartAPI:
   async def generateVerifyURL():
       url = configData['base-url'] + "/v1/generateUserVerifyURL"
       arg = {'service':configData['service']}
       verbose("PolymartAPI: generateVerifyURL() called, parameters: " + str(arg))
       token = None
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             token = json.loads(str(await r.text()))['response']['result']['url']
             verbose("PolymartAPI: generateVerifyURL() success, token: " + str(token))
             return token

   async def verifyUser(token):
       url = configData['base-url'] + "/v1/verifyUser"
       arg = {'service':configData['service'],'token':token}
       verbose("PolymartAPI: verifyUser() called, parameters: " + str(arg))
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             id = json.loads(str(await r.text()))['response']['result']['user']['id']
             verbose("PolymartAPI: verifyUser() success, ID: " + str(id))
             return id

   async def getUserData(api_key, user_id):
       url = configData['base-url'] + "/v1/getUserData"
       arg = {'api_key':api_key,'user_id':user_id}
       verbose("PolymartAPI: getUserData() called, parameters: " + str(arg))
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
              verbose("PolymartAPI: getUserData() success, JSON data: " + str(await r.text()))
              return json.loads(str(await r.text()))

   async def getResourceUserData(api_key, resource_id, user_id):
       url = configData['base-url'] + "/v1/getResourceUserData"
       arg = {'api_key':api_key,'resource_id':resource_id,'user_id':user_id}
       verbose("PolymartAPI: getResourceUserData() called, parameters: " + str(arg))
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
             verbose("PolymartAPI: getResourceUserData() success, JSON data: " + str(await r.text()))
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

print("PolymartBase " + str(bot_version))
print("Licensed under the permissive MIT license")
bot = interactions.Client(token=configData['bot-token'])
if configData['activity'] is not None:
    bot = interactions.Client(token=configData['bot-token'], presence=interactions.ClientPresence(activities=[interactions.PresenceActivity(name=configData['activity'], type=interactions.PresenceActivityType.GAME)]))

# Commands

@bot.command(
    name="reload",
    description="Reload config files",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=configData['server-id']
)
async def reload(ctx: interactions.CommandContext):
    verbose("Reload command triggered by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))
    configData = yaml1.load(Path('config.yml'))
    resourceData = yaml1.load(Path('resources.yml'))
    infoEmbed = interactions.Embed(description=configData['indicator']['yessir'] + " Reload config files successfully!", color=0x33a343)
    infoEmbed.set_footer(text="Requested by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + " at " + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")) + "  |  Bot version " + bot_version + " (" + bot_branch + ")")
    await ctx.send(embeds=infoEmbed, ephemeral=True)
    verbose("Reload command success for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))

@bot.command(
    name="verify",
    description="Verify ownership of plugins",
    scope=configData['server-id']
)
async def verify(ctx: interactions.CommandContext):
   verbose("Verify command triggered by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))
   channel_id = ctx.channel.id
   if configData['channel-id'] is not None:
       if configData['channel-id'] != channel_id:
           errEmbed = interactions.Embed(description=configData['indicator']['nop'] + " Sorry, you cannot use this command in this channel!")
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
   row = interactions.ActionRow(
    components=[getTokenButton, verifyButton]
   )
   infoEmbed = interactions.Embed(title="Hi there!", description="Hi there " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "! This form is here to help you get started! \n\nTo get started, click the **Get Token** button and it will automatically open a link. \nLogin into your Polymart account and it will generate a token. \nCopy that token and click the **Verify** button, enter your token and let the bot handle the rest! \n\nIf you have bought a plugin after verification and would like to get verified for that plugin, just do verify again!", color=0x33a343)
   infoEmbed.set_footer(text="Requested by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + " at " + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")) + "  |  Bot version " + bot_version + " (" + bot_branch + ")")
   await ctx.send(embeds=infoEmbed, components=row, ephemeral=True)

@bot.component("verify")
async def verify(ctx):
    verbose("Verify button interacted by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))
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

@bot.modal("user_token_response")
async def user_token_response(ctx, response: str):
    verbose("Token received, verifying " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "...")
    await ctx.defer()
    resourcesCount = 0
    ownedResources = 0
    token = response
    member = ctx.member
    user_name, user_id = await getUser(response, configData['global-api-key'])
    base_success_text_part_1 = "Username: " + user_name + "\nUser ID: " + user_id + "\n\nStatus:"
    base_success_text_part_2 = "\n\nVerification Successfully!"
    final_success_text = ""
    await getAllResources()
    for r in resourceList:
        verbose("Checking ownership of resource " + str(resourceList[r].getResourceName()) + " for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "...")
        resourcesCount += 1
        specificKey = configData['global-api-key']
        if resourceList[r].getResourceSpecificKey() is not None:
            specificKey = resourceList[r].getResourceSpecificKey()
        ownershipStatus = await checkAndVerify(ctx, specificKey, resourceList[r].getResourceID(), token, resourceList[r].getResourceRoleID())
        if ownershipStatus == True:
            ownedResources += 1
            verbose(str(ctx.author.name) + "#" + str(ctx.author.discriminator) + " owns resource " + str(resourceList[r].getResourceName()))
        final_success_text += "\n" + resourceList[r].getResourceIcon() + " **" + resourceList[r].getResourceName() + "**: " + str(ownershipStatus)
        verbose("Finished checking ownership of resource " + str(resourceList[r].getResourceName()) + " for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "!")
    text = base_success_text_part_1 + final_success_text + base_success_text_part_2
    text2 = text.replace("False", configData['indicator']['nop'])
    text3 = text2.replace("True", configData['indicator']['yessir'])
    text4 = text3.replace("None", "")
    verbose("Summary for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + ": owned " + str(ownedResources) + "/" + str(resourcesCount))
    embed = interactions.Embed(title="Verification Summary for User " + str(ctx.author.name) + "#" + str(ctx.author.discriminator), description=text4, color=0x33a343)
    embed.set_footer(text="Requested by " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + " at " + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")) + "  |  Bot version " + bot_version + " (" + bot_branch + ")")
    if configData['display-user-avatar'] == True:
        embed.set_thumbnail(url=member.user.avatar_url)
    verbose("Deleting previous verification form for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))
    await ctx.edit("test")
    await ctx.send(embeds=embed)
    verbose("Verify command success for " + str(ctx.author.name) + "#" + str(ctx.author.discriminator))
    
async def getUser(user_token, api_key):
    verbose("getUser() called, parameters: " + str(user_token) + ", " + str(api_key))
    user_id = await PolymartAPI.verifyUser(user_token)
    user_data = await PolymartAPI.getUserData(api_key, user_id)
    user_name = user_data['response']['user']['username']
    verbose("getUser() success, results: " + str(user_name) + ", " + str(user_id))
    return user_name, user_id
    
async def checkAndVerify(context, api_key, resource_id, user_token, verified_role_id):
    verbose("checkAndVerify() called, parameters: " + str(api_key) + ", " + str(resource_id) + ", " + str(user_token) + ", " + str(verified_role_id))
    user_id = await PolymartAPI.verifyUser(user_token)
    user_data = await PolymartAPI.getUserData(api_key, user_id)
    resource_user_data = await PolymartAPI.getResourceUserData(api_key, resource_id, user_id)
    if context.author.roles and verified_role_id not in context.author.roles or not context.author.roles:
        if resource_user_data['response']['resource']['purchaseValid']:
            verbose("checkAndVerify() success, adding role...")
            await context.author.add_role(verified_role_id, configData['server-id'])
            return True
        else:
            verbose("checkAndVerify() success")
            return False
    elif context.author.roles and verified_role_id in context.author.roles:
        verbose("checkAndVerify() success")
        return True

async def getAllResources():
    verbose("getAllResources() called")
    for r in resourceData:
        resource = resourceData[r]
        resourceConf = Resource(resource['resource-name'], resource['resource-id'], resource['role-id'], resource['icon'], resource['api-key'])
        resourceList[r] = resourceConf
    verbose("getAllResources() success")
            
bot.start()
