BASEDIR=$(dirname $0)
cd ${BASEDIR} || exit 1
# Prefer a venv's own python/pytest if one sits alongside the repo
# (../.venv, matching what ci.yml's "Set up venv" step creates, or
# ../.venv-vallenato_fr, matching bin/README_VIRTUAL_ENVIRONMENT.md's local
# dev setup) - falls back to whatever "python" is already on PATH otherwise
# (e.g. when called after activating one of those venvs by hand). Callers
# (e.g. .githooks/pre-push) may pre-set PYTHON to pin an exact interpreter.
if [ -z "${PYTHON:-}" ]; then
    if [ -x "../.venv/bin/python" ]; then
        PYTHON="../.venv/bin/python"
    elif [ -x "../.venv-vallenato_fr/bin/python" ]; then
        PYTHON="../.venv-vallenato_fr/bin/python"
    else
        PYTHON="python"
    fi
fi
rm -rf ../html_dev/coverage && ${PYTHON} -m pytest \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html:../html_dev/coverage \
    --cov-report=xml:coverage.xml \
    --cov-config=.coveragerc \
    --cov-fail-under=100 \
    --junitxml=test-results.xml
