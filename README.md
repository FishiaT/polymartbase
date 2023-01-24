# polymartbase
 Self hosted configurable Discord bot for verifying Polymart plugins ownership.

 3.2.0 contains some changes to the config file (mainly rename of the options), as such you need to adapt your existing config to 3.2.0 manually, but it should be very straightforward.

## Initial setup
 NOTE: This is mainly targeted at Windows and GNU/Linux systems, as these are the only platforms tested. However, since this is written in Python, it should work on every platform that support Python.

 First, install Python 3.8 or newer. 
 * For Windows, download the latest installer from [here](https://www.python.org/).
 * For GNU/Linux, depending on your distribution, it may already have Python installed (check it by running `python3`). If not, install it using distribution's package manager (for Ubuntu, running `sudo apt install python3 python-pip` will install everything you need).

 Then, run `pip install aiohttp git+https://github.com/interactions-py/library.git@unstable ruamel.yaml` to install the needed dependencies. Note, you need to use the unstable version of interactions.py in order for all functions of the bot to work properly.

 Now clone this repository, edit the `config.yml` file and `resources.yml` file, then run the bot by `python3 base.py`. If configured properly, the bot should be working.

## License
 This project is licensed under the permissive MIT license.
 
 tl/dr: do whatever you want with this bot, I don't care. But you may not hold me liable for what you did.
