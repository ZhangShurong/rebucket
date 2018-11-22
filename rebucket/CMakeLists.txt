cmake_minimum_required(VERSION 2.8.9)
project (rebucket)
set(CMAKE_BUILD_TYPE Release)

# Bring the headers, such as helloworld.h into the project
INCLUDE_DIRECTORIES(include)
SET(SOURCE_PATH ${PROJECT_SOURCE_DIR}/src)
# AUX_SOURCE_DIRECTORY(${SOURCE_PATH} SRC_LIST)
# However, the file(GLOB...) allows for wildcard additions:
file(GLOB SOURCES "src/*.cpp")
file(GLOB TEST_SOURCES "test/*.cpp")
add_executable(test ${TEST_SOURCES})

# Generate the shared library from the sources
add_library(rebucket SHARED ${SOURCES})
# create the executable
# include (GenerateExportHeader)
# GENERATE_EXPORT_HEADER(rebucket
#              BASE_NAME rebucket
#              EXPORT_MACRO_NAME SHARED_EXPORT
#              EXPORT_FILE_NAME rebucket_EXPORTS.h
#              STATIC_DEFINE SHARED_EXPORTS_BUILT_AS_STATIC)
target_link_libraries(test rebucket)
# Set the location for library installation -- i.e., /usr/local/lib
# not really necessary in this example. Use "sudo make install" to apply
#install(TARGETS hello DESTINATION /usr/local/lib)
configure_file(test/test.py test.py COPYONLY)
