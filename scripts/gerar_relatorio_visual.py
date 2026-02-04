import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use('Agg')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from io_adapters.loader_factory import load_dataset_file

# --- CONFIGURAÇÃO DO FILTRO ---
FILTRO_DATASET = "paisagens" 
# ------------------------------

def gerar_todas_imagens():
    pasta_saida = "resultados_visuais"
    arquivo_csv = "resultado_final_metricas.csv"
    
    if not os.path.exists(pasta_saida): os.makedirs(pasta_saida)
    if not os.path.exists(arquivo_csv): return

    print(f"Lendo CSV: {arquivo_csv} com filtro='{FILTRO_DATASET}'")
    try:
        df = pd.read_csv(arquivo_csv, sep=';')
    except:
        print("Erro ao ler CSV. Verifique o separador.")
        return
    
    if FILTRO_DATASET:
        df = df[df['Dataset'] == FILTRO_DATASET]
    
    total = len(df)
    print(f"Gerando {total} imagens com MATEMÁTICA PURA...")

    for index, row in df.iterrows():
        try:
            nome_arquivo = row['Arquivo']
            dataset = row['Dataset']
            base_ideal = row['Base Usada']
            econ = row['Economia (%)']
            
            caminho_completo = os.path.join("datasets", dataset, nome_arquivo)
            if not os.path.exists(caminho_completo): continue

            dados = load_dataset_file(caminho_completo)
            if dados is None or dados.ndim < 2: continue 

            dados = dados.astype(np.float64)
            p_max = np.max(dados)
            if p_max <= 1.0:
                dados = dados * 255.0

            p_min = np.min(dados)
            eh_medico = (p_min < -100)

            
            if eh_medico:
                # Lógica LUNA16 (Mantida)
                vmin, vmax = -1000, 400
                offset = 1 - p_min
                dados_offset = dados + offset
                indices = np.floor(np.log(dados_offset) / np.log(base_ideal))
                reconstruido = np.exp(indices * np.log(base_ideal)) - offset
                
                visual_orig = dados
                visual_fol = reconstruido
            else:

                vmin, vmax = 0, 255
                
                indices = np.floor(np.log(dados + 1) / np.log(base_ideal))
                
                reconstruido = np.power(base_ideal, indices)
                
                visual_orig = np.clip(dados, 0, 255).astype(np.uint8)
                visual_fol = np.clip(reconstruido, 0, 255).astype(np.uint8)

            fig, ax = plt.subplots(1, 3, figsize=(15, 6))
            
            # Original
            ax[0].imshow(visual_orig, cmap='gray', vmin=vmin, vmax=vmax)
            ax[0].set_title("Original")
            ax[0].axis('off')
            
            # FoL Reconstruído
            ax[1].imshow(visual_fol, cmap='gray', vmin=vmin, vmax=vmax)
            ax[1].set_title(f"FoL Reconstruído\nBase {base_ideal:.3f}")
            ax[1].axis('off')
            
            # Diferença (Mapa de Erro)
            # Calcula diferença normalizada (0.0 a 1.0)
            orig_norm = visual_orig.astype(float)
            fol_norm = visual_fol.astype(float)
            
            # Ajuste de escala para o mapa de erro aparecer bem
            if eh_medico:
                div = 1400 
            else:
                div = 255.0 
                
            diff = np.abs(orig_norm - fol_norm) / div
            
            im_diff = ax[2].imshow(diff, cmap='inferno', vmin=0, vmax=0.1)
            ax[2].set_title(f"Mapa de Erro (Escala 10%)\nEcon: {econ:.1f}%")
            ax[2].axis('off')
            
            plt.colorbar(im_diff, ax=ax[2], fraction=0.046, pad=0.04)

            nome_limpo = os.path.splitext(nome_arquivo)[0]
            nome_saida = f"{dataset}_{nome_limpo}.png"
            plt.tight_layout()
            plt.savefig(os.path.join(pasta_saida, nome_saida), dpi=100)
            plt.close(fig)

            print(f"[{index+1}/{total}] Salvo: {nome_saida}")

        except Exception as e:
            print(f"Erro em {row.get('Arquivo')}: {e}")

if __name__ == "__main__":
    gerar_todas_imagens()