# polymartbase
 A base Python discord bot for Polymart plugin verification

## Initial setup
 NOTE: This is mainly targeted at Windows and GNU/Linux systems, as these are the only platforms tested. However, since this is written in Python, it should work on every platform that support Python.

 First, install Python 3.8 or newer. 
 * For Windows, download the latest installer from [here](https://www.python.org/).
 * For GNU/Linux, depending on your distribution, it may already have Python installed (check it by running `python3`). If not, install it using distribution's package manager (for Ubuntu, running `sudo apt install python3 python-pip` will install everything you need).

 Then, run `pip install aiohttp discord-py-interactions ruamel.yaml` to install the needed dependencies.

 Now clone this repository, edit the `config.yml` file and `resources.yml` file, then run the bot by `python3 base.py`. If no tracebacks occurs, then the bot should be online now.

## License
 This project is licensed under the MIT license.
 
 tl/dr: use it, change it, modify it, do whatever you want with this, except you may not hold any developer liable for what you do.
