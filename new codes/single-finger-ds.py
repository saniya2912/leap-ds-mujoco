import math
import os
import state_representation as sr
import time
from datetime import timedelta
from dynamical_systems import create_cartesian_ds, DYNAMICAL_SYSTEM_TYPE
from pyquaternion import Quaternion
import mujoco_py
import numpy as np


class MuJoCoRobotInterface:

    def __init__(self, mujoco_model_path):
        # Load the MuJoCo model
        self.model = mujoco_py.load_model_from_path(mujoco_model_path)
        self.sim = mujoco_py.MjSim(self.model)
        self.viewer = mujoco_py.MjViewer(self.sim)  # Initialize the viewer
        self.eef_name = "fingertip"  # Replace with the actual end-effector name in your model
        self.eef_pose = None
        self.joint_positions = sr.JointPositions()
        self.read_robot_state()

    def read_robot_state(self):
        # Update joint positions
        joint_names = [self.model.joint_id2name(i) for i in range(self.model.njnt)]
        joint_values = self.sim.data.qpos[:len(joint_names)]
        self.joint_positions = sr.JointPositions("robot", joint_names, joint_values)

        # Update end-effector pose
        eef_position = self.sim.data.get_body_xpos(self.eef_name)
        eef_orientation = self.sim.data.get_body_xquat(self.eef_name)
        self.eef_pose = sr.CartesianPose(
            self.eef_name, 
            "world", 
            position=eef_position, 
            orientation=Quaternion(eef_orientation)
        )

    def send_control_command(self, desired_eef_twist, dt):
        # Get current Jacobian for the end-effector
        jacobian = np.zeros((6, self.model.nv))
        mujoco_py.functions.mj_jacBody(
            self.model, self.sim.data, jacobian, self.model.body_name2id(self.eef_name)
        )

        # Compute desired joint velocities using Jacobian pseudo-inverse
        jacobian_pinv = np.linalg.pinv(jacobian[:3])  # Consider only positional part for simplicity
        desired_velocity = desired_eef_twist.get_linear_velocity()
        joint_velocities = np.dot(jacobian_pinv, desired_velocity)

        # Apply joint velocities
        self.sim.data.qvel[:len(joint_velocities)] = joint_velocities
        self.sim.step()

        # Render the simulation in the viewer
        self.viewer.render()


def control_loop_step(robot, ds, dt):
    # Read the robot state
    robot.read_robot_state()
    print(robot.joint_positions)
    print(robot.eef_pose)

    # Get the twist evaluated at current pose
    desired_twist = sr.CartesianTwist(ds.evaluate(robot.eef_pose))

    # Send the desired twist to the robot
    robot.send_control_command(desired_twist, dt)


def control_loop(robot, dt, tolerance):
    target = sr.CartesianPose(robot.eef_pose.get_name(), robot.eef_pose.get_reference_frame())
    target.set_position(.5, .0, .75)
    target.set_orientation(Quaternion(axis=[.0, 1., .0], radians=math.pi))

    # Create dynamical system
    ds = create_cartesian_ds(DYNAMICAL_SYSTEM_TYPE.POINT_ATTRACTOR)
    ds.set_parameter(sr.Parameter("attractor", target, sr.ParameterType.STATE, sr.StateType.CARTESIAN_POSE))

    # Loop until target is reached
    distance = sr.dist(robot.eef_pose, target, sr.CartesianStateVariable.POSE)
    while distance > tolerance:
        control_loop_step(robot, ds, dt)
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
    mujoco_model_path = "/home/aaditya/leap-ds-control/leap hand/index_finger.xml"  # Replace with your robot's MuJoCo XML file path
    robot = MuJoCoRobotInterface(mujoco_model_path)
    control_loop(robot, timedelta(milliseconds=100), 1e-3)


if __name__ == "__main__":
    main()
