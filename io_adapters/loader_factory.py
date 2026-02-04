import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
from PIL import Image

def load_dataset_file(filepath):
    """
    Lê arquivos .mhd, .csv, .jpg e devolve números (Numpy Array).
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo não existe: {filepath}")
        return None

    try:
        # 1. Imagens Médicas (LUNA16, DICOM)
        if ext in ['.mhd', '.dcm', '.nii']:
            itk_img = sitk.ReadImage(filepath)
            arr = sitk.GetArrayFromImage(itk_img)
            # Se for 3D, pega a fatia do meio
            return arr[arr.shape[0]//2] if arr.ndim == 3 else arr

        # 2. Imagens Comuns (JPG, PNG)
        elif ext in ['.jpg', '.png', '.jpeg', '.bmp']:
            img = Image.open(filepath).convert('L') # Converte para Preto e Branco
            return np.array(img)

        # 3. Tabelas de Dados (CSV, Excel)
        elif ext in ['.csv', '.txt']:
            df = pd.read_csv(filepath)
            # Pega apenas colunas numéricas
            return df.select_dtypes(include=[np.number]).to_numpy()

        # 4. Arrays Numpy Direto
        elif ext in ['.npy']:
            return np.load(filepath)

        else:
            print(f"[AVISO] Formato {ext} não suportado.")
            return None

    except Exception as e:
        print(f"[ERRO LOAD] Falha ao ler {filepath}: {e}")
        return None