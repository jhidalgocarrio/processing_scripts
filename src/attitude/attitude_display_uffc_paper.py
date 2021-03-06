#!/usr/bin/env python

path = '/home/javi/npi/data/20150323_ww_dlr/imu_stim300_attitude_test_20150325-1716/'

##################################
pose_ikf_orient_file = path + 'pose_ikf_orientation.0.data'

#without allan data
pose_ikf_inflated_coef_orient_file = path + 'pose_ikf_inflated_coef_orientation.4.data'

pose_ikf_data_sheet_coef_orient_file = path + 'pose_ikf_data_sheet_coef_orientation.0.data'
# incomplete mdel
#pose_ikf_data_sheet_coef_orient_file = path + 'pose_ikf_incomplete_model.1.data'

pose_imu_orient_file = path + 'pose_imu_orientation.0.data'

pose_ref_orient_file = path + 'pose_ref_orientation.0.data'
##################################

import sys
sys.path.insert(0, './src/core')
import csv, scipy
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import quaternion as quat
import datadisplay as data

# Read the ikf filter orientation information
ikf_orient = data.QuaternionData()
ikf_orient.readData(pose_ikf_orient_file, cov=True)

# Read the inflated values for ikf filter orientation information
ikf_inflated_coef_orient = data.QuaternionData()
ikf_inflated_coef_orient.readData(pose_ikf_inflated_coef_orient_file, cov=True)

# Read the data sheet values for ikf filter orientation information
ikf_data_sheet_coef_orient = data.QuaternionData()
ikf_data_sheet_coef_orient.readData(pose_ikf_data_sheet_coef_orient_file, cov=True)

# Read the imu orientation information
imu_orient = data.QuaternionData()
imu_orient.readData(pose_imu_orient_file, cov=True)

# Read the reference orientation information
reference_orient = data.QuaternionData()
reference_orient.readData(pose_ref_orient_file, cov=False)

################################
### COMPUTE COV EIGENVALUES  ###
################################
ikf_orient.covSymmetry()
ikf_orient.eigenValues()

ikf_inflated_coef_orient.covSymmetry()
ikf_inflated_coef_orient.eigenValues()

ikf_data_sheet_coef_orient.covSymmetry()
ikf_data_sheet_coef_orient.eigenValues()

imu_orient.covSymmetry()
imu_orient.eigenValues()

########################
### PLOTTING VALUES  ###
########################

matplotlib.rcParams.update({'font.size': 30, 'font.weight': 'bold'})
fig = plt.figure(1)
ax = fig.add_subplot(111)

plt.rc('text', usetex=False)# activate latex text rendering

time = ikf_orient.atime
time = time - ikf_orient.atime[0] # Time alignment
euler = []
euler.append(ikf_orient.getEuler(0))# Yaw
euler.append(ikf_orient.getEuler(1))# Pitch
euler.append(ikf_orient.getEuler(2))# Roll

# Alignment with ground truth
alignment_diff = []
alignment_diff.append(ikf_orient.getEuler(0)[0] - reference_orient.getEuler(0)[0]) # Yaw
alignment_diff.append(-ikf_orient.getEuler(1)[0] - reference_orient.getEuler(1)[0]) # Pitch
alignment_diff.append(-ikf_orient.getEuler(2)[0] - reference_orient.getEuler(2)[0]) # Roll

euler[0] = euler[0] - alignment_diff[0]
euler[1] = euler[1] + alignment_diff[1]
euler[2] = euler[2] - alignment_diff[2]

# Convert to degrees
euler[0][:] = [x * 180.00/math.pi for x in euler[0] ]#convert to degrees
euler[1][:] = [x * 180.00/math.pi for x in euler[1] ]#convert to degrees
euler[2][:] = [x * 180.00/math.pi for x in euler[2] ]#convert to degrees

# IMU frame is 180 rotates wrt body
euler[1] = -euler[1]
euler[2] = -euler[2]

# Check the heading to be -180, 180
for i in range(0, len(euler[0])-1):
    if euler[0][i] > 360.00:
        euler[0][i] = euler[0][i] - 360.00

    if euler[0][i] > 180.00:
        euler[0][i] = -180.00 + (euler[0][i] - 180.00)

    if euler[0][i] < -360.00:
        euler[0][i] = euler[0][i] + 360.00

    if euler[0][i] < -180.00:
        euler[0][i] = 180.00 + (180.00 + euler[0][i])


