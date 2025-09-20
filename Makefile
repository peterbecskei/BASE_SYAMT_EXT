# Makefile for background.cpp
# Requires libcurl and jsoncpp libraries

CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2
TARGET = background
SOURCES = background.cpp
HEADERS = background.h

# Library flags
LIBS = -lcurl -ljsoncpp

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LIBS)

# Clean build artifacts
clean:
	rm -f $(TARGET) *.o

# Install dependencies (Ubuntu/Debian)
install-deps:
	sudo apt-get update
	sudo apt-get install libcurl4-openssl-dev libjsoncpp-dev

# Install dependencies (Windows with vcpkg)
install-deps-windows:
	vcpkg install curl jsoncpp

# Run the program
run: $(TARGET)
	./$(TARGET)

# Debug build
debug: CXXFLAGS += -g -DDEBUG
debug: $(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build the executable (default)"
	@echo "  clean        - Remove build artifacts"
	@echo "  install-deps - Install required libraries (Ubuntu/Debian)"
	@echo "  install-deps-windows - Install required libraries (Windows with vcpkg)"
	@echo "  run          - Build and run the program"
	@echo "  debug        - Build with debug symbols"
	@echo "  help         - Show this help message"

.PHONY: all clean install-deps install-deps-windows run debug help
