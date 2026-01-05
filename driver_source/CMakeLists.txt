cmake_minimum_required(VERSION 3.10)
project(VirtualControllerDriver)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenVR SDK
# You need to download OpenVR SDK and set OPENVR_SDK_PATH
set(OPENVR_SDK_PATH "${CMAKE_CURRENT_SOURCE_DIR}/openvr" CACHE PATH "Path to OpenVR SDK")

include_directories(${OPENVR_SDK_PATH}/headers)

# Source files
set(SOURCES
    virtual_controller_driver.cpp
)

# Create DLL
add_library(driver_virtualcontroller SHARED ${SOURCES})

# Link OpenVR library
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    # 64-bit
    target_link_libraries(driver_virtualcontroller ${OPENVR_SDK_PATH}/lib/win64/openvr_api.lib)
else()
    # 32-bit
    target_link_libraries(driver_virtualcontroller ${OPENVR_SDK_PATH}/lib/win32/openvr_api.lib)
endif()

# Output directory
set_target_properties(driver_virtualcontroller PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
