import numpy as np

def apply_windowing(img, min_bound=-1000, max_bound=400):
    """
    Filtra a imagem para focar apenas na faixa de interesse (Janelamento).
    Padrão LUNA16 (Pulmão): -1000 a 400 HU.
    """
    img_windowed = img.copy()
    img_windowed[img_windowed < min_bound] = min_bound
    img_windowed[img_windowed > max_bound] = max_bound
    return img_windowed

def apply_fol(data_array, base=1.05, bias=50, windowing=True):
    """
    Aplica FoL e converte para uint8 para economia máxima de espaço.
    """
    # 1. Janelamento (Crucial para CT Scans)
    if windowing:
        data_array = apply_windowing(data_array)
        
    min_val = np.min(data_array)
    data_shifted = data_array - min_val 
    
    img_safe = np.maximum(data_shifted + bias, 1e-10)
    transformed = np.floor(np.log(img_safe) / np.log(base))
    
    transformed = transformed.astype(np.int32)
    
    return transformed