# isolator Development Guide

Welcome to the development guide for `isolator`. This document provides an overview of the package structure, configuration files, development tools, and instructions for building and publishing the package.

## Package Structure

The package is structured as follows:

```
isolator/
├── isolator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── enums.py
│   ├── isolator.py
│   ├── logging_config.py
│   └── managers/
│       ├── __init__.py
│       ├── display_manager.py
│       ├── filesystem_manager.py
│       ├── requirements_manager.py
│       └── security_manager.py
├── LICENSE
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── requirements.txt
├── setup.cfg
└── setup.py
```

## Configuration Files

- **setup.py**: Main package configuration.
- **setup.cfg**: Package metadata and build settings.
- **pyproject.toml**: Build system requirements.
- **MANIFEST.in**: Additional file inclusions.
- **requirements.txt**: Development dependencies.

## Package Information

- **Name**: isolator
- **Version**: 0.1.0
- **Python Requirement**: >=3.8
- **License**: MIT

## Development Tools

The following tools are used for development:

- **Code Formatting**: `black`, `isort`
- **Linting**: `flake8`
- **Type Checking**: `mypy`
- **Testing**: `pytest`, `pytest-cov`
- **Build Tools**: `build`, `twine`

## Building and Publishing the Package

To build and publish the package, follow these steps:

1. **Build the Package**:
   ```bash
   python -m build
   ```

2. **Check the Distribution**:
   ```bash
   twine check dist/*
   ```

3. **Upload to TestPyPI (for testing)**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI (when ready)**:
   ```bash
   twine upload dist/*
   ```

## Installing the Package

Users can install the package using:

```bash
pip install isolator
```

## Features

- **Command-line Interface**: Accessible via the `isolator` command.
- **Full Documentation**: Available in `README.md`.
- **Proper Dependency Management**: Ensures all dependencies are managed correctly.
- **Development Tools Configuration**: Includes settings for code formatting, linting, type checking, and testing.

## Contributing

To contribute to `isolator`, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your branch to your fork.
5. Create a pull request to the main repository.

Thank you for contributing to `isolator`!