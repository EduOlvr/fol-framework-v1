import numpy as np
from core.transform import apply_fol

def encontrar_base_ideal(img_original, bias=50):
    """
    Versão 2.0: Alta Precisão (Fine-Tuning)
    Testa 100 bases para capturar nuances sutis entre imagens.
    """
    bases_teste = np.linspace(1.01, 3.0, 100) 
    
    num_clusters = []
    
    amostra = img_original if img_original.ndim == 2 else img_original[img_original.shape[0]//2]
    
    for b in bases_teste:
        res = apply_fol(amostra, base=b, bias=bias)
        n_unique = len(np.unique(res))
        num_clusters.append(n_unique)
    
    # 3. Matemática do Cotovelo (Kneedle)
    x = np.arange(len(bases_teste))
    y = np.array(num_clusters)
    
    # Se a curva for reta (ex: imagem preta), retorna base padrão
    if y.max() == y.min():
        return 1.05, (bases_teste, num_clusters)

    x_norm = (x - x.min()) / (x.max() - x.min())
    y_norm = (y - y.min()) / (y.max() - y.min())
    
    vetor_reta = np.array([1, y_norm[-1] - y_norm[0]])
    vetor_reta = vetor_reta / np.linalg.norm(vetor_reta)
    
    vec_pontos = np.vstack((x_norm, y_norm - y_norm[0])).T
    distancias = np.abs(np.cross(vec_pontos, vetor_reta))
    
    idx_ideal = np.argmax(distancias)
    best_base = bases_teste[idx_ideal]
    
    return best_base, (bases_teste, num_clusters)