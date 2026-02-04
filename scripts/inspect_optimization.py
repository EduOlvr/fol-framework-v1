import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.optimizer import encontrar_base_ideal
from io_adapters.loader_factory import load_dataset_file
from core.descriptors import apply_lbp_2d

def visualizar_curva_otimizacao(caminho_arquivo, usar_lbp=False):
    print(f"--- ANALISANDO OTIMIZAÇÃO: {os.path.basename(caminho_arquivo)} ---")
    
    img_original = load_dataset_file(caminho_arquivo)
    if img_original is None: return

    # 2. Pré-processamento (LBP se necessário)
    dados_entrada = img_original
    if usar_lbp and img_original.ndim == 2:
        print("[INFO] Aplicando LBP antes da otimização...")
        lbp = apply_lbp_2d(img_original)
        dados_entrada = img_original + lbp

    melhor_base, (eixo_x_bases, eixo_y_clusters) = encontrar_base_ideal(dados_entrada, bias=50)
    
    clusters_escolhidos = eixo_y_clusters[np.where(eixo_x_bases == melhor_base)[0][0]]

    print(f"Base Escolhida: {melhor_base:.4f}")
    print(f"Clusters Resultantes: {clusters_escolhidos}")

    plt.figure(figsize=(10, 6))
    
    plt.plot(eixo_x_bases, eixo_y_clusters, marker='o', linestyle='-', color='b', label='Curva de Compressão')
    
    plt.plot(melhor_base, clusters_escolhidos, marker='o', markersize=12, color='red', label=f'Base Otimizada ({melhor_base:.3f})')
    
    plt.axvline(x=melhor_base, color='red', linestyle='--', alpha=0.5)
    plt.axhline(y=clusters_escolhidos, color='red', linestyle='--', alpha=0.5)

    plt.title(f"Método do Cotovelo (Kneedle Algorithm)\nArquivo: {os.path.basename(caminho_arquivo)}")
    plt.xlabel("Valor da Base (Log)")
    plt.ylabel("Número de Clusters (Cores)")
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    plt.legend()
  
    plt.text(melhor_base + 0.02, clusters_escolhidos + 5, 
             f"Ponto Ideal\n(Equilíbrio)", color='red', fontweight='bold')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizador da Curva de Otimização")
    parser.add_argument("arquivo", help="Caminho do arquivo")
    parser.add_argument("--lbp", action="store_true", help="Ativar LBP")
    
    args = parser.parse_args()
    
    visualizar_curva_otimizacao(args.arquivo, args.lbp)