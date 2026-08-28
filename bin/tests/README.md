El Vallenatero Francés
======================

How to run the test suite:
--------------------------

Run the `./bin/test.sh` file.

How to run the test suite (and everything else CI checks) before each `git push`
----------------------------------------------------------------------------------

Install the repo's pre-push hook once per clone:

```shell
git config core.hooksPath .githooks
```

See [`.githooks/pre-push`](../../.githooks/pre-push) for what it runs (ruff,
mypy, bandit, zizmor, actionlint, pip-audit, and this test suite with its
100% coverage gate).
