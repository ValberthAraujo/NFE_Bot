import pandas as pd
from app.controller.utils import importar_arquivo


def ler_csv(caminho: str) -> list[str]:
    df_bruto = pd.read_csv(caminho, header=None, sep=",", dtype=str, encoding="latin1")
    remover_cabeçalho = df_bruto.iloc[4:].reset_index(drop=True)
    chave_col = 0

    chaves = remover_cabeçalho[chave_col].dropna()
    chaves = chaves.astype(str).str.strip()
    chaves = chaves[chaves != ""]

    return chaves.tolist()

if __name__ == "__main__":
    caminho_arquivo = importar_arquivo()
    chaves = ler_csv(caminho_arquivo)