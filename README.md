# Isolator

[![PyPI version](https://badge.fury.io/py/isolator.svg)](https://badge.fury.io/py/isolator)
[![Python](https://img.shields.io/pypi/pyversions/isolator.svg)](https://pypi.org/project/isolator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible application isolation tool for Linux that uses bubblewrap to create secure, isolated environments for running applications. Isolator provides enhanced security features, GUI application support, and configurable isolation levels.

## Features

- 🔒 Secure application isolation using bubblewrap
- 🖥️ Full GUI application support (X11 and Wayland)
- 📁 Configurable filesystem isolation
- 🛡️ Multiple security levels
- 🎮 Application-specific profiles
- 📊 Detailed logging and debugging options

## Requirements

- Python 3.8 or higher
- Linux operating system
- bubblewrap package installed (`sudo apt install bubblewrap` OR `sudo apt install bwrap` on Debian/Ubuntu)

## Installation

### From PyPI

```bash
pip install isolator
```

### From Source

```bash
git clone https://github.com/venopyx/isolator.git
cd isolator
pip install -e .
```

> NOTE: If you're using Kali Linux, consider using `pipx` inplace of `pip`.


## Basic Usage

### Simple Application Launch

Run any application in an isolated environment:

```bash
# Run Firefox in isolation
isolator firefox

# Run VS Code in isolation
isolator code

# Run VLC media player in isolation
isolator vlc
```

### Command Arguments

You can pass arguments to the isolated application:

```bash
# Open a specific URL in Firefox
isolator firefox https://github.com

# Open a file in VS Code
isolator code myproject/

# Play a specific file in VLC
isolator vlc myvideo.mp4
```

## Advanced Options

### Isolation Levels

```bash
# Run with minimal isolation
isolator --isolation-level minimal firefox

# Run with standard isolation (default)
isolator --isolation-level standard firefox

# Run with strict isolation
isolator --isolation-level strict firefox
```

Each isolation level provides different security features:
- `minimal`: Basic process and filesystem isolation
- `standard`: Adds display server isolation and basic security features
- `strict`: Maximum isolation including network restrictions

<!-- > #### Strict Isolation Note
> When using `--isolation-level strict` with GUI applications, ensure your X11/Wayland server is configured to allow connections from isolated environments. This may require setting up X authority permissions or adjusting Wayland socket access. -->

### Application Profiles

```bash
# Explicitly set browser profile
isolator --profile BROWSER chrome

# Use multimedia profile for media applications
isolator --profile MULTIMEDIA vlc

# Development profile for IDEs and tools
isolator --profile DEVELOPMENT code
```

Available profiles:
- `BASIC`: Default profile for general applications
- `BROWSER`: Optimized for web browsers
- `MULTIMEDIA`: Configured for media applications
- `DEVELOPMENT`: Tailored for development tools
- `GRAPHICS`: Optimized for graphics applications

### Persistent Storage

```bash
# Run with persistent storage
isolator --persist ~/my-isolated-data firefox

# Run with persistent storage and strict isolation
isolator --persist ~/my-isolated-data --isolation-level strict firefox
```

### Network Control

```bash
# Run without network access
isolator --no-network firefox

# Run with network access (default)
isolator firefox
```

### GUI Support

```bash
# Run without GUI support
isolator --no-gui application

# Run with GUI support (default)
isolator application
```

### Debug Logging

```bash
# Enable debug logging
isolator --debug firefox
```

## Environment Variables

Isolator respects and manages various environment variables:

```bash
# Set custom temporary directory
export ISOLATOR_TMP_DIR=/path/to/tmp
isolator firefox

# Set custom XDG runtime directory
export XDG_RUNTIME_DIR=/run/user/1000
isolator firefox
```

## Security Considerations

Isolator provides several security features:

1. **Filesystem Isolation**:
   - Read-only system directories
   - Isolated home directory
   - Temporary writable storage

2. **Process Isolation**:
   - Separate PID namespace
   - IPC isolation
   - User namespace isolation (in strict mode)

3. **Network Isolation**:
   - Optional network access
   - Configurable network restrictions

4. **Display Server Isolation**:
   - Secure X11/Wayland access
   - Protected cookie handling

## Examples

### Web Browser Isolation

```bash
# Run Chrome with persistent profile
isolator --persist ~/.chrome-isolated \
         --profile BROWSER \
         google-chrome

# Run Firefox in strict mode
isolator --isolation-level strict \
         --profile BROWSER \
         firefox
```

### Development Environment

```bash
# Run VS Code with custom storage
isolator --persist ~/.vscode-isolated \
         --profile DEVELOPMENT \
         code myproject/

# Run PyCharm with debug logging
isolator --debug \
         --profile DEVELOPMENT \
         --persist ~/.pycharm-isolated \
         pycharm
```

### Multimedia Applications

```bash
# Run VLC with multimedia profile
isolator --profile MULTIMEDIA \
         --persist ~/.vlc-isolated \
         vlc

# Run OBS Studio with network access
isolator --profile MULTIMEDIA \
         --persist ~/.obs-isolated \
         obs
```

## Configuration File

Isolator supports configuration files for persistent settings:

```ini
# ~/.config/isolator/config.ini
[default]
isolation_level = standard
persist_dir = ~/.isolated-data
network_enabled = true
gui_enabled = true
debug = false

[browser]
profile = browser
persist_dir = ~/.browser-isolated

[development]
profile = development
persist_dir = ~/.dev-isolated
```

## Troubleshooting

### Common Issues

1. **Application fails to start**:
   ```bash
   # Check with debug logging
   isolator --debug application
   ```

2. **Display issues**:
   ```bash
   # Verify X11 socket access
   isolator --debug --profile BROWSER firefox
   ```

3. **Network problems**:
   ```bash
   # Test network connectivity
   isolator --debug application
   ```

### Debug Information

Enable detailed logging for troubleshooting:

```bash
isolator --debug application 2> debug.log
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Gemechis Chala - gladsonchala@gmail.com

Project Link: [https://github.com/venopyx/isolator](https://github.com/venopyx/isolator)

## License

Distributed under the MIT License. See `LICENSE` for more information.