import numpy as np
from skimage import measure
from skimage import filters 
from scipy import stats
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

# consider connected componenets only in two dimensions
# do multiple orthogonal passes and throw out the small components 

# should voxels have a type? they can keep track of what cc they are in

np.set_printoptions(threshold=sys.maxsize)

def get_axial(voxels, n):
    # reformats matrix so first index pulls axials     
    axial = [] 
    for vs in voxels:
       axial.append([v[n] for v in vs])
    return axial

def strip_range(voxels, upper=75, lower=0):
    def f(v):
        if v<lower or v>upper:
            return 0
        else:
            return v
    return np.vectorize(f)(voxels)

def connected_components(voxels):
    def f(v):
        if v < 1: 
            return 0
        else:
            return 1
    blobs = np.vectorize(f)(voxels)
    m = measure.label(blobs)
    return m

def biggest_component(ccs):
    ccs = ccs.flatten()
    ccs = ccs[ccs != 0] # remove 0s
    return stats.mode(ccs)[0][0]

def toss_small_components(voxels):
    # sets all voxels to zero that arent in the largest connected component
    ccs = connected_components(voxels)
    b = biggest_component(ccs)
    

def animate(data):
    fig = plt.figure()
    ims = []
    for i in range(66):
        im = plt.imshow(get_axial(data, i), cmap='nipy_spectral', animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=100, blit=True,
                                    repeat_delay=1000)
    plt.show()


if len(sys.argv) == 1:
    level = 200
else:
    level = int(sys.argv[1])


img = nib.load('l1_Orig.nii')
data = img.get_fdata()
stripped_data = strip_range(data)
strip = nib.Nifti1Image(stripped_data, img.affine, img.header)
nib.save(strip, 'strip.nii')


cc = connected_components(get_axial(stripped_data,30))
plt.imshow(cc, cmap='nipy_spectral')
plt.show()

#os.system('miview bones.nii')



