#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version 1.1 12/28/2017
Caleb M. Hill
Department of Chemistry
University of Wyoming
caleb.hill@uwyo.edu

This program was designed for the purpose of analyzing electrochemical microscopy data acquired in the Hill Lab at the University of Wyoming. This encompasses two specific tasks:
-Construction of current "movies" depicting spatial variations in voltammetric behavior across a sample
-GUI-assisted generation of voltammograms corresponding to specific points

The data is expected in the form of a 2D array, with Nt points in the first dimension (corresponding to different points in time) and Nx*Ny+1 points in the second dimension, corresponding to different spatial pixels. The first column is expected to hold the potentials corresponding to each point in time. The software expects current values in A, and potentials in V.
"""

import tkinter as tk
from tkinter import filedialog
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colorbar as cb
import matplotlib as mpl
from matplotlib import gridspec
import pandas as pd
from tifffile import imsave
		
#Get file path via GUI
root = tk.Tk()
root.withdraw()
filePath = filedialog.askopenfilename()
	
#Import data
rawData = pd.read_csv(filePath,dtype=sp.float64,sep='\t').as_matrix()
Nt = int(rawData.shape[0])
N = rawData.shape[1] - 1
Nx = int(input("What's the image width (in pixels)?"))
Ny = int(N/Nx)
print(Nx,Ny)

#Create array with potential values				
E = rawData[:,0]

#Format data cube. Note that this takes into account the alternating raster pattern of the SECCM instrument.                
dataCube = sp.zeros((Ny,Nx,Nt),dtype=sp.float64)
datamin = sp.inf
datamax = -sp.inf
for nx in range(Nx):
	for ny in range(Ny):
		for nz in range(Nt):
			datapoint = rawData[nz,nx+ny*Nx+1]
			if ny % 2 == 0:
				dataCube[ny,nx,nz] = datapoint
			else:
				dataCube[ny,-(nx+1),nz] = datapoint
			if nz >= 100:
				if datapoint < datamin:
					datamin = datapoint
				if datapoint > datamax:
					datamax = datapoint

#Generate movie if desired.
choice = input("Would you like a movie? (y/n)")
if choice == 'y':
	print('Movie is being prepared... Be patient...')
	fig = plt.figure()
	gs = gridspec.GridSpec(1,2,width_ratios=[10,1])
	ax1 = fig.add_subplot(gs[0])
	ax2 = fig.add_subplot(gs[1])

	norm = mpl.colors.Normalize(vmin=datamin, vmax=datamax)
	imagecb = cb.ColorbarBase(ax2,norm=norm,format='%.0e')
	imagecb.ax.set_title('i / A')

	ims = []
	textx = 0.05*Nx
	texty = 0.95*Ny
	for n in range(100,Nt):
		frame = dataCube[:,:,n]
		im = ax1.imshow(frame,norm=norm,interpolation='none',origin='lower')
		tx = ax1.text(textx,texty, 'E = ' + '{0:.3f}'.format(E[n]) + ' V',color='w',family='sans-serif',size=24, va='top',ha='left',weight='bold')
		ims.append([im,tx])
		
	ani = animation.ArtistAnimation(fig, ims, interval=10, repeat=False)

	path = filePath + '_curr_Movie.mp4'
	ani.save(path,bitrate=20000)

	plt.show()
			
#GUI-triggered functions to output cv of a single region
ncv = 1
def exportCV(x,y):
	global ncv
	curr = dataCube[y,x,:]
	cv = sp.stack((E,curr),axis=-1)
	path = filePath + '_' + str(ncv) + '_x' + str(x) + '_y' + str(y) + '.txt'
	sp.savetxt(path,cv,delimiter='\t')
	ncv += 1
	
def onclick(event):
	x = int(round(event.xdata))
	y = int(round(event.ydata))
	exportCV(x,y)
	print(x, y)

fig, current_ax = plt.subplots()  		
totalCurr = sp.sum(dataCube,axis=2)
totCurrPlot = plt.imshow(totalCurr,interpolation='none',origin='lower')
plt.connect('button_press_event', onclick)
plt.show()