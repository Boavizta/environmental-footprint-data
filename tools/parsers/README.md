# Parsers

This folder contains the parsing modules for each different providers.

Each parser takes a file as input (usually a PDF) and returns a `DeviceCarbonFootprint` object.

Keep each parser in a distinct module (file), and move common code to the `lib` folder.

## Development

When working on a parser, download the corresponding file locally then run:

```sh
python -m parsers.dell_laptop carbon-footprint-wyse-3030.pdf
```

You might need to install some libraries.

```sh
pip install -r requirements.txt
apt install tesseract-ocr
```

## Typing

To check that everything is typed properly, install the test requirements.

```sh
pip install -r requirements-testing.txt
```

Then you can run:

```sh
mypy --strict --ignore-missing-imports parsers tests
```

## Testing

See [tests folder](../tests).
