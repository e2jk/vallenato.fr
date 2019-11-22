El Vallenatero Francés
======================

How to run the test suite:
--------------------------

Run the `./bin/test.sh` file.

How to run the test suite before each `git commit`
--------------------------------------------------

Add the following to your `.git/hooks/pre-commit` file:

```shell
#!/bin/sh

# Run the Unit Tests suite
./bin/test.sh
```
