import math
import os
import time
from datetime import timedelta
from dynamical_systems import create_cartesian_ds, DYNAMICAL_SYSTEM_TYPE
from pyquaternion import Quaternion
import mujoco
import mujoco.viewer as viewer
import numpy as np
import state_representation as sr

class MuJoCoRobotInterface:
    def __init__(self, model_path):
        # Load the MuJoCo model
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        self.viewer = viewer.launch_passive(self.model, self.data)

        # Initialize variables
        self.eef_pose = None
        self.joint_positions = None
        self.robot_name = "mujoco_robot"  # Placeholder robot name
        self.target_marker = None
        self.read_robot_state()

    def read_robot_state(self):
        # Get joint positions
        joint_positions = self.data.qpos[:self.model.njnt]
        joint_names = [mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(self.model.njnt)]
        self.joint_positions = sr.JointPositions(self.robot_name, joint_names, joint_positions)

        # Calculate the end-effector pose using forward kinematics
        self.eef_pose = self._compute_eef_pose()

    def _compute_eef_pose(self):
    # Retrieve the end-effector position and orientation from MuJoCo
        eef_body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "fingertip")
        eef_position = self.data.xpos[eef_body_id]
        eef_orientation = self.data.xquat[eef_body_id]
        return sr.CartesianPose(self.robot_name, eef_position, eef_orientation, "world")


    def send_control_command(self, desired_eef_twist, dt):
    # Compute position and rotation Jacobians
        jacp = np.zeros((3, self.model.nv))
        jacr = np.zeros((3, self.model.nv))
        eef_body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "fingertip")
        mujoco.mj_jacBody(self.model, self.data, jacp, jacr, eef_body_id)

        # Combine position and rotation Jacobians
        jacobian = np.vstack((jacp, jacr))

        # Desired twist as an array
        desired_twist_array = np.hstack((desired_eef_twist.get_linear_velocity(), desired_eef_twist.get_angular_velocity()))

        # Compute joint velocities using pseudo-inverse
        joint_velocities = np.linalg.pinv(jacobian).dot(desired_twist_array)

        # Apply the joint velocities
        self.data.qvel[:len(joint_velocities)] = joint_velocities
        mujoco.mj_step(self.model, self.data)
        self.viewer.sync()

        # Update joint positions
        self.read_robot_state()


def set_target_marker(self, target_position):
        # Add a visual marker for the target position
        if self.target_marker is None:
            self.target_marker = np.zeros(3)
        self.target_marker[:] = target_position

        # Adding marker information for the green sphere
        green_sphere_position = target_position + np.array([-0.03, -0.03, -0.02]) 
        self.model.geom_pos = np.vstack((self.model.geom_pos, green_sphere_position))
        self.model.geom_size = np.vstack((self.model.geom_size, [0.01, 0.01, 0.01]))  # Sphere size
        self.model.geom_rgba = np.vstack((self.model.geom_rgba, [0, 1, 0, 1]))  # Green color
        self.model.geom_type = np.append(self.model.geom_type, mujoco.mjtGeom.mjGEOM_SPHERE)

        self.viewer.sync()


def control_loop_step(robot, ds, dt):
    robot.read_robot_state()
    print(robot.joint_positions)
    print(robot.eef_pose)

    desired_twist = sr.CartesianTwist(ds.evaluate(robot.eef_pose))
    robot.send_control_command(desired_twist, dt)


def control_loop(robot, dt, tolerance):
    target = sr.CartesianPose(robot.eef_pose.get_name(), robot.eef_pose.get_reference_frame())
    target.set_position(-0.03, -0.03, -0.02)
    target.set_orientation(Quaternion(axis=[0.0, 1.0, 0.0], radians=math.pi))

    ds = create_cartesian_ds(DYNAMICAL_SYSTEM_TYPE.POINT_ATTRACTOR)
    ds.set_parameter(sr.Parameter("attractor", target, sr.ParameterType.STATE, sr.StateType.CARTESIAN_POSE))

    distance = sr.dist(robot.eef_pose, target, sr.CartesianStateVariable.POSE)
    while distance > tolerance:
        control_loop_step(robot, ds, dt.total_seconds())
        distance = sr.dist(robot.eef_pose, target, sr.CartesianStateVariable.POSE)
        print(f"Distance to attractor: {distance}")
        print("-----------")
        time.sleep(dt.total_seconds())

    print("##### TARGET #####")
    print(target)
    print("##### CURRENT STATES #####")
    print(robot.joint_positions)
    print(robot.eef_pose)


def main():
    # Replace with the path to your MuJoCo XML model
    model_path = "/home/aaditya/leap-ds-control/leap hand/index_finger.xml"

    # Initialize the MuJoCo robot interface
    robot = MuJoCoRobotInterface(model_path)

    control_loop(robot, timedelta(milliseconds=100), 1e-3)


if __name__ == "__main__":
    main()
