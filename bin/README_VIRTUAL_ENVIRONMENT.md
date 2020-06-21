Virtual environment setup
=========================

Create the environment:
-----------------------
```bash
$ cd devel/vallenato.fr/
$ mkdir -p .venv-vallenato_fr
$ python3 -m venv .venv-vallenato_fr
$ source .venv-vallenato_fr/bin/activate
$ cd bin/
$ pip3 install wheel
$ pip3 install -r requirements.txt
```

Activate the virtual environment:
---------------------------------
`$ source ~/devel/vallenato.fr/.venv-vallenato_fr/bin/activate`

When done:
----------
`$ deactivate`

Update the dependencies:
------------------------
`$ pip3 install -r requirements.txt`

First time creation/update of the dependencies:
-----------------------------------------------
`$ pip3 freeze > requirements.txt`
