# polymartbase
 Self hosted configurable Discord bot for verifying Polymart plugins ownership.

## Initial setup
 First, install Python 3.8 or newer. 
 * For Windows, download the latest installer from [here](https://www.python.org/).
 * For GNU/Linux, depending on your distribution, it may already have Python installed (check it by running `python3`). If not, install it using distribution's package manager (for Ubuntu, running `sudo apt install python3 python-pip` will install everything you need).
 * For other platforms, see the platform's guide.

 Then, run `pip install aiohttp git+https://github.com/interactions-py/library.git@unstable ruamel.yaml` to install the needed dependencies. Note, you need to use the unstable version of interactions.py in order for all functions of the bot to work properly.

 Now clone this repository, edit the `config.yml` file and `resources.yml` file, then run the bot by `python3 base.py`. If configured properly, the bot should be working.

 Since this bot is self hosted, you need to host it yourself. An old computer from 1998 running 24/7 should be enough.

## License
 This project is licensed under the permissive MIT license.
 
 tl/dr: do whatever you want with this bot, I don't care. But you may not hold me liable for what you did.
