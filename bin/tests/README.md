El Vallenatero Francés
======================

How to run the test suite:
--------------------------

Run the following in the `bin` folder:
`coverage run --include=./*.py --omit=tests/* -m unittest discover && rm -rf ../html_dev/coverage && coverage html --directory=../html_dev/coverage --title="Code test coverage for vallenato.fr"`
