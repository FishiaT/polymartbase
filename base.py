# PolymartBase

from ruamel import yaml
from pathlib import Path
import httpx
import json
import interactions
import datetime

bot_version = "4.0.1"

config_data = yaml.YAML(typ='safe').load(Path('config.yml'))
resource_data = yaml.YAML(typ='safe').load(Path('resources.yml'))

resources = {}

bot = interactions.Client(intents=interactions.Intents.DEFAULT)

class Resource:
    name = None
    id = None
    role_id = None
    icon = None
    api_key = None
    def __init__(self, name, id, role_id, icon, api_key):
        self.name = name
        self.id = id
        self.role_id = role_id
        self.icon = icon
        self.specific_key = api_key
        
class PolymartAPI:
   def generate_verify_url():
       url = config_data['base_url'] + "/v1/generateUserVerifyURL"
       arg = {'service':config_data['service']}
       resp = json.loads(str(httpx.get(url, params=arg).text))
       return resp
   def verify_user(token):
       url = config_data['base_url'] + "/v1/verifyUser"
       arg = {'service':config_data['service'],'token':token}
       resp = json.loads(str(httpx.get(url, params=arg).text))
       return resp
   def get_user_data(api_key, user_id):
       url = config_data['base_url'] + "/v1/getUserData"
       arg = {'api_key':api_key,'user_id':user_id}
       resp = json.loads(str(httpx.post(url, json=arg).text))
       return resp
   def get_resource_user_data(api_key, resource_id, user_id):
       url = config_data['base_url'] + "/v1/getResourceUserData"
       arg = {'api_key':api_key,'resource_id':resource_id,'user_id':user_id}
       resp = json.loads(str(httpx.post(url, json=arg).text))
       return resp
                
@interactions.listen()
async def on_ready():
    if config_data['activity'] is not None:
        await bot.change_presence(status=interactions.Status.ONLINE, activity=interactions.Activity(name=config_data['activity']))
    if config_data['disable_failsafe']:
        print("WARNING: BUILT-IN FAILSAFE HAS BEEN DISABLED! IT IS RECOMMENDED TO ENABLE THIS.")
    print("PolymartBase " + bot_version)
    print("The bot is now ready!")
    
async def api_failsafe(ctx, json_data, err_type, resource=None):
    if json_data['response']['success'] == True or config_data['disable_failsafe']:
        return True
    error_embed = interactions.Embed()
    error_embed.color = "#" + config_data['layout']['error_color']
    error_embed.footer = "Bot version " + bot_version
    match err_type:
        case "verify_url":
            error_embed.description = config_data['indicator']['x'] + " Failed to generate the verification URL!"
            await ctx.send(embeds=error_embed, ephemeral=True)
            return False
        case "invalid_token":
            error_embed.description = config_data['indicator']['x'] + " Invalid verification key!"
            await ctx.send(embeds=error_embed, ephemeral=True)
            return False
        case "user_data":
            error_embed.description = config_data['indicator']['x'] + " Failed to get user information!"
            await ctx.send(embeds=error_embed, ephemeral=True)
            return False
        case "res_user_data":
            error_embed.description = config_data['indicator']['x'] + " Failed to get user resource ownership information for " + str(resource.name) + "!"
            await ctx.send(embeds=error_embed, ephemeral=True)
            return False
    
#@interactions.listen(disable_default_listeners=True)
#async def on_command_error(event: interactions.api.events.Error):
#    await event.ctx.send("Something has went wrong, please try again.", ephemeral=True)
               
