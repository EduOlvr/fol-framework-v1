import os
import argparse
import time
import pandas as pd
import numpy as np 
from core.transform import apply_fol
from core.descriptors import apply_lbp_2d

# --- IMPORTAÇÃO DAS MÉTRICAS ---
try:
    from core.metrics import calcular_metricas
except ImportError:
    print("[AVISO] core.metrics não encontrado. As métricas serão zeradas.")
    # Atualizado para aceitar qualquer parâmetro (dataset_type, etc)
    def calcular_metricas(orig, rec, **kwargs): return {}
# -------------------------------

try:
    from core.optimizer import encontrar_base_ideal
except ImportError:
    pass

from io_adapters.loader_factory import load_dataset_file
from io_adapters.minio_connector import StorageService

def run_pipeline(root_folder, target_dataset=None, use_lbp=False, base_padrao=1.05, auto_mode=False):
    modo_str = "AUTOMÁTICO" if auto_mode else f"FIXO (Base {base_padrao})"
    print(f"--- INICIANDO PROCESSAMENTO CIENTÍFICO ---")
    print(f"--- MODO: {modo_str} ---")
    
    relatorio_geral = [] 
    
    if target_dataset:
        start_dir = os.path.join(root_folder, target_dataset)
    else:
        start_dir = root_folder
    
    if not os.path.exists(start_dir):
        print(f"[ERRO] Pasta não encontrada: {start_dir}")
        return

    storage = StorageService()
    
    arquivos = []
    for root, dirs, filenames in os.walk(start_dir):
        for f in filenames:
            if f.lower().endswith(('.raw', '.npz', '.mhd', '.jpg', '.jpeg', '.png')) and not f.startswith('.'):
                arquivos.append(os.path.join(root, f))
    
    print(f"Total de arquivos encontrados: {len(arquivos)}")

    for i, filepath in enumerate(arquivos):
        try:
            nome_arquivo = os.path.basename(filepath)
            caminho_relativo = os.path.relpath(filepath, root_folder)
            nome_base = os.path.splitext(caminho_relativo)[0].replace(os.sep, '/')
            
            dados_brutos = load_dataset_file(filepath)
            if dados_brutos is None or dados_brutos.size == 0: continue
            
            eh_imagem = (dados_brutos.ndim >= 2)
            
            # Detecta se é Médico (Valores negativos como -1000)
            p_min = np.min(dados_brutos)
            eh_medico = (p_min < -100) 

            dados_entrada = dados_brutos.astype(np.float64)
            
            if use_lbp and eh_imagem:
                lbp = apply_lbp_2d(dados_brutos)
                dados_entrada = dados_entrada + lbp
                
            # --- DECISÃO DA BASE ---
            base_atual = base_padrao
            
            if auto_mode and eh_imagem:
                print(f"[{i+1}/{len(arquivos)}] Otimizando base para {nome_arquivo}...")
                try:
                    base_calculada, _ = encontrar_base_ideal(dados_entrada, bias=50) 
                    base_atual = base_calculada
                except Exception:
                    pass
            else:
                print(f"[{i+1}/{len(arquivos)}] Processando {nome_arquivo} (Médico={eh_medico}) com base {base_atual}...")
            
            # --- APLICAÇÃO DO FOL ---
            inicio = time.time()
            dados_fol = apply_fol(dados_entrada, base=base_atual, windowing=eh_medico)
            tempo = time.time() - inicio
            
            # --- OTIMIZAÇÃO DE ARMAZENAMENTO ---
            if eh_medico:
                dados_fol_storage = dados_fol.astype(np.int16)
            else:
                max_cluster = np.max(dados_fol)
                if max_cluster < 256:
                    dados_fol_storage = dados_fol.astype(np.uint8) 
                elif max_cluster < 65536:
                    dados_fol_storage = dados_fol.astype(np.uint16)
                else:
                    dados_fol_storage = dados_fol 

            # --- CÁLCULO DE MÉTRICAS ---
            # 1. Reconstrói a imagem (simulação)
            if eh_medico:
                dados_rec = dados_fol 
            else:
                dados_rec = np.power(base_atual, dados_fol)

            # 2. Define o tipo para selecionar as métricas corretas
            if eh_medico:
                tipo_dataset = "medico"
            else:
                tipo_dataset = "visual"

            # 3. Chama a função com o novo parâmetro
            resultados_metricas = calcular_metricas(dados_entrada, dados_rec, dataset_type=tipo_dataset)
            # ---------------------------

            # --- UPLOAD ---
            path_orig = f"raw/{nome_base}.npz"
            path_proc = f"processed/{nome_base}_fol.npz"
            
            tam_orig = storage.upload_data(path_orig, dados_brutos)
            tam_fol = storage.upload_data(path_proc, dados_fol_storage)
            
            # --- RELATÓRIO INDIVIDUAL ---
            if tam_orig > 0:
                economia = 100 - (tam_fol / tam_orig * 100)
                cluster_log = int(np.max(dados_fol)) if not eh_medico else "N/A"

                linha_registro = {
                    'Arquivo': nome_arquivo,
                    'Dataset': os.path.basename(os.path.dirname(filepath)),
                    'Base Usada': round(base_atual, 4),
                    'Tamanho Original (KB)': round(tam_orig/1024, 2),
                    'Tamanho FoL (KB)': round(tam_fol/1024, 2),
                    'Economia (%)': round(economia, 2),
                    'Tempo (s)': round(tempo, 4),
                    'Clusters Max': cluster_log,
                    **resultados_metricas 
                }
                relatorio_geral.append(linha_registro)
                
                # Exibe SSIM no terminal se disponível
                ssim_str = f" | SSIM: {resultados_metricas.get('ssim', 0):.4f}" if 'ssim' in resultados_metricas else ""
                print(f"   -> Base: {base_atual:.3f} | Econ: {economia:.1f}%{ssim_str}")

        except Exception as e:
            print(f"[ERRO] Falha ao processar {filepath}: {e}")

    # --- RELATÓRIO FINAL CONSOLIDADO ---
    if relatorio_geral:
        df = pd.DataFrame(relatorio_geral)
        nome_csv = "resultado_final_metricas.csv"
        
        # 1. Organização das colunas (Prioridade visual no CSV)
        colunas_ordem = [
            'Arquivo', 'Dataset', 'Base Usada', 'Economia (%)', 
            'ssim', 'psnr', 'dice', 'hausdorff', 'mcc', 'accuracy', 'sensitivity',
            'Clusters Max', 'Tamanho Original (KB)', 'Tamanho FoL (KB)', 'Tempo (s)'
        ]
        
        todas_colunas = colunas_ordem + [c for c in df.columns if c not in colunas_ordem]
        cols_to_save = [c for c in todas_colunas if c in df.columns]
        
        df = df[cols_to_save]
        df.to_csv(nome_csv, index=False, sep=';')
        
        print("\n" + "="*50)
        print(f"RELATÓRIO FINAL CONSOLIDADO")
        print(f"Arquivo salvo: {nome_csv}")
        print("-" * 50)
        
        # 2. Imprime a média de TODAS as métricas numéricas relevantes encontradas
        metricas_para_media = [
            'Economia (%)', 'ssim', 'psnr', 'dice', 'jaccard', 
            'mcc', 'sensitivity', 'accuracy', 'hausdorff'
        ]
        
        for metrica in metricas_para_media:
            if metrica in df.columns:
                valor_medio = df[metrica].mean()
                # Mostra no terminal
                print(f"Média de {metrica:<15}: {valor_medio:.4f}")
                
        print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--only")
    parser.add_argument("--lbp", action="store_true")
    parser.add_argument("--base", type=float, default=1.05)
    parser.add_argument("--auto", action="store_true")
    
    args = parser.parse_args()
    
    run_pipeline(args.root, args.only, args.lbp, args.base, args.auto)