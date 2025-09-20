# C++ Background Runner

This is a C++ implementation of the Python `background.py` script that replicates the core functionality of `background.js`.

## Features

- **HTTP Requests**: Uses libcurl for HTTP operations
- **CSV Data Persistence**: Reads/writes URL data to CSV files
- **ID Tracking**: Maintains last processed ID in a text file
- **Rate Limiting**: Handles 429 and 302 responses with appropriate delays
- **API Integration**: Fetches data from automobile.at API
- **Cross-platform**: Works on Windows, Linux, and macOS

## Dependencies

### Required Libraries
- **libcurl**: For HTTP requests
- **jsoncpp**: For JSON parsing (optional, can be removed if not needed)

### Installation

#### Ubuntu/Debian
```bash
sudo apt-get install libcurl4-openssl-dev libjsoncpp-dev
```

#### Windows (with vcpkg)
```bash
vcpkg install curl jsoncpp
```

#### macOS (with Homebrew)
```bash
brew install curl jsoncpp
```

## Building

### Windows

#### Using Build Script
```cmd
build.bat
```

#### Using CMake
```cmd
mkdir build
cd build
cmake ..
cmake --build .
```

#### Manual Compilation
```cmd
# With Visual Studio
cl /EHsc /std:c++11 background.cpp /Fe:background.exe

# With MinGW-w64
g++ -std=c++11 -Wall -Wextra -O2 -o background.exe background.cpp -lcurl -ljsoncpp

# With Clang
clang++ -std=c++11 -Wall -Wextra -O2 -o background.exe background.cpp -lcurl -ljsoncpp
```

### Linux/macOS

#### Using Makefile
```bash
# Build the executable
make

# Build with debug symbols
make debug

# Clean build artifacts
make clean

# Install dependencies (Ubuntu/Debian)
make install-deps
```

#### Using CMake
```bash
mkdir build
cd build
cmake ..
make
```

#### Manual Compilation
```bash
g++ -std=c++11 -Wall -Wextra -O2 -o background background.cpp -lcurl -ljsoncpp
```

## Usage

```bash
# Run the program
./background

# Or using make
make run
```

## Configuration

Edit the `Config` class in `background.h` to modify:

- `START_ID`: Starting ID for checking (default: 1251923)
- `BASE_URL`: Base URL for automobile.at listings
- `CHECK_INTERVAL_SECONDS`: Delay between requests (default: 0.2s)
- `URL_DATA_CSV`: CSV file for data persistence
- `LAST_ID_FILE`: Text file for last processed ID

## Output Files

- **URL_data.csv**: Contains all checked URLs with their status and metadata
- **LastID.TXT**: Contains the last successfully processed ID

## Differences from Python Version

1. **Error Handling**: More explicit error handling with try-catch blocks
2. **Memory Management**: Manual memory management for CURL handles
3. **String Handling**: Uses std::string instead of Python strings
4. **File I/O**: Uses std::fstream instead of Python's file operations
5. **Threading**: Uses std::this_thread for delays instead of time.sleep()

## Troubleshooting

### Common Issues

1. **Missing Libraries**: Ensure libcurl and jsoncpp are installed
2. **Compilation Errors**: Check C++11 support in your compiler
3. **Runtime Errors**: Verify network connectivity and file permissions

### Debug Mode

Build with debug symbols for better error tracking:
```bash
make debug
```

## License

Same as the original Python script.
