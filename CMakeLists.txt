cmake_minimum_required(VERSION 3.10)
project(BackgroundRunner)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)
pkg_check_modules(JSONCPP REQUIRED jsoncpp)

# Add executable
add_executable(background background.cpp)

# Include directories
target_include_directories(background PRIVATE ${CURL_INCLUDE_DIRS} ${JSONCPP_INCLUDE_DIRS})

# Link libraries
target_link_libraries(background ${CURL_LIBRARIES} ${JSONCPP_LIBRARIES})

# Compiler flags
target_compile_options(background PRIVATE ${CURL_CFLAGS_OTHER} ${JSONCPP_CFLAGS_OTHER})

# Windows-specific settings
if(WIN32)
    target_compile_definitions(background PRIVATE WIN32_LEAN_AND_MEAN)
endif()

# Installation
install(TARGETS background DESTINATION bin)
