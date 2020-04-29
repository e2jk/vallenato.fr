Virtual environment setup
=========================

Create the environment:
-----------------------
```bash
$ mkdir -p ~/.python-virtual-environment/vallenato_fr
$ python3 -m venv ~/.python-virtual-environment/vallenato_fr
$ pip3 install -r requirements.txt
```

Activate the virtual environment:
---------------------------------
`$ source ~/.python-virtual-environment/vallenato_fr/bin/activate`

When done:
----------
`$ deactivate`

Update the dependencies:
------------------------
`$ pip3 install -r requirements.txt`

First time creation/update of the dependencies:
-----------------------------------------------
`$ pip3 freeze > requirements.txt`
