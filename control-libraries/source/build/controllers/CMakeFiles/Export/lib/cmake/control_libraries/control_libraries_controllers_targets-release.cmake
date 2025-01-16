#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "control_libraries::controllers" for configuration "Release"
set_property(TARGET control_libraries::controllers APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(control_libraries::controllers PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcontrollers.so"
  IMPORTED_SONAME_RELEASE "libcontrollers.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS control_libraries::controllers )
list(APPEND _IMPORT_CHECK_FILES_FOR_control_libraries::controllers "${_IMPORT_PREFIX}/lib/libcontrollers.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
