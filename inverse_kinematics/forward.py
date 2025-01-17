import numpy as np
import scipy


# specify prior
# specify segment lengths

# sample_prior(prior_spec)
# eval_prior(prior_spec)

# forward(prior_samples, segment_lengths)
#  component (start, parameter)
class RobotArm():

    def __init__(self, components):

        self.components = components 

    def forward(self, theta, start_coord=None, only_end=True):
        """
        Parameters
        ----------
        start : (batch_size, start_coord_dim)
            Coordinates of where robot is fixated.
            (0, 0, 0) for a 2D robot indicates x=0, y=0, phi=0
        theta : (batch_size, n_params)
            Parameters for the components.

        Returns
        -------
        end   : (batch_size, n_end)
            Coordinates of the end-effector.
        """

        n_arms = list(theta.values()).pop().shape[0]

        if start_coord is None:
            start_coord = np.zeros((n_arms, 3))
        else:
            assert start_coord.shape == (n_arms, 3)

        coord = start_coord.copy()

        if not only_end:
            coords = np.empty((start_coord.shape[0], len(self.components)+1, start_coord.shape[1]))
            coords[:,0,:] = coord 
        
        for i,name in enumerate(self.components.keys()):
            coord = self.components[name].forward(theta[name], coord) 
            
            if not only_end:
                coords[:,i+1,:] = coord

        if only_end:
            return coord
        return coords

class Rail():

    def __init__(self, fix_rot=0):

        self.fix_rot = fix_rot

    def forward(self, theta, start_coord):

        assert len(theta.shape) == 1
        batch_size = theta.shape[0]
        assert start_coord.shape == (batch_size, 3)

        coord = start_coord.copy()
        
        coord[:,0] -= np.sin(coord[:,2]) * theta
        coord[:,1] += np.cos(coord[:,2]) * theta
        coord[:,2] += self.fix_rot
        
        return coord

class Joint():

    def __init__(self, length):

        self.length = length

    def forward(self, theta, start_coord):
        
        assert len(theta.shape) == 1
        batch_size = theta.shape[0]
        assert start_coord.shape == (batch_size, 3)

        coord = start_coord.copy()

        coord[:,0] += self.length * np.cos(coord[:,2] + theta)
        coord[:,1] += self.length * np.sin(coord[:,2] + theta)
        coord[:,2] += theta

        return coord

# sample posterior
#  needs prior to sample and evaluate
#  is hand-crafted to reparameterize problem given by forward





if __name__ == "__main__":
    print("Testing IK: forward component")
    # to something like test.py

    n_arms = 100
    start_coord = np.zeros((n_arms,3))  #np.random.normal(size=(5,3))
    theta = np.random.normal(loc=0, scale=[0.25,0.5,0.5,0.5], size=(n_arms,4))
    r = Rail()
    j1 = Joint(0.5)
    j2 = Joint(0.5)
    j3 = Joint(1.0)
    arm = RobotArm([r,j1,j2,j3])
    coords = arm.forward(theta, start_coord, only_end=False)
