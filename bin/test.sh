BASEDIR=$(dirname $0)
cd ${BASEDIR} || exit 1
# Prefer a venv's own python/pytest if one sits alongside the repo
# (../.venv, matching what ci.yml's "Set up venv" step creates) - falls
# back to whatever "python" is already on PATH otherwise (e.g. when called
# after activating .venv-vallenato_fr by hand, as the local dev docs
# describe).
if [ -x "../.venv/bin/python" ]; then
    PYTHON="../.venv/bin/python"
else
    PYTHON="python"
fi
rm -rf ../html_dev/coverage && ${PYTHON} -m pytest \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html:../html_dev/coverage \
    --cov-report=xml:coverage.xml \
    --cov-config=.coveragerc \
    --cov-fail-under=100 \
    --junitxml=test-results.xml
