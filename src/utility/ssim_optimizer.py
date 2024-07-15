import numpy as np
from scipy.ndimage import uniform_filter

def _supported_float_type(dtype):
    return np.float32 if dtype == np.float32 else np.float64

def gaussian(im, sigma=1.5, truncate=3.5, mode='reflect'):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(im, sigma=sigma, truncate=truncate, mode=mode)

def check_shape_equality(im1, im2):
    if im1.shape != im2.shape:
        raise ValueError("Input images must have the same dimensions.")

class SSIMOptimizer:
    def __init__(self, im_fixed, win_size=7, gaussian_weights=False, sigma=1.5, use_sample_covariance=True):
        self.im_fixed = im_fixed
        self.win_size = win_size
        self.gaussian_weights = gaussian_weights
        self.sigma = sigma
        self.use_sample_covariance = use_sample_covariance
        
        self.float_type = _supported_float_type(im_fixed.dtype)
        self.filter_func = gaussian if gaussian_weights else uniform_filter
        self.filter_args = {'sigma': sigma, 'truncate': 3.5, 'mode': 'reflect'} if gaussian_weights else {'size': win_size}

        self.precompute_components()

    def precompute_components(self):
        im = self.im_fixed.astype(self.float_type, copy=False)
        NP = self.win_size**im.ndim
        self.cov_norm = NP / (NP - 1) if self.use_sample_covariance else 1.0

        self.ux = self.filter_func(im, **self.filter_args)
        self.uxx = self.filter_func(im * im, **self.filter_args)
        self.vx = self.cov_norm * (self.uxx - self.ux * self.ux)

    def structural_similarity(self, im1, data_range=None, K1=0.01, K2=0.03):
        check_shape_equality(im1, self.im_fixed)
        im1 = im1.astype(self.float_type, copy=False)
        im2 = self.im_fixed

        uy = self.ux
        vy = self.vx

        uxy = self.filter_func(im1 * im2, **self.filter_args)
        ux = self.filter_func(im1, **self.filter_args)
        uxx = self.filter_func(im1 * im1, **self.filter_args)
        vx = self.cov_norm * (uxx - ux * ux)
        vxy = self.cov_norm * (uxy - ux * uy)

        R = data_range
        C1 = (K1 * R) ** 2
        C2 = (K2 * R) ** 2

        A1 = 2 * ux * uy + C1
        A2 = 2 * vxy + C2
        B1 = ux**2 + uy**2 + C1
        B2 = vx + vy + C2
        S = (A1 * A2) / (B1 * B2)

        mssim = S.mean(dtype=np.float64)

        return mssim