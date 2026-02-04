import pandas as pd
import os

def analisar_resultados():
    arquivo_csv = "resultado_final_metricas.csv"
    
    if not os.path.exists(arquivo_csv):
        print("ERRO: Arquivo 'resultado_final_metricas.csv' não encontrado.")
        return

    df = pd.read_csv(arquivo_csv, sep=';')

    print("="*50)
    print("RESUMO ESTATÍSTICO DO DATASET")
    print("="*50)

    media_econ = df['Economia (%)'].mean()
    
    if 'ssim' in df.columns:
        media_ssim = df['ssim'].mean()
    else:
        media_ssim = 0.0 
    
    print(f"Total de Arquivos: {len(df)}")
    print(f"Média GERAL de Economia:       {media_econ:.2f}%")
    print(f"Média GERAL de SSIM (Qualidade): {media_ssim:.4f}")
    print("-" * 50)

    if 'Dataset' in df.columns:
        print("\n--- POR TIPO DE DADO ---")
        colunas_interesse = ['Economia (%)', 'Base Usada']
        if 'ssim' in df.columns: colunas_interesse.append('ssim')
        
        agrupado = df.groupby('Dataset')[colunas_interesse].mean()
        print(agrupado)
        
    print("="*50)

if __name__ == "__main__":
    analisar_resultados()