@interactions.slash_command(name="verify", description="Verify plugins ownership.")
async def verify(ctx: interactions.SlashContext):
    #if ctx.author.id != 713566850650341437:
    #    await ctx.send("Hey there! The bot is currently in a rewrite. As such, the bot is not available to use at the moment. Please use tickets to verify yourself for the time being. Sorry for the inconvenience.", ephemeral=True)
    #    return
    if config_data['channel_id'] is not None and ctx.channel.id not in config_data['channel_id']:
        error_embed = interactions.Embed(description=config_data['indicator']['x'] + " Sorry, you can\'t use this command here!")
        await ctx.send(embeds=error_embed, ephemeral=True)
        return
    url = PolymartAPI.generate_verify_url()
    if not await api_failsafe(ctx, url, "verify_url"):
        return
    inst_buttons: list[interactions.ActionRow] = [
        interactions.ActionRow(
            interactions.Button(
                style=interactions.ButtonStyle.URL,
                label="Get Key",
                url=url['response']['result']['url'],
            ),
            interactions.Button(
                custom_id="verify_btn",
                style=interactions.ButtonStyle.GREEN,
                label="Verify",
            )
        )
    ]
    instruction_embed = interactions.Embed(title="Just a few more steps...", description="To verify yourself, follow the following steps:\n\n1. Click \"Get Key\", login into your Polymart account if asked, and copy the generated key.\n\n2. Click \"Verify\", then paste the copied key into the text box and click \"Submit\".\n\nThe bot will finish the job automatically after that.", footer="Bot version " + bot_version)
    await ctx.send(embeds=instruction_embed, components=inst_buttons, ephemeral=True)
    
@interactions.listen()
async def on_component(event: interactions.api.events.Component):
    ctx = event.ctx
    match ctx.custom_id:
        case "verify_btn":
            token_input = interactions.Modal(
                interactions.ShortText(
                    label="Polymart Verification Key",
                    custom_id="token",
                    required=True,
                    placeholder="XXX-XXX-XXX",
                    min_length=11,
                    max_length=11,
                ),
                title="Enter your verification key.",
            )
            await ctx.send_modal(modal=token_input)
            modal_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(token_input)
            verify_resp = PolymartAPI.verify_user(modal_ctx.responses['token'])
            if not await api_failsafe(modal_ctx, verify_resp, "invalid_token"):
                return
            user_id = verify_resp['response']['result']['user']['id']
            user_data_resp = PolymartAPI.get_user_data(config_data['global_api_key'], user_id)
            if not await api_failsafe(modal_ctx, user_data_resp, "user_data"):
                return
            user_name = user_data_resp['response']['user']['username']
            await modal_ctx.defer()
            summary_embed = interactions.Embed(title="Success", color="#" + config_data['layout']['summary_color'], footer="Bot version " + bot_version, description="**• Discord**: " + str(ctx.author.display_name) + "#" + str(ctx.author.discriminator) + "\n**• Date**: " + str(datetime.datetime.now().strftime("%m/%d/%Y")))
            summary_embed.add_field(name="**User Name**", value=user_name, inline=True)
            summary_embed.add_field(name="**User ID**", value=str(user_id), inline=True)
            owned_resources_text = ""
            owned_res = 0
            total_res = len(resources)
            for res in resources:
                api_key = None
                if resources[res].api_key is not None:
                    api_key = resources[res].api_key
                else:
                    api_key = config_data['global_api_key']
                resource_user_data = PolymartAPI.get_resource_user_data(api_key, resources[res].id, user_id)
                if not await api_failsafe(ctx, resource_user_data, "res_user_data", resources[res]):
                    return
                if await verify_ownership(modal_ctx, resources[res], resource_user_data, user_id):
                    purchase_time = datetime.datetime.fromtimestamp(int(resource_user_data['response']['resource']['purchaseTime'])).strftime("%m/%d/%Y")
                    owned_resources_text += resources[res].icon + " " + resources[res].name + " (" + str(purchase_time) + ")\n" 
                    owned_res += 1
            if owned_res == 0:
                owned_resources_text = "Nothing :(\n"
            owned_resources_text += "\n**Verified Successfully!**"
            summary_embed.add_field(name="**Owned (" + str(owned_res) + "/" + str(total_res) + ")**", value=owned_resources_text)
            await modal_ctx.send(embeds=summary_embed)

async def verify_ownership(ctx, resource, resource_user_data, user_id):
    if ctx.author.roles and resource.role_id in ctx.author.roles:
        return True
    elif ctx.author.roles and resource.role_id not in ctx.author.roles or not ctx.author.roles:
        if resource_user_data['response']['resource']['purchaseValid']:
            await ctx.author.add_role(resource.role_id)
            return True
        else:
            return False

def fetch_resources():
    for res in resource_data:
        resource = resource_data[res]
        resource_conf = Resource(resource['resource_name'], resource['resource_id'], resource['role_id'], resource['icon'], resource['api_key'])
        resources[res] = resource_conf

fetch_resources()
bot.start(config_data['bot_token'])
