# PolymartBase
# Licensed under MIT license

# THIS CODE IS FOR VERSION 3.2.4, WHICH IS AN ATTEMPT TO IMPLEMENT SPIGOTMC RESOURCE SUPPORT
# IT'S NOT YET READY TO USE IN PRODUCTION

# Powered by terrible code written by a dumb weeb

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
bot_version = "3.2.4-indev"

# Git branch and whether it is open source or closed source
bot_branch = "oss/3.2.4"

class PolymartAPI:
   async def generateVerifyURL():
       url = configData['providers']['polymart']['base-url'] + "/v1/generateUserVerifyURL"
       arg = {'service':configData['providers']['polymart']['service']}
       token = None
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             token = json.loads(str(await r.text()))['response']['result']['url']
             return token

   async def verifyUser(token):
       url = configData['providers']['polymart']['base-url'] + "/v1/verifyUser"
       arg = {'service':configData['providers']['polymart']['service'],'token':token}
       async with aiohttp.ClientSession() as session:
          async with session.get(url, json=arg) as r:
             id = json.loads(str(await r.text()))['response']['result']['user']['id']
             return id

   async def getUserData(api_key, user_id):
       url = configData['providers']['polymart']['base-url'] + "/v1/getUserData"
       arg = {'api_key':api_key,'user_id':user_id}
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
              return json.loads(str(await r.text()))

   async def getResourceUserData(api_key, resource_id, user_id):
       url = configData['providers']['polymart']['base-url'] + "/v1/getResourceUserData"
       arg = {'api_key':api_key,'resource_id':resource_id,'user_id':user_id}
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
             return json.loads(str(await r.text()))

   async def getAccountType(user_id):
       url = configData['providers']['polymart']['base-url'] + "/v1/getAccountInfo"
       arg = {'user_id':user_id}
       async with aiohttp.ClientSession() as session:
          async with session.post(url, json=arg) as r:
             try:
                # why tf do you need to do this
                # the type property is enough lol
                return json.loads(str(await r.text()))['response']['user']['type']
             except Exception:
                return json.loads(str(await r.text()))['response']['team']['type']

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

class ResourceProvider:
    hasPolymart = None
    hasSpigot = None
    polymartResourceID = None
    polymartKeyOverride = None
    spigotResourceID = None

def parsePlaceholder(ctx, string):
    return string.replace("%version%", bot_version).replace("%branch%", bot_branch).replace("%date%", str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M"))).replace("%user_name%", str(ctx.author.name)).replace("%user_discriminator%", str(ctx.author.discriminator)).replace("%user_full%", str(ctx.author.name) + "#" + str(ctx.author.discriminator)).replace("%invis%", "᲼").replace("%22invis%", "᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼")

print("PolymartBase " + str(bot_version))
print("Licensed under the permissive MIT license")
bot = interactions.Client(token=configData['bot-token'])
if configData['activity'] is not None:
    bot = interactions.Client(token=configData['bot-token'], presence=interactions.ClientPresence(activities=[interactions.PresenceActivity(name=configData['activity'], type=interactions.PresenceActivityType.GAME)]))

# Commands

@bot.command(
    name="verify",
    description="Verify ownership of plugins",
    scope=configData['server-id']
)
async def verify(ctx: interactions.CommandContext):
   channel_id = ctx.channel.id
   if configData['channel-id'] is not None:
       if configData['channel-id'] != channel_id:
           errEmbed = interactions.Embed(description=configData['indicator']['x'] + " Sorry, you cannot use this command in this channel!")
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
        custom_id="verify_c"
   )
   row = interactions.ActionRow(
    components=[getTokenButton, verifyButton]
   )
   infoEmbed = interactions.Embed(title="Hi there!", description="Hi there " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "! This form is here to help you get started! \n\nTo get started, click the **Get Token** button and it will automatically open a link. \nLogin into your Polymart account and it will generate a token. \nCopy that token and click the **Verify** button, enter your token and let the bot handle the rest! \n\nIf you have bought a plugin after verification and would like to get verified for that plugin, just do verify again!", color=0x33a343)
   infoEmbed.set_footer(text=parsePlaceholder(ctx, configData['layout']['footer']))
   await ctx.send(embeds=infoEmbed, components=row, ephemeral=True)

@bot.component("verify_c")
async def verify_component(ctx):
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
    await ctx.defer()
    resourceList = await getAllResources()
    member = ctx.member
    user_id = await PolymartAPI.verifyUser(response)
    user_data = await PolymartAPI.getUserData(configData['providers']['polymart']['global-api-key'], user_id)
    user_name = user_data['response']['user']['username']
    base_first = "Username: " + user_name + "\nUser ID: " + user_id + "\n\nStatus:"
    base_final = "\n\nVerified Successfully!"
    final_text = ""
    embed = interactions.Embed(title=parsePlaceholder(ctx, configData['layout']['title']), color=0x33a343)
    embed.set_footer(text=parsePlaceholder(ctx, configData['layout']['footer']))
    for r in resourceList:
        ownershipStatus = await checkAndVerify(ctx, specificKey, resourceList[r].getResourceID(), response, resourceList[r].getResourceRoleID(), user_data, user_id)
        if configData['layout']['mode'] == "new" and ownershipStatus:
            final_text += resourceList[r].getResourceIcon() + " " + resourceList[r].getResourceName() + "\n"
        elif configData['layout']['mode'] == "default":
            final_text += "\n" + resourceList[r].getResourceIcon() + " **" + resourceList[r].getResourceName() + "**: " + str(ownershipStatus)
    if configData['layout']['mode'] == "new":
        embed.add_field(name="**User Name**", value=user_name, inline=True)
        embed.add_field(name="**User ID**", value=str(user_id), inline=True)
        embed.add_field(name="**Date**", value=str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M")), inline=True)
        embed.add_field(name="**Owned**", value=final_text)
        embed.add_field(name="Verified Successfully!", value="")
        embed.description = "**• Discord**: " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + "\n**• Account Type**: " + str(await PolymartAPI.getAccountType(user_id)).replace("user", "User").replace("team", "Team")
    elif configData['layout']['mode'] == "default":
        text = base_first + final_text + base_final
        embed.description = text.replace("False", configData['indicator']['x']).replace("True", configData['indicator']['check_mark']).replace("None", "")
    await ctx.send(embeds=embed)
    
async def checkAndVerify(context, api_key, resource_id, user_token, verified_role_id, user_data, user_id):
    resource_user_data = await PolymartAPI.getResourceUserData(api_key, resource_id, user_id)
    if context.author.roles and verified_role_id not in context.author.roles or not context.author.roles:
        if resource_user_data['response']['resource']['purchaseValid']:
            await context.author.add_role(verified_role_id, configData['server-id'])
            return True
        else:
            return False
    elif context.author.roles and verified_role_id in context.author.roles:
        return True

async def getAllResources():
    resourceList = {}
    for r in resourceData:
        resource = resourceData[r]
        resourceList[r] = Resource(resource['resource-name'], resource['resource-id'], resource['role-id'], resource['icon'], resource['api-key'])
    return resourceList
            
bot.start()