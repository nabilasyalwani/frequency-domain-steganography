from datetime import datetime
from PIL import Image
from collections import defaultdict
from matplotlib.pylab import ceil, floor, round
from scipy import signal
from scipy import ndimage
import os
import cv2
import math
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import gauss

def ssim(cover_path, stego_path):
    cover = Image.open(cover_path).convert('L')
    stego = Image.open(stego_path).convert('L')

    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2

    cover_arr = np.array(cover, dtype=np.float64)
    stego_arr = np.array(stego, dtype=np.float64)
    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())

    mu1 = cv2.filter2D(cover_arr, -1, window)[5:-5, 5:-5]  # valid
    mu2 = cv2.filter2D(stego_arr, -1, window)[5:-5, 5:-5]
    mu1_sq = mu1**2
    mu2_sq = mu2**2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.filter2D(cover_arr**2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(stego_arr**2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(cover_arr * stego_arr, -1, window)[5:-5, 5:-5] - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()

def ssim_2(img1, img2, cs_map=False):
    """Return the Structural Similarity Map corresponding to input images img1 
    and img2 (images are assumed to be uint8)
    
    This function attempts to mimic precisely the functionality of ssim.m a 
    MATLAB provided by the author's of SSIM
    https://ece.uwaterloo.ca/~z70wang/research/ssim/ssim_index.m
    """
    img1 = Image.open(img1).convert('L')
    img2 = Image.open(img2).convert('L')
    img1_arr = np.array(img1, dtype=np.float64)
    img2_arr = np.array(img2, dtype=np.float64)
    size = 11
    sigma = 1.5
    window = gauss.fspecial_gauss(size, sigma)
    K1 = 0.01
    K2 = 0.03
    L = 255 #bitdepth of image
    C1 = (K1*L)**2
    C2 = (K2*L)**2
    mu1 = signal.fftconvolve(window, img1_arr, mode='valid')
    mu2 = signal.fftconvolve(window, img2_arr, mode='valid')
    mu1_sq = mu1*mu1
    mu2_sq = mu2*mu2
    mu1_mu2 = mu1*mu2
    sigma1_sq = signal.fftconvolve(window, img1_arr*img1_arr, mode='valid') - mu1_sq
    sigma2_sq = signal.fftconvolve(window, img2_arr*img2_arr, mode='valid') - mu2_sq
    sigma12 = signal.fftconvolve(window, img1_arr*img2_arr, mode='valid') - mu1_mu2
    if cs_map:
        return (((2*mu1_mu2 + C1)*(2*sigma12 + C2))/((mu1_sq + mu2_sq + C1)*
                    (sigma1_sq + sigma2_sq + C2)), 
                (2.0*sigma12 + C2)/(sigma1_sq + sigma2_sq + C2))
    else:
        return ((2*mu1_mu2 + C1)*(2*sigma12 + C2))/((mu1_sq + mu2_sq + C1)*
                    (sigma1_sq + sigma2_sq + C2))

def msssim(img1, img2):
    """This function implements Multi-Scale Structural Similarity (MSSSIM) Image 
    Quality Assessment according to Z. Wang's "Multi-scale structural similarity 
    for image quality assessment" Invited Paper, IEEE Asilomar Conference on 
    Signals, Systems and Computers, Nov. 2003 
    
    Author's MATLAB implementation:-
    http://www.cns.nyu.edu/~lcv/ssim/msssim.zip
    """
    level = 5
    weight = np.array([0.0448, 0.2856, 0.3001, 0.2363, 0.1333])
    downsample_filter = np.ones((2, 2))/4.0
    im1 = img1.astype(np.float64)
    im2 = img2.astype(np.float64)
    mssim = np.array([])
    mcs = np.array([])
    for l in range(level):
        ssim_map, cs_map = ssim_2(img1, img2, cs_map=True)
        mssim = np.append(mssim, ssim_map.mean())
        mcs = np.append(mcs, cs_map.mean())
        filtered_im1 = ndimage.filters.convolve(im1, downsample_filter, 
                                                mode='reflect')
        filtered_im2 = ndimage.filters.convolve(im2, downsample_filter, 
                                                mode='reflect')
        im1 = filtered_im1[::2, ::2]
        im2 = filtered_im2[::2, ::2]
    return (np.prod(mcs[0:level-1]**weight[0:level-1])*
                    (mssim[level-1]**weight[level-1]))

def fsi(cover_path, stego_path):
    size_cover = os.path.getsize(cover_path)
    size_stego = os.path.getsize(stego_path)
    print(f"Size cover: {size_cover}")
    print(f"Size stego: {size_stego}")
    fsi_res = (size_stego - size_cover) 
    return np.float64(fsi_res)

def psnr(cover_path, stego_path):
    """
    Menghitung nilai PSNR antara cover image dan stego image.
    Input:
        cover_path : path ke cover image (TIFF, PNG, dll)
        stego_path : path ke stego image
    Output:
        psnr_value : nilai PSNR dalam dB
    """

    cover = Image.open(cover_path).convert('L')
    stego = Image.open(stego_path).convert('L')

    cover_arr = np.array(cover, dtype=np.float64)
    stego_arr = np.array(stego, dtype=np.float64)

    if cover_arr.shape != stego_arr.shape:
        raise ValueError("Ukuran cover dan stego image tidak sama!")

    mse = np.mean(np.abs(cover_arr - stego_arr) ** 2)

    if mse == 0:
        return float('inf')  # Gambar identik, PSNR tak terhingga

    max_pixel = 255.0
    psnr_value = 20 * math.log10(max_pixel / math.sqrt(mse))

    return psnr_value