import numpy as np
from skimage import measure
from skimage import filters 

import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os


def get_axial(voxels, n):
    # reformats matrix so first index pulls axials     
    axial = [] 
    for sl in voxels:
       axial.append([x[n] for x in sl])
    return axial

def strip_skull(voxels, hu=100):
    def f(x):
        if x>hu:
            return -1000
        else:
            return x
    return np.vectorize(f)(voxels)

def animate(data):
    fig = plt.figure()
    ims = []
    for i in range(66):
        im = plt.imshow(get_axial(data, i), animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=80, blit=True,
                                    repeat_delay=1000)
    plt.show()


if len(sys.argv) == 1:
    level = 200
else:
    level = int(sys.argv[1])




img = nib.load('l1_Orig.nii')
data = img.get_fdata()
windowed_data = strip_skull(data)
bones = nib.Nifti1Image(windowed_data, img.affine, img.header)
nib.save(bones, 'bones.nii')


all_labels = measure.label(windowed_data)


#os.system('miview bones.nii')



