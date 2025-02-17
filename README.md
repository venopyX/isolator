# Isolator Run

A secure application isolation tool for Linux using bubblewrap. Run applications in isolated environments with enhanced security and data protection.

## Features

- 🔒 Secure application isolation using bubblewrap
- 🖥️ Full GUI application support (X11)
- 📁 Temporary filesystem isolation
- 🛡️ Configurable security levels
- 🔧 Flexible configuration options
- 📊 Comprehensive logging

## Requirements

- Python 3.8 or higher
- Linux operating system
- bubblewrap package installed

## Installation

### From PyPI

```bash
pip install isolator
```

### From Source

```bash
git clone https://github.com/scorpidev/isolator.git
cd isolator
pip install -e .
```

## Usage

### Basic Usage

Run any application in an isolated environment:

```bash
isolator google-chrome  # Run Chrome in isolation
isolator mousepad      # Run text editor in isolation
```

### Advanced Options

```bash
# Run with debug logging
isolator --debug firefox

# Run with persistent storage
isolator --persist /path/to/storage firefox

# Run with network isolation
isolator --no-network firefox

# Run with strict isolation
isolator --isolation-level strict firefox
```

### Configuration

The tool supports various isolation levels and profiles:

- **Isolation Levels**:
  - `minimal`: Basic isolation
  - `standard`: Default level with GUI support
  - `strict`: Maximum isolation

- **Application Profiles**:
  - `BASIC`: Standard applications
  - `BROWSER`: Web browsers
  - `MULTIMEDIA`: Media applications
  - `DEVELOPMENT`: Development tools
  - `GRAPHICS`: Graphics applications

## Security Features

- Read-only system file access
- Temporary writable storage
- Process isolation
- Optional network isolation
- Configurable device access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
