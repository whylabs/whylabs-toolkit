# WhyLabs Toolkit

The WhyLabs Toolkit package contains helper methods to help users interact with our internal APIs. Users will benefit from using it if they want to abstract some of WhyLabs' internal logic and also automate recurring API calls.


## Basic usage
To start using the `whylabs_toolkit` package, install it from PyPI with:
```bash
pip install whylabs_toolkit
``` 

## Packages

The available packages that we have enable different use-cases for the `whylabs_toolkit`. To get started, navigate to one of the following sections and find useful tutorials there.

| Package             | Usage                |
|---------------------|----------------------|
| [Monitor Manager](https://github.com/whylabs/whylabs-toolkit/blob/mainline/whylabs_toolkit/monitor/manager/README.md) | Author and modify existing WhyLabs monitor with Python |
| [WhyLabs Helpers](https://github.com/whylabs/whylabs-toolkit/blob/mainline/whylabs_toolkit/helpers/README.md) | Interact with and modify your Datasets and ML Models specs in WhyLabs. |

## Development

To start contributing, you will manage dependencies with [Poetry](https://python-poetry.org/) and also a handful of `Makefile` commands. To install all necessary dependencies and activate the virtual environment, run:

```bash
make setup && poetry shell
```

## Get in touch
If you want to learn more how you can benefit from this package or if there is anything missing, please [contact our support](https://whylabs.ai/contact-us), we'll be more than happy to help you!