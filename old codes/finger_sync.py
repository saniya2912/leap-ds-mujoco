import numpy as np

class FingerSynchronizationDS:
    def __init__(self, beta1=1.0, beta2=5.0):
        self.beta1 = beta1
        self.beta2 = beta2

    # Intermediate Dynamics DS
    def intermediate_ds(self, z, zd):
        """ Intermediate dynamic system for variable z. """
        z_dot = -self.beta1 * (1 - np.exp(-self.beta2 * (z - zd))) / (1 + np.exp(-self.beta2 * (z - zd)))
        return z_dot

    # Task-Space DS
    def task_space_ds(self, x, z, x1, x2, Ax=5):
        I_dx = np.eye(len(x))  # Identity matrix
        x_dot = -((z * Ax + self.intermediate_ds(z, 0) * I_dx) @ (x2 - x1)) - Ax * (x - x2)
        return x_dot

    # DS Coupling for multiple fingers
    def coupled_ds(self, nf, alpha, zd):
        return (1 / (nf + 1)) * (zd + sum(alpha))

    # Overall DS for one fingertip
    def overall_ds(self, alpha, zd, z, x, x1, x2):
        z_dot = self.intermediate_ds(alpha, zd)
        x_dot = self.task_space_ds(x, z, x1, x2)
        return z_dot, x_dot

# Example of usage
if __name__ == "__main__":
    # Initialize the DS for finger synchronization
    ds = FingerSynchronizationDS()

    # Variables for simulation (randomly initialized here)
    x1 = np.array([0, 0, 0])  # Initial position
    x2 = np.array([1, 1, 1])  # Final position
    x = np.array([0.5, 0.5, 0.5])  # Current fingertip position
    alpha = 0.5  # Current relative distance
    z = 0.2  # Intermediate DS state
    zd = 1.0  # Desired final state

    # Simulate one step
    z_dot, x_dot = ds.overall_ds(alpha, zd, z, x, x1, x2)

    print("z_dot (Change in intermediate DS):", z_dot)
    print("x_dot (Change in fingertip position):", x_dot)