# 🔬 Pesquisa FoL Universal: Compressão e Armazenamento Otimizado

Este repositório contém a implementação e validação experimental do algoritmo **Floor of Log (FoL)**, baseado na tese de Peixoto (2023). O projeto expande a aplicação original (focada em imagens médicas LUNA16) para uma **arquitetura universal**, capaz de processar diferentes tipos de dados (Imagens, CSVs) em um fluxo de nuvem simulado.

O objetivo é validar a redução de entropia e economia de armazenamento para cenários de **IoT e Telemedicina** usando Object Storage (MinIO/S3).

> [!IMPORTANT]
> **Otimização de Armazenamento:** O algoritmo converte automaticamente os dados processados para **int16, uint16 ou uint8**, dependendo da faixa de valores dinâmica e do tipo de dado (Médico vs Visual), maximizando a economia de espaço.

---

## 📂 Estrutura do Projeto

O projeto segue uma arquitetura modular para separar a ciência (algoritmos) da engenharia (pipeline de dados).

```text
pesquisa-fol-universal/
│
├── core/                       # O "Cérebro" (Matemática Pura)
│   ├── transform.py            # Algoritmo FoL com Janelamento (Windowing)
│   ├── optimizer.py            # Auto-Tuning (Kneedle Algorithm)
│   ├── descriptors.py          # Extrator LBP (Texture Descriptors)
│   └── metrics.py              # Cálculo de SSIM, DICE, PSNR (Qualidade)
│
├── io_adapters/                # Os "Conectores" (I/O)
│   ├── loader_factory.py       # Carrega MHD, JPG, CSV, NPY automaticamente
│   └── minio_connector.py      # Gerencia upload/download no MinIO
│
├── datasets/                   # Seus Dados (Entrada)
│   ├── luna16/                 # Ex: Imagens Médicas (.mhd/.raw)
│   ├── paisagens/              # Ex: Imagens Gerais (.jpg)
│   └── humanfaces/             # Ex: Imagens de Rosto (.jpg)
│
├── scripts/                    # Ferramentas de Análise
│   ├── analise_global.py       # Resumo estatístico do CSV final no terminal
│   ├── gerar_graficos.py       # Gera gráficos de barras e trade-off
│   ├── gerar_relatorio_visual.py # Cria imagens comparativas (Original vs FoL)
│   ├── inspect_sample.py       # Visualizador individual interativo
│   └── inspect_optimization.py # Visualizador da curva de "Cotovelo"
│
├── dados_minio/                # Simulação do Storage Local (MinIO)
├── resultados_graficos_finais/ # Saída dos gráficos gerados
├── resultados_visuais/         # Saída das imagens comparativas
│
├── main.py                     # O Pipeline Principal (Batch Processing)
├── requirements.txt            # Dependências Python
└── resultado_final_metricas.csv # Relatório final consolidado
```

---

## Pré-requisitos e Instalação

### 1. Ambiente Python
Instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 2. Infraestrutura de Armazenamento (MinIO)
Este projeto requer uma instância local do MinIO rodando para simular a nuvem S3.
1. Baixe o `minio.exe`.
2. Execute em um terminal separado (**PowerShell**):

```powershell
.\minio.exe server .\dados_minio --console-address ":9001"
```

---

## Como Rodar (Pipeline Principal)

O script `main.py` é o orquestrador. Ele aceita argumentos para controlar o comportamento do algoritmo FoL.

### 1. Execução Padrão (Base Default = 1.05)
Se nenhuma base for especificada, o algoritmo usa **b = 1.05**. Ideal para testes rápidos ou dados genéricos.

```bash
# Processa tudo que está na pasta datasets/
python main.py --root "datasets"
```

### 2. Cenário de Alta Fidelidade (Faces e Paisagens)
Para reproduzir os resultados de SSIM > 0.99 (Biometria/Fotografia), force a "Base Dourada" (1.022).

```bash
# Processa apenas a pasta humanfaces com base 1.022
python main.py --root "datasets" --only "humanfaces" --base 1.022
```

### 3. Cenário de Alta Compressão (Médico / LUNA16)
Para maximizar a economia de espaço (~71%) em exames médicos, utilize a **Base 1.151** combinada com o descritor de textura LBP.

```bash
# A flag --lbp ativa o pré-processamento de textura
python main.py --root "datasets" --only "luna16" --base 1.151 --lbp
```

### 4. Modo Automático (Auto-Tuning)
O sistema ignora a base manual e calcula matematicamente a base ideal para cada arquivo individualmente usando o **Método do Cotovelo** (Kneedle Algorithm). Útil para datasets desconhecidos.

```bash
python main.py --root "datasets" --auto
```

| Argumento | Função |
| :--- | :--- |
| `--root` | Pasta raiz onde estão os datasets (Obrigatório). |
| `--only` | Processa apenas uma subpasta específica (ex: luna16). |
| `--base` | Define manualmente a base logarítmica (ex: 1.022). Se omitido, usa 1.05. |
| `--auto` | Ativa o otimizador automático de base (substitui o `--base`). |
| `--lbp` | Ativa o filtro Local Binary Patterns (recomendado para imagens/médico). |

---

## Ferramentas de Análise e Pós-Processamento

Após rodar o pipeline principal, use os scripts da pasta `scripts/` para visualizar e analisar os resultados.

### 1. Resumo Estatístico Global
Lê o `resultado_final_metricas.csv` e exibe médias de economia e qualidade (SSIM) agrupadas por dataset no terminal.

```bash
python scripts/analise_global.py
```

### 2. Relatório Visual (Comparativo)
Gera imagens lado-a-lado (**Original** | **Reconstruído** | **Mapa de Erro**) na pasta `resultados_visuais/`.
*(Obs: Edite a variável `FILTRO_DATASET` dentro do script para selecionar o dataset desejado)*

```bash
python scripts/gerar_relatorio_visual.py
```

### 3. Gráficos Consolidados
Gera gráficos de barras (Economia, Comparativo SSIM) e Scatter Plot (Trade-off) na pasta `resultados_graficos_finais/`.

```bash
python scripts/gerar_graficos.py
```

### 4. Inspeção Individual
Para analisar um único arquivo detalhadamente (ver janelamento e histogramas):

```bash
python scripts/inspect_sample.py "datasets/luna16/exemplo.mhd" --lbp
```

---

## Relatórios de Métricas

Ao final da execução do `main.py`, o arquivo **`resultado_final_metricas.csv`** será gerado na raiz.
*   **Separador:** Ponto e vírgula (`;`)
*   **Métricas Incluídas:**
    *   **Economia (%):** Redução de tamanho (Original vs MinIO).
    *   **SSIM:** Similaridade estrutural (0 a 1).
    *   **PSNR:** Relação sinal-ruído.
    *   **DICE:** Coeficiente de sobreposição (apenas datasets médicos).
    *   **Tempo:** Tempo de processamento.

---

## Desenvolvimento Colaborativo

*   **Novas Métricas:** Devem ser implementadas em `core/metrics.py`. O `main.py` chamará o `calcular_metricas` automaticamente.
*   **Novos Tipos de Arquivo:** Adicione o suporte em `io_adapters/loader_factory.py`.

## Referências
* **Peixoto, S. A. (2023).** *Transformada Floor of Log Aplicada em Contexto Cross-Dimensional*. Tese de Doutorado.