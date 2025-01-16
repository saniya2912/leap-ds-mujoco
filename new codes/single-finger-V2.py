import math
import time
from datetime import timedelta
from dynamical_systems import create_cartesian_ds, DYNAMICAL_SYSTEM_TYPE
from pyquaternion import Quaternion
import mujoco
import mujoco.viewer as viewer
import state_representation as sr
from robot_model import Model, QPInverseVelocityParameters

class MuJoCoRobotInterface:

    def __init__(self, robot_name, model_path):
        # Load the MuJoCo model
        self._robot = Model(robot_name, model_path)
        self.eef_pose = None
        self.joint_positions = sr.JointPositions().Zero(robot_name, self._robot.get_joint_frames())
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        self.viewer = viewer.launch_passive(self.model, self.data)
        self.read_robot_state()


    def read_robot_state(self):
        # this is a dummy robot, we assume the joint state is executed
        self.eef_pose = self._robot.forward_kinematics(self.joint_positions)


    def send_control_command(self, desired_eef_twist, dt):
        # create the inverse velocity parameters and set the period of the control loop
        parameters = QPInverseVelocityParameters()
        parameters.dt = dt
        # apply the inverse velocity
        desired_joint_velocities = self._robot.inverse_velocity(desired_eef_twist, self.joint_positions, parameters)
        # integrate the new position
        self.joint_positions = (dt * desired_joint_velocities) + self.joint_positions


def control_loop_step(robot, ds, dt):
    robot.read_robot_state()
    print(robot.joint_positions)
    print(robot.eef_pose)
    # get the twist evaluated at current pose
    desired_twist = sr.CartesianTwist(ds.evaluate(robot.eef_pose))
    robot.send_control_command(desired_twist, dt)


def control_loop(robot, dt, tolerance):
    target = sr.CartesianPose(robot.eef_pose.get_name(), robot.eef_pose.get_reference_frame())
    target.set_position(0.5, 0.0, 0.5)
    target.set_orientation(Quaternion(axis=[0.0, 1.0, 0.0], radians=math.pi))
    ds = create_cartesian_ds(DYNAMICAL_SYSTEM_TYPE.POINT_ATTRACTOR)
    ds.set_parameter(sr.Parameter("attractor", target, sr.ParameterType.STATE, sr.StateType.CARTESIAN_POSE))

    # loop until target is reached
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
    model_path = "/home/aaditya/leap-ds-control/leap hand/robot.urdf"
    # Initialize the MuJoCo robot interface
    robot = MuJoCoRobotInterface("leap", model_path)
    control_loop(robot, timedelta(milliseconds=100), 1e-3)


if __name__ == "__main__":
    main()
