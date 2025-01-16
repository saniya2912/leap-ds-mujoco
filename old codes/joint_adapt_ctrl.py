import numpy as np

class JointSpaceAdaptiveController:
    def __init__(self, nj):
        # Initialize parameters
        self.nj = nj  # number of joints
        self.q = np.zeros(nj)  # joint positions
        self.q_dot = np.zeros(nj)  # joint velocities
        self.Adapt_gains_q = np.zeros((nj, 2 * nj))  # Adaptive gain for q
        self.Adapt_gains_r = np.zeros((nj, nj))  # Adaptive gain for r
        self.P = np.eye(2 * nj)  # Positive definite matrix
        self.Ar = np.eye(2 * nj)  # Matrix controlling the reference model dynamics
        self.Br = np.eye(nj)  # Regulation matrix

        # Control parameters
        self.kappa_star = np.array([0.15, 0.12, 0.1, 0.05])  # Desired stiffness for each joint
        self.epsilon_j = 0.02  # Error tolerance

    def nominal_joint_space_dynamics(self, x_dot_desired):
        # Define the reference model dynamics
        r = x_dot_desired  # Regulation signal
        zeta_dot_ref = self.Ar @ np.hstack((self.q, self.q_dot)) + self.Br @ r
        return zeta_dot_ref

    def update_adaptive_gains(self, e, r, q):
        # Adaptive laws for updating the control gains
        lambda_q = np.diag(np.maximum(0, 1 - np.exp(-e**2 / (2 * self.epsilon_j**2))))
        S = np.diag(self.kappa_star * (1 - 1 / (np.diag(self.Adapt_gains_q @ self.Adapt_gains_q.T) + 0.001)))
        S_r = np.diag(self.kappa_star * (1 - 1 / (np.diag(self.Adapt_gains_r @ self.Adapt_gains_r.T) + 0.001)))

        self.Adapt_gains_q += -lambda_q @ (self.Br.T @ self.P @ e @ q.T - S @ self.Adapt_gains_q)
        self.Adapt_gains_r += -lambda_q @ (self.Br.T @ self.P @ e @ r.T - S_r @ self.Adapt_gains_r)

    def compute_torque(self, x_dot_desired):
        # Compute the joint torques for the control loop
        r = x_dot_desired
        zeta_dot_ref = self.nominal_joint_space_dynamics(r)

        # Compute the tracking error
        e = np.hstack((self.q, self.q_dot)) - zeta_dot_ref

        # Update the adaptive gains
        self.update_adaptive_gains(e, r, self.q)

        # Calculate joint torques using the adaptive control law
        torque = self.Adapt_gains_q @ np.hstack((self.q, self.q_dot)) + self.Adapt_gains_r @ r

        return torque

# Example usage
nj = 4  # Number of joints
controller = JointSpaceAdaptiveController(nj)

# Desired fingertip velocity
x_dot_desired = np.array([0.1, 0.2, 0.3, 0.4])

# Compute torque to realize desired velocity
torque_output = controller.compute_torque(x_dot_desired)
print("Joint Torques:", torque_output)
