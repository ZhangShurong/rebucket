cmake_minimum_required(VERSION 2.8.9)
project (rebucket)
set(CMAKE_BUILD_TYPE Release)

# Bring the headers, such as helloworld.h into the project
include_directories(include)
SET(SOURCE_PATH ${PROJECT_SOURCE_DIR}/src)
AUX_SOURCE_DIRECTORY(${SOURCE_PATH} SRC_LIST)
# However, the file(GLOB...) allows for wildcard additions:
file(GLOB SOURCES "src/*.cpp")

# Generate the shared library from the sources
add_library(rebucket SHARED ${SOURCES})

# Set the location for library installation -- i.e., /usr/local/lib
# not really necessary in this example. Use "sudo make install" to apply
#install(TARGETS hello DESTINATION /usr/local/lib)
