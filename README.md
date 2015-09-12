# Automatic roster downloading

A script to automatically download rosters from
https://my.cs.illinois.edu/classtools.  Super hacky, so don't judge plz.

## Installation

### On EWS

You have two options. You can either use 233's pyenv installation and
then use the virtualenv method (below), or use EWS's Python 3 module
(the Python 2.7 module has a broken pip, and Python 3 is superior
anyway):

```sh
module load python3
pip3 install --user -r requirements.txt
```

You'll have to repeat the

```sh
module load python3
```

every new shell session, or just add it to your `~/.bashrc` (or the
configuration file of whatever shell you use).

### Using virtualenv

If you're familiar with virtualenv, you can use it to set up an isolated
environment for the script:

```sh
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

And then activate the virtual environment whenever you want to use the
script:

```sh
source venv/bin/activate
```

And deactivate it when you're done:

```sh
deactivate
```

If you're not familiar with virtualenv, it might be worth learning;
GIYF.

### Using a regular pip install

Just do

```sh
pip3 install -r requirements.txt
```

and you should be good to go. You may want to use the `--user` option
for `pip3 install` if you don't want to add to the global packages (or
if you don't have the access rights to do so). 

## Usage

Refer to

```sh
./download_roster.py -h
```

## Help

Feel free to shoot me an email at meenai1@illinois.edu or file an issue.
Pull requests to make this not horribly hacky/fragile are also welcome.
