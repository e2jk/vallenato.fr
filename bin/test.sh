BASEDIR=$(dirname $0)
cd ${BASEDIR} && rm -rf ../html_dev/coverage && python -m pytest \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html:../html_dev/coverage \
    --cov-report=xml:coverage.xml \
    --cov-config=.coveragerc \
    --cov-fail-under=100 \
    --junitxml=test-results.xml
