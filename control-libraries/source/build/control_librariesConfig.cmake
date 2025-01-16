
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was Config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

set(_control_libraries_supported_components state_representation dynamical_systems robot_model controllers)
set(control_libraries_LIBRARIES "state_representation;dynamical_systems;robot_model;/usr/local/lib/libpinocchio.so;/usr/lib/x86_64-linux-gnu/libboost_filesystem.so;/usr/lib/x86_64-linux-gnu/libboost_serialization.so;/usr/lib/x86_64-linux-gnu/libboost_system.so;OsqpEigen::OsqpEigen;osqp::osqp;Eigen3::Eigen;controllers")

include(CMakeFindDependencyMacro)
find_dependency(Eigen3)

# Find robot model dependencies if it is in the interface library list and no components are explicitly listed
if ("robot_model" IN_LIST control_libraries_LIBRARIES AND NOT control_libraries_FIND_COMPONENTS)
  find_dependency(pinocchio)
  find_dependency(OsqpEigen)
  find_dependency(osqp)
endif()

foreach(_comp ${control_libraries_FIND_COMPONENTS})
  if (${_comp} IN_LIST _control_libraries_supported_components)
    set(control_libraries_${_comp}_FOUND True)
  else()
    set_and_check(control_libraries_FOUND False)
    set_and_check(control_libraries_NOT_FOUND_MESSAGE "Unsupported component: ${_comp}")
  endif()

  # Find robot model dependencies if the corresponding components are explicitly listed
  if (${_comp} STREQUAL "controllers" OR ${_comp} STREQUAL "robot_model")
    find_dependency(pinocchio)
    find_dependency(OsqpEigen)
    find_dependency(osqp)
  endif()

  include("${CMAKE_CURRENT_LIST_DIR}/control_libraries_${_comp}_targets.cmake")
endforeach()

check_required_components(control_libraries)
