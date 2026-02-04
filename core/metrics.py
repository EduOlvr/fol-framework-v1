import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.spatial.distance import directed_hausdorff

def calcular_metricas(img_orig, img_rec, dataset_type="generic"):
    """
    Calcula métricas específicas baseadas no tipo de dataset.
    
    Args:
        img_orig, img_rec: Arrays numpy.
        dataset_type (str): 'medico', 'visual' (rosto/paisagem) ou 'sinal'.
    """
    resultados = {}
    
    # --- 1. PRÉ-PROCESSAMENTO PARA SSIM (A CORREÇÃO DO 0.60) ---
    # O SSIM exige que ambas as imagens sejam EXATAMENTE do mesmo tipo e escala.
    # Vamos forçar tudo para uint8 (0-255) que é o padrão visual.
    
    # Normaliza e converte Original
    if img_orig.dtype != np.uint8:
        orig_norm = (img_orig - np.min(img_orig))
        if np.max(orig_norm) > 0:
            orig_norm = (orig_norm / np.max(orig_norm)) * 255.0
        img1 = orig_norm.astype(np.uint8)
    else:
        img1 = img_orig

    # Normaliza e converte Reconstruída
    if img_rec.dtype != np.uint8:
        rec_norm = (img_rec - np.min(img_rec))
        if np.max(rec_norm) > 0:
            rec_norm = (rec_norm / np.max(rec_norm)) * 255.0
        img2 = rec_norm.astype(np.uint8)
    else:
        img2 = img_rec

    # --- 2. MÉTRICAS VISUAIS (SSIM / PSNR) ---
    # Aplicar em: Rostos, Paisagens e Médico (como complementar)
    if dataset_type in ["visual", "medico"]:
        try:
            # win_size=7 é o padrão. data_range=255 é CRÍTICO para uint8.
            val_ssim = ssim(img1, img2, data_range=255, win_size=7)
            resultados['ssim'] = val_ssim
            
            val_psnr = psnr(img1, img2, data_range=255)
            resultados['psnr'] = val_psnr
        except Exception as e:
            print(f"Erro SSIM: {e}")
            resultados['ssim'] = 0.0
            resultados['psnr'] = 0.0

    # --- 3. MÉTRICAS DA TESE (SEGMENTAÇÃO) ---
    # Aplicar APENAS em: LUNA16 (Médico)
    # Motivo: Dice mede sobreposição de máscara. Não faz sentido em foto de rosto.
    if dataset_type == "medico":
        # Binarização (Simulação de máscara para manter compatibilidade com a tese)
        limiar = 127
        bin_orig = (img1 > limiar)
        bin_rec = (img2 > limiar)
        
        vp = np.sum(bin_orig & bin_rec)
        fp = np.sum(~bin_orig & bin_rec)
        fn = np.sum(bin_orig & ~bin_rec)
        
        # Dice
        denom = (2 * vp + fp + fn)
        resultados['dice'] = (2 * vp) / denom if denom > 0 else 0.0
        
        # Hausdorff
        if np.any(bin_orig) and np.any(bin_rec):
            try:
                d1 = directed_hausdorff(bin_orig, bin_rec)[0]
                resultados['hausdorff'] = d1
            except:
                resultados['hausdorff'] = 0.0
        else:
            resultados['hausdorff'] = 0.0

    return resultados