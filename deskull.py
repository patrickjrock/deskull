# Patrick Rock 8/30/2020
# deskull.py
# preprocessing step to remove extra-axial tissue

import numpy as np
from skimage import measure
from skimage import filters 
from scipy import stats
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

def filter_range(voxels, upper=75, lower=0):
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
    return measure.label(blobs)

def biggest_component(ccs):
    ccs = ccs.flatten()
    ccs = ccs[ccs != 0] 
    m = stats.mode(ccs) 
    if len(m[0]) == 0: 
        return 0
    return stats.mode(ccs)[0][0]

def toss_small_components(voxels):
    ccs = connected_components(voxels)
    b = biggest_component(ccs)
    for i in range(ccs.shape[0]):
        for j in range(ccs.shape[1]):
            if ccs [i][j] != b:
                voxels[i][j] = 0 
    return voxels

def animate(data, iv=100):
    fig = plt.figure()
    ims = []
    for i in range(data.shape[0]):
        im = plt.imshow(data[i], cmap='gray', animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=iv, blit=True,
                                    repeat_delay=1000)
    plt.show()

def npmap(f, xs):
    return np.array(list(map(f, xs)))

def deskull(nii_file):
    img = nib.load(nii_file)
    data = img.get_fdata()
    data = filter_range(data) # filter out skull
    data = npmap(toss_small_components, data) # saggital pass 
    data = np.transpose(data, (2,0,1)) # change orientation 
    data = npmap(toss_small_components, data) # axial pass 
    data = np.transpose(data, (1,2,0)) # restore original orientation
    return nib.Nifti1Image(data, img.affine, img.header)




