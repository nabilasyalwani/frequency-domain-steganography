from datetime import datetime
from PIL import Image
from collections import defaultdict
from matplotlib.pylab import ceil, floor, round
import os
import cv2
import math
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns

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

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) *
                                                            (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()

def fsi(cover_path, stego_path):
    size_cover = os.path.getsize(cover_path)
    size_stego = os.path.getsize(stego_path)
    print(f"Size cover: {size_cover}")
    print(f"Size stego: {size_stego}")
    fsi_res = ((size_stego - size_cover) / size_cover) 
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

    mse = np.mean((cover_arr - stego_arr) ** 2)

    if mse == 0:
        return float('inf')  # Gambar identik, PSNR tak terhingga

    max_pixel = 255.0
    psnr_value = 20 * math.log10(max_pixel / math.sqrt(mse))

    return psnr_value