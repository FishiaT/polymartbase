# polymartbase
 Self hosted configurable Discord bot for verifying Polymart plugins ownership.

## Initial setup
 NOTE: This is mainly targeted at Windows and GNU/Linux systems, as these are the only platforms tested. However, since this is written in Python, it should work on every platform that support Python.

 First, install Python 3.8 or newer. See your platform's documentation for how.

 Then, run `pip install aiohttp git+https://github.com/interactions-py/library.git@unstable ruamel.yaml` to install the needed dependencies. 

 Now clone this repository, edit `config.yml` and `resources.yml` (every config options is documented), then run the bot by running `python3 base.py`. If configured properly, the bot should go online. Now anyone can run `/verify` and follow the instructions to verify themselves!

## License
 This project is licensed under the permissive MIT license.
 
 tl/dr: do whatever you want with this bot, including selling it, I don't care. But you must credit me. I'm not liable for anything that you have done.
