# MIT License

# Polymart Verification Bot Base
# Version 3.0.0 (oss/main)

# The base to make your own Polymart verification discord Bot
# Warning: I wrote this in 1 day, code is very bad, but it works lol

# Requires aiohttp & discord-py-interactions, install them with pip3

import aiohttp
import random
import json
import interactions
import os
import datetime

# bot version
# dont change this unless PR
# major.minor.patch
bot_version = "3.0.0"

# <closed/oss> / <git branch>
# dont change this unless you make a closed fork or change git branch
bot_branch = "oss/main"

# Your discord bot token
# The bot must have the bot and application.commands permission
token = "Replace_This_With_The_Token"

# Don't change this 
base_url = "https://api.polymart.org"

# Your "service", can be basically anything
service = "BaseVerification"

# Your discord server ID
server_id =

# plugin_name_verified_role: the ID of the role that the bot will give after verify (one per plugin)
plugin_name_verified_role =

# plugin_name_resource_id: polymart resource ID for the plugin that you want to verify (one per plugin)
plugin_name_resource_id =

# your Polymart api key, must have the List Buyer permission
api_key = "Replace_This_With_The_Api_Key"

# to verify ownership for a plugin, you can use checkAndVerify, for the user_token arg just type "token" here (without the quotes ofc), for other info it depends on your plugin and your server, make sure to use the correct api key for the plugin (the api key need to be from the one who sell the plugin)
# checkAndVerify returns a boolean based on if the verification is success or not, aka it return True (captial T matters) if the user bought the plugin and False (again, F matters) if the user not or verify failed fsr, how you want to store it is your choice (i suggest put it in the text itself)
# modify the text string to change the verification summary

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

print("This bot is licensed under MIT license")
print("Bot Token: " + token)
bot = interactions.Client(token=token, presence=interactions.ClientPresence(activities=[interactions.PresenceActivity(name="/verify", type=interactions.PresenceActivityType.GAME)]))

# Commands

@bot.command(
    name="verify",
    description="Verify ownership of plugins",
    scope=server_id
)
async def verify(ctx: interactions.CommandContext):
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
    user_name, user_id = await getUser(token, api_key)
    text = "Username: " + user_name + "\nUser ID: " + user_id + "\n\nStatus: \n" + "\n\nVerification Successfully!"
    text2 = text.replace("False", ":x:")
    text3 = text2.replace("True", ":white_check_mark:")
    embed = interactions.Embed(title="Verification Summary for User " + str(ctx.author), description=text3, color=0x33a343)
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
            
bot.start()
