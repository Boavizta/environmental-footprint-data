# Tests

To run the tests install testing dependencies:

```sh
pip install -r requirements-testing.txt
```

then run

```sh
python -m unittest discover -s tools/tests
```

## New parser tests

To add new tests file, add the input file in the `testdata` folder under the name of the
corresponding parser.

Add a JSON file next to it with the parsed expectations.
