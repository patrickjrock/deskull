import numpy as np
from skimage import measure
from skimage import filters 

import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

# consider connected componenets only in two dimensions
# do multiple orthogonal passes and throw out the small components 

np.set_printoptions(threshold=sys.maxsize)

def get_axial(voxels, n):
    # reformats matrix so first index pulls axials     
    axial = [] 
    for sl in voxels:
       axial.append([x[n] for x in sl])
    return axial

def strip_range(voxels, upper=75, lower=0):
    def f(x):
        if x<lower or x>upper:
            return 0
        else:
            return x
    return np.vectorize(f)(voxels)

def connected_components(voxels):
    def f(x):
        if x < 1: 
            return 0
        else:
            return x
    #voxels = filters.gaussian(voxels, sigma = 200) 
    blobs = np.vectorize(f)(voxels)

    # remove this
    b = nib.Nifti1Image(blobs, img.affine, img.header)
    nib.save(b, 'blobs.nii')

    v = nib.Nifti1Image(voxels, img.affine, img.header)
    nib.save(v, 'voxels.nii')


    m = measure.label(blobs)
    print(m)
    return m


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


animate(connected_components(stripped_data))


#os.system('miview bones.nii')



