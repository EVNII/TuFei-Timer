from src.utility.get_correct_file_path import get_correct_file_path

import numpy as np
import ctypes

ssim_dll_path = get_correct_file_path('bin/')

dll = np.ctypeslib.load_library('ssim.dll', ssim_dll_path)

def get_function(res_type='float', func_name='PSNR_Byte', arg_types=['Byte*', 'int', 'int', 'int', 'Byte*']):
    type_dict = {'int':ctypes.c_int, 'float':ctypes.c_float, 'double':ctypes.c_double, 'void':None,
                'int32':ctypes.c_int32, 'uint32':ctypes.c_uint32, 'int16':ctypes.c_int16, 'uint16':ctypes.c_uint16,
                'int8':ctypes.c_int8, 'uint8':ctypes.c_uint8, 'byte':ctypes.c_uint8,
                'char*':ctypes.c_char_p,
                'float*':np.ctypeslib.ndpointer(dtype='float32', ndim=1, flags='CONTIGUOUS'),
                'int*':np.ctypeslib.ndpointer(dtype='int32', ndim=1, flags='CONTIGUOUS'),
                'byte*':np.ctypeslib.ndpointer(dtype='uint8', ndim=1, flags='CONTIGUOUS')}

    func = dll.__getattr__(func_name)
    func.restype = type_dict[res_type]
    func.argtypes = [type_dict[str.lower(x).replace(' ', '')] for x in arg_types]
    return func

# float PSNR_Byte(Byte* pDataX, Byte* pDataY, int step, int width, int height, int maxVal);
PSNR_Byte = get_function('float', 'PSNR_Byte', ['Byte*', 'Byte*', 'int', 'int', 'int', 'int'])

# float PSNR_Float(float* pDataX, float* pDataY, int step, int width, int height, double maxVal);
PSNR_Float = get_function('float', 'PSNR_Float', ['float*', 'float*', 'int', 'int', 'int', 'double'])

# float SSIM_Byte(Byte* pDataX, Byte* pDataY, int step, int width, int height, int win_size, int maxVal);
SSIM_Byte = get_function('float', 'SSIM_Byte', ['Byte*', 'Byte*', 'int', 'int', 'int', 'int', 'int'])

# float SSIM_Float(float* pDataX, float* pDataY, int step, int width, int height, int win_size, double maxVal);
SSIM_Float = get_function('float', 'SSIM_Float', ['float*', 'float*', 'int', 'int', 'int', 'int', 'double'])

def SSIM(x, y, max_value=None, win_size=7):
    [h,w,c] = x.shape
    x = x.astype('float32') if(x.dtype=='float64') else x
    y = y.astype('float32') if(y.dtype=='float64') else y
    if(x.dtype=='uint8' and y.dtype=='uint8'):
        return SSIM_Byte(x.reshape([-1]), y.reshape([-1]), w*c, w, h, win_size, 255 if(max_value==None) else int(max_value))
    if(x.dtype=='float32' and y.dtype=='float32'):
        return SSIM_Float(x.reshape([-1]), y.reshape([-1]), w*c, w, h, win_size, 255.0 if(max_value==None) else float(max_value))
    raise RuntimeError("NO DLL loaded")
    #return skimage.measure.compare_ssim(x,y, win_size=win_size, data_range=max_value, multichannel=(x.ndim>2))