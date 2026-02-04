import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURAÇÃO DOS DADOS FINAIS (Recuperados dos testes) ---
dados_consolidados = {
    'Dataset': ['LUNA16 (Médico)', 'Human Faces', 'Paisagens'],
    'Tipo': ['Alta Compressão', 'Alta Fidelidade', 'Híbrido'],
    'Economia (%)': [71.37, 29.45, 25.59],
    'SSIM': [0.5507, 0.9902, 0.9895],
    'PSNR (dB)': [11.49, 45.22, 44.46],
    'Base Usada': ['1.151', '1.022', '1.022']
}

def gerar_visuais_tcc():
    # Cria o DataFrame
    df = pd.DataFrame(dados_consolidados)
    
    pasta_saida = "resultados_graficos_finais"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        
    print("Gerando gráficos para o TCC...")
    print(df)

    # Configuração de Estilo
    sns.set_theme(style="whitegrid")
    
    # --- GRÁFICO 1: COMPARATIVO DE ECONOMIA (BARRAS) ---
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='Dataset', y='Economia (%)', data=df, palette='Blues_d')
    
    # Adiciona valores nas barras
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}%', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha='center', va='center', 
                   xytext=(0, 9), 
                   textcoords='offset points',
                   fontsize=14, fontweight='bold')
                   
    plt.title('Eficiência de Compressão por Domínio (FoL)', fontsize=16)
    plt.ylim(0, 100)
    plt.ylabel('Redução de Tamanho (%)', fontsize=12)
    plt.xlabel('')
    
    salvar_em = os.path.join(pasta_saida, "1_comparativo_economia.png")
    plt.savefig(salvar_em, dpi=300)
    print(f"[OK] Gráfico de Economia salvo: {salvar_em}")
    plt.close()

    # --- GRÁFICO 2: QUALIDADE VISUAL (SSIM) ---
    plt.figure(figsize=(10, 6))
    colors = ['#ff9999', '#66b3ff', '#99ff99'] # Cores diferentes para destacar
    ax = sns.barplot(x='Dataset', y='SSIM', data=df, palette='viridis')
    
    # Linha de corte de "Perfeição" (0.95)
    plt.axhline(0.95, color='red', linestyle='--', label='Limiar de Alta Fidelidade (0.95)')
    
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.3f}', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha='center', va='center', 
                   xytext=(0, 9), 
                   textcoords='offset points',
                   fontsize=14, fontweight='bold')

    plt.title('Integridade Visual (SSIM) por Domínio', fontsize=16)
    plt.ylim(0, 1.1)
    plt.ylabel('SSIM (1.0 = Idêntico)', fontsize=12)
    plt.legend()
    
    salvar_em = os.path.join(pasta_saida, "2_comparativo_qualidade_ssim.png")
    plt.savefig(salvar_em, dpi=300)
    print(f"[OK] Gráfico de SSIM salvo: {salvar_em}")
    plt.close()

    # --- GRÁFICO 3: TRADE-OFF (ECONOMIA vs QUALIDADE) ---
    # O Gráfico mais importante para a defesa
    plt.figure(figsize=(10, 7))
    
    # Plot de dispersão
    sns.scatterplot(data=df, x='Economia (%)', y='SSIM', hue='Dataset', style='Dataset', s=500)
    
    # Anotações
    for i in range(df.shape[0]):
        plt.text(
            df['Economia (%)'][i]+1, 
            df['SSIM'][i]+0.02, 
            f"{df['Dataset'][i]}\n(Base {df['Base Usada'][i]})", 
            fontsize=11, 
            weight='bold'
        )

    plt.title('Trade-off: Economia vs. Fidelidade', fontsize=16)
    plt.xlabel('Economia de Espaço (%)', fontsize=12)
    plt.ylabel('Qualidade Visual (SSIM)', fontsize=12)
    plt.xlim(0, 100)
    plt.ylim(0, 1.1)
    plt.grid(True, linestyle='--')
    
    # Áreas de fundo para explicar o conceito
    plt.axvspan(60, 100, color='green', alpha=0.1, label='Zona de Alta Compressão')
    plt.axhspan(0.90, 1.1, color='blue', alpha=0.1, label='Zona de Alta Fidelidade')
    
    plt.legend(loc='lower left')
    
    salvar_em = os.path.join(pasta_saida, "3_tradeoff_analise.png")
    plt.savefig(salvar_em, dpi=300)
    print(f"[OK] Gráfico de Trade-off salvo: {salvar_em}")
    plt.close()

if __name__ == "__main__":
    gerar_visuais_tcc()