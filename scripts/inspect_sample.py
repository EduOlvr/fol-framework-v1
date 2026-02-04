import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io_adapters.loader_factory import load_dataset_file
# Não importamos apply_fol aqui para poder simular manualmente sem limite de 255

def inspecionar_arquivo(caminho_arquivo, base=1.05):
    print(f"--- INSPECIONANDO (SIMULAÇÃO 16-BIT): {os.path.basename(caminho_arquivo)} ---")
    
    if not os.path.exists(caminho_arquivo):
        print(f"[ERRO] Arquivo não existe: {caminho_arquivo}")
        return

    dados = load_dataset_file(caminho_arquivo)
    if dados is None: return

    dados = dados.astype(np.float64)

    # Detecta tipo e ajusta escala visual
    if dados.ndim == 1 or (dados.ndim == 2 and dados.shape[1] == 1):
        eh_imagem = False
        dados = np.squeeze(dados)
    else:
        eh_imagem = True
        
    p_min = np.min(dados)
    eh_medico = (p_min < -100)

    if eh_imagem:
        if eh_medico:
            print("[TIPO] Médico (LUNA16) - Usando Janela -1000 a 400")
            vmin, vmax = -1000, 400
            cmap = 'gray'
            dados_offset = dados - p_min + 1
            indices = np.floor(np.log(dados_offset) / np.log(base)).astype(np.float64)
            dados_fol_reconstruido = np.exp(indices * np.log(base)) + p_min - 1
            
            visual_orig = dados
            visual_fol = dados_fol_reconstruido
            
        else:
            print(f"[TIPO] Paisagem - Modo High Fidelity (Bypassing 8-bit limit)")
            vmin, vmax = 0, 255
            cmap = 'gray'
            
            indices_reais = np.floor(np.log(dados + 1) / np.log(base))
            
            max_cluster = np.max(indices_reais)
            print(f"[INFO] Cluster Máximo Gerado: {int(max_cluster)}")
            if max_cluster > 255:
                print(f"       -> ATENÇÃO: Isso exigiria uint16 (ocupa o dobro do espaço).")
                print(f"       -> O sistema original (uint8) tela preta aqui.")
                print(f"       -> Esta visualização mostra o potencial teórico.")

            dados_fol_reconstruido = np.power(base, indices_reais)
        
            visual_orig = np.clip(dados, 0, 255).astype(np.uint8)
            visual_fol = np.clip(dados_fol_reconstruido, 0, 255).astype(np.uint8)

    unique_orig = len(np.unique(dados))
    unique_fol = len(np.unique(indices_reais)) if eh_imagem else 0
    
    if eh_imagem:
        plt.figure(figsize=(15, 6))
        
        plt.subplot(1, 3, 1)
        plt.imshow(visual_orig, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.title("Original")
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(visual_fol, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.title(f"FoL High Fidelity (Base {base})\n{unique_fol} Clusters (Simulado 16-bit)")
        plt.axis('off')

        plt.subplot(1, 3, 3)
        orig_f = visual_orig.astype(float) / 255.0
        fol_f = visual_fol.astype(float) / 255.0
        diff = np.abs(orig_f - fol_f)
        
        plt.imshow(diff, cmap='inferno', vmin=0, vmax=0.05) 
        plt.title("Mapa de Erro (Escala 0-5%)")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", help="Caminho do arquivo")
    parser.add_argument("--lbp", action="store_true")
    parser.add_argument("--base", type=float, default=1.05)
    args = parser.parse_args()
    
    inspecionar_arquivo(args.arquivo, base=args.base)