# Reduce number of points
time = time[0::50]
euler[0] = euler[0][0::50]
euler[1] = euler[1][0::50]
euler[2] = euler[2][0::50]

# IKF Filter
axis = 0
if axis == 2:
    label_text = "Roll [filter w/ Allan data]"
    color_value = [1.0,0,0]
elif axis  == 1:
    label_text = "Pitch [filter w/ Allan data]"
    color_value = [0.0,1.0,0]
else:
    label_text = "Yaw [filter w/ Allan data]"
    color_value = [0.0,0.0,1.0]

ax.plot(time, euler[axis], marker='o', linestyle='-', label=label_text, color=color_value, lw=6)
sigma = ikf_orient.getStd(axis=axis, levelconf = 2)
sigma[:] = [x * 180.00/math.pi for x in sigma]#convert to degrees
sigma = sigma[0::50]
ax.fill(np.concatenate([time, time[::-1]]),
        np.concatenate([euler[axis] - sigma,
                       (euler[axis] + sigma)[::-1]]),
        alpha=.5, fc='0.50', ec='None', label='95% confidence interval')

# Data Sheet covariance filter
time = ikf_data_sheet_coef_orient.atime
time = time - ikf_data_sheet_coef_orient.atime[0] # Time alignment
euler = []
euler.append(ikf_data_sheet_coef_orient.getEuler(0))# Yaw
euler.append(ikf_data_sheet_coef_orient.getEuler(1))# Pitch
euler.append(ikf_data_sheet_coef_orient.getEuler(2))# Roll

# Alignment with ground truth
alignment_diff = []
alignment_diff.append(ikf_data_sheet_coef_orient.getEuler(0)[0] - reference_orient.getEuler(0)[0]) # Yaw
alignment_diff.append(-ikf_data_sheet_coef_orient.getEuler(1)[0] - reference_orient.getEuler(1)[0]) # Pitch
alignment_diff.append(-ikf_data_sheet_coef_orient.getEuler(2)[0] - reference_orient.getEuler(2)[0]) # Roll

euler[0] = euler[0] - alignment_diff[0]
euler[1] = euler[1] + alignment_diff[1]
euler[2] = euler[2] - alignment_diff[2]

# Convert to degrees
euler[0][:] = [x * 180.00/math.pi for x in euler[0] ]#convert to degrees
euler[1][:] = [x * 180.00/math.pi for x in euler[1] ]#convert to degrees
euler[2][:] = [x * 180.00/math.pi for x in euler[2] ]#convert to degrees

# IMU frame is 180 rotates wrt body
euler[1] = -euler[1]
euler[2] = -euler[2]

# Check the heading to be -180, 180
for i in range(0, len(euler[0])-1):
    if euler[0][i] > 360.00:
        euler[0][i] = euler[0][i] - 360.00

    if euler[0][i] > 180.00:
        euler[0][i] = -180.00 + (euler[0][i] - 180.00)

    if euler[0][i] < -360.00:
        euler[0][i] = euler[0][i] + 360.00

    if euler[0][i] < -180.00:
        euler[0][i] = 180.00 + (180.00 + euler[0][i])


# Reduce number of points
time = time[0::50]
euler[0] = euler[0][0::50]
euler[1] = euler[1][0::50]
euler[2] = euler[2][0::50]

# IKF Filter
if axis == 2:
    label_text = "Roll [filter w/i Allan data]"
    color_value = [0.3,0.3,0.3]
elif axis  == 1:
    label_text = "Pitch [filter w/i Allan data]"
    color_value = [0.3,0.3,0.3]
else:
    label_text = "Yaw [filter w/i Allan data]"
    color_value = [0.3,0.3,0.3]

ax.plot(time, euler[axis], marker='x', linestyle='--', label=label_text, color=color_value, lw=6)


# Inflated covariance filter
time = ikf_inflated_coef_orient.atime
time = time - ikf_inflated_coef_orient.atime[0] # Time alignment
euler = []
euler.append(ikf_inflated_coef_orient.getEuler(0))# Yaw
euler.append(ikf_inflated_coef_orient.getEuler(1))# Pitch
euler.append(ikf_inflated_coef_orient.getEuler(2))# Roll

# Alignment with ground truth
alignment_diff = []
alignment_diff.append(ikf_inflated_coef_orient.getEuler(0)[0] - reference_orient.getEuler(0)[0]) # Yaw
alignment_diff.append(-ikf_inflated_coef_orient.getEuler(1)[0] - reference_orient.getEuler(1)[0]) # Pitch
alignment_diff.append(-ikf_inflated_coef_orient.getEuler(2)[0] - reference_orient.getEuler(2)[0]) # Roll

euler[0] = euler[0] - alignment_diff[0]
euler[1] = euler[1] + alignment_diff[1]
euler[2] = euler[2] - alignment_diff[2]

# Convert to degrees
euler[0][:] = [x * 180.00/math.pi for x in euler[0] ]#convert to degrees
euler[1][:] = [x * 180.00/math.pi for x in euler[1] ]#convert to degrees
euler[2][:] = [x * 180.00/math.pi for x in euler[2] ]#convert to degrees

# IMU frame is 180 rotates wrt body
euler[1] = -euler[1]
euler[2] = -euler[2]

# Check the heading to be -180, 180
for i in range(0, len(euler[0])-1):
    if euler[0][i] > 360.00:
        euler[0][i] = euler[0][i] - 360.00

    if euler[0][i] > 180.00:
        euler[0][i] = -180.00 + (euler[0][i] - 180.00)

    if euler[0][i] < -360.00:
        euler[0][i] = euler[0][i] + 360.00

    if euler[0][i] < -180.00:
        euler[0][i] = 180.00 + (180.00 + euler[0][i])


# Reduce number of points
time = time[0::50]
euler[0] = euler[0][0::50]
euler[1] = euler[1][0::50]
euler[2] = euler[2][0::50]

# IKF Filter
if axis == 2:
    label_text = "Roll [filter w/o Allan data]"
    color_value = [0,0,0]
elif axis  == 1:
    label_text = "Pitch [filter w/o Allan data]"
    color_value = [0,0,0]
else:
    label_text = "Yaw [filter w/o Allan data]"
    color_value = [0,0,0]

ax.plot(time, euler[axis], marker='x', linestyle='--', label=label_text, color=color_value, lw=6)
#sigma = ikf_inflated_coef_orient.getStd(axis=axis, levelconf = 2)
#sigma[:] = [x * 180.00/math.pi for x in sigma]#convert to degrees
#sigma = sigma[0::50]
#ax.fill(np.concatenate([time, time[::-1]]),
#        np.concatenate([euler[axis] - sigma,
#                       (euler[axis] + sigma)[::-1]]),
#        alpha=.5, fc='0.20', ec='None')

# Ground Truth
time = reference_orient.atime
time = time - ikf_orient.atime[0]# Time alignment
euler = []
euler.append(reference_orient.getEuler(0))# Yaw
euler.append(reference_orient.getEuler(1))# Pitch
euler.append(reference_orient.getEuler(2))# Roll

# Convert to degrees
euler[0][:] = [x * 180.00/math.pi for x in euler[0] ]#convert to degrees
euler[1][:] = [x * 180.00/math.pi for x in euler[1] ]#convert to degrees
euler[2][:] = [x * 180.00/math.pi for x in euler[2] ]#convert to degrees

# Reduce number of points
#time = time[0::5]
#euler[0] = euler[0][0::5]
#euler[1] = euler[1][0::5]
#euler[2] = euler[2][0::5]

if axis == 2:
    label_text = "Roll [ground truth]"
    color_value = [0.2,0.6,0.7]
elif axis  == 1:
    label_text = "Pitch [ground truth]"
    color_value = [0.2,0.6,0.7]
else:
    label_text = "Yaw [ground truth]"
    color_value = [0.2,0.6,0.7]

ax.plot(time, euler[axis], marker='D', linestyle='None', label=label_text, color=color_value, alpha=0.5, lw=6)

plt.xlabel(r'Time [$s$]')
plt.ylabel(r'Angle [${}^\circ$]')
plt.grid(True)
#plt.legend(prop={'size':25}, loc=1)
plt.show(block=False)

raw_input("Press Enter to continue...")

