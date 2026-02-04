from skimage.feature import local_binary_pattern
import numpy as np

def apply_lbp_2d(img_array, radius=1):
    """
    Aplica LBP apenas se for uma imagem 2D.
    """
    if img_array.ndim != 2:
        return np.zeros_like(img_array)
        
    points = 8 * radius
    # method='uniform' é o padrão da literatura médica
    return local_binary_pattern(img_array, points, radius, method='uniform')