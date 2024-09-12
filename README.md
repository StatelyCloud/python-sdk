# Python SDK

This folder contains the Stately Cloud Python SDK

## Running tests locally
- `just test-python` runs the unit tests
- `just integ-python` runs the python integ tests against a local backend

## Running tests against a live backend
- Get the `TEST_API_RUNNER` key for your chosen environment from Bitwarden and set it in your shell env:
  - `export TEST_RUNNER_API_KEY='xxxyyyzzz'`
- Run `just integ-python {dev|prod}`


## Other handy commands
- `just build-python` builds the distributable package in ./dist
- `just lint-python` runs the linter
- `just fix-python` fixes any automatically fixable linting issues
