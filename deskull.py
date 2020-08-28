import numpy as np
from skimage import measure
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os


if len(sys.argv) == 1:
    level = 200

else:
    level = int(sys.argv[1])

img = nib.load('l1_Orig.nii')
data = img.get_fdata()
windowed_data = 1*(data > level)
bones = nib.Nifti1Image(windowed_data, img.affine, img.header)
nib.save(bones, 'bones.nii')
all_labels = measure.label(windowed_data)

fig = plt.figure()
ims = []
for i in range(512):
    im = plt.imshow(all_labels[i], cmap='nipy_spectral', animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=20, blit=True,
                                repeat_delay=1000)
plt.show()

#os.system('miview bones.nii')



