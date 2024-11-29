#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "control_libraries::dynamical_systems" for configuration "Release"
set_property(TARGET control_libraries::dynamical_systems APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(control_libraries::dynamical_systems PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdynamical_systems.so"
  IMPORTED_SONAME_RELEASE "libdynamical_systems.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS control_libraries::dynamical_systems )
list(APPEND _IMPORT_CHECK_FILES_FOR_control_libraries::dynamical_systems "${_IMPORT_PREFIX}/lib/libdynamical_systems.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
