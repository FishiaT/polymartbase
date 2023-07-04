# polymartbase
 Self-hosted and easily configurable Discord bot for verifying Polymart plugin ownership.

## Installation
 Clone this repository (you can also just download the ZIP):
 ```
 git clone https://github.com/ClickNinYT/polemartbase && cd polymartbase
 ```

 Install required dependencies:
 ```
 python3 -m pip install -r requirements.txt
 ```

## Creating the bot
 Head to [Discord Developer Portal](https://discord.com/developers/applications), login to your Discord account if asked, and create a new Application.

 After that, head to the Bot setting and enable all 3 Privileged Gateway Intents.

 ![img1](https://user-images.githubusercontent.com/74685931/250798340-e02d37a0-945e-48fc-9f0c-471c08c2fc55.png)

 In the Bot Permissions section, just enable the "Administrator" permission.

 Now head to the OAuth2 setting and select URL Generator, in the Scopes section enable the "bot" and "applications.commandss" scope.

![img2](https://user-images.githubusercontent.com/74685931/250799394-0728b56d-d970-469f-a8ad-c4020e528197.png)

  Scroll down and enable the Administrator permission again in the Bot Permissions section.

  After that, an URL should be generated which can be used to invite the bot to your server.

## Setting up the bot
 Go back to the Bot settings, and click Reset Token. A new token will be generated. Now open the "config.yml" file, and replace `DISCORD_BOT_TOKEN` with your token.

 Now changes all settings in both `config.yml` and `resources.yml` accordingly.

 After that, run the bot:
 ```
 python3 base.py
 ```

 If configured properly, the bot should be online and ready to use!

## License
 This project is licensed under the [MIT license](https://www.tldrlegal.com/license/mit-license).
 
 tl;dr: do whatever you want with this bot (even selling it), just credit me properly and retain the license.
