#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "control_libraries::state_representation" for configuration "Release"
set_property(TARGET control_libraries::state_representation APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(control_libraries::state_representation PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libstate_representation.so"
  IMPORTED_SONAME_RELEASE "libstate_representation.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS control_libraries::state_representation )
list(APPEND _IMPORT_CHECK_FILES_FOR_control_libraries::state_representation "${_IMPORT_PREFIX}/lib/libstate_representation.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
