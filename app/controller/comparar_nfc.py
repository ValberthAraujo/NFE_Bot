from __future__ import annotations

import csv
import io
import unicodedata
from collections.abc import Iterator
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.controller.utils import _parse_decimal, _validar_fontes
from app.model.salvar_excel import salvar_relatorio

# Fixed column layout for the NFC DTE CSV (no column headers, positional).
DTE_COLUMN_CHAVE = 0
DTE_COLUMN_NUMERO = 5
DTE_COLUMN_VALOR = 10

DOMINIO_COLUMN_NUMERO = 4
DOMINIO_COLUMN_VALOR = 20

ENCODINGS = ("utf-8-sig", "latin-1")


def _obter_coluna(linha: list[str], indice: int | None) -> str:
    if indice is None or indice >= len(linha):
        return ""
    return linha[indice].strip()


def _extrair_numero_documento(valor: str) -> int | None:
    if not valor:
        return None
    trecho = valor.split("/")[0]
    somente_digitos = "".join(char for char in trecho if char.isdigit())
    if not somente_digitos:
        return None
    return int(somente_digitos)


def _forcar_lista_caminhos(caminhos: Iterable[Path | str] | Path | str) -> list[Path]:
    if isinstance(caminhos, (Path, str)):
        caminhos = [caminhos]
    return [Path(caminho) for caminho in caminhos]


def carregar_dte(caminhos: Iterable[Path | str] | Path | str) -> pd.DataFrame:
    registros: list[dict[str, object]] = []

    for caminho in _forcar_lista_caminhos(caminhos):
        if not caminho.exists():
            continue

        for encoding in ENCODINGS:
            try:
                with caminho.open(encoding=encoding) as fonte:
                    leitor = csv.reader(fonte)
                    for linha in leitor:
                        chave = _obter_coluna(linha, DTE_COLUMN_CHAVE).replace('"', "")
                        if len(chave) < 20:
                            continue

                        numero = _extrair_numero_documento(
                            _obter_coluna(linha, DTE_COLUMN_NUMERO)
                        )
                        valor = _parse_decimal(_obter_coluna(linha, DTE_COLUMN_VALOR))

                        if numero is None or valor is None:
                            continue

                        registros.append(
                            {
                                "Arquivo DTE": caminho.name,
                                "Nota DTE": numero,
                                "Valor DTE": valor,
                                "Chave de Acesso": chave,
                            }
                        )
                break
            except UnicodeDecodeError:
                continue

    df = pd.DataFrame(registros)

    if df.empty:
        return pd.DataFrame(columns=["Arquivo DTE", "Nota DTE", "Valor DTE", "Chave de Acesso"])

    def _concatenar_unicos(valores: pd.Series) -> str:
        distintos = sorted({valor for valor in valores if valor})
        return ", ".join(distintos)

    agrupado = (
        df.groupby("Nota DTE", as_index=False)
        .agg(
            {
                "Arquivo DTE": _concatenar_unicos,
                "Valor DTE": "sum",
                "Chave de Acesso": _concatenar_unicos,
            }
        )
        .reindex(columns=["Arquivo DTE", "Nota DTE", "Valor DTE", "Chave de Acesso"])
    )
    agrupado["Valor DTE"] = agrupado["Valor DTE"].round(2)

    return agrupado


def carregar_dominio(caminho: Path | str) -> pd.DataFrame:
    registros: list[dict[str, object]] = []
    caminho = Path(caminho)

    for encoding in ENCODINGS:
        try:
            with caminho.open(encoding=encoding) as fonte:
                leitor = csv.reader(fonte, delimiter=";")
                for linha in leitor:
                    if not linha:
                        continue

                    primeira_coluna = _obter_coluna(linha, 0).lower()
                    if primeira_coluna.startswith("total"):
                        continue

                    numero = _extrair_numero_documento(
                        _obter_coluna(linha, DOMINIO_COLUMN_NUMERO)
                    )
                    valor = _parse_decimal(_obter_coluna(linha, DOMINIO_COLUMN_VALOR))

                    if numero is None or valor is None:
                        continue

                    registros.append(
                        {
                            "Nota Dominio": numero,
                            "Valor Contabil Dominio": valor,
                        }
                    )
            break
        except UnicodeDecodeError:
            continue

    df = pd.DataFrame(registros)
    agrupado = (
        df.groupby("Nota Dominio", as_index=False)["Valor Contabil Dominio"]
        .sum()
        .round(2)
    )
    return agrupado


def montar_cruzamento(dte: pd.DataFrame, dominio: pd.DataFrame) -> pd.DataFrame:
    cruzamento = dte.merge(
        dominio,
        how="outer",
        left_on="Nota DTE",
        right_on="Nota Dominio",
    ).sort_values(["Nota DTE", "Nota Dominio", "Chave de Acesso"])

    cruzamento["Valor Contabil Dominio"] = pd.to_numeric(
        cruzamento.get("Valor Contabil Dominio"), errors="coerce"
    )
    cruzamento["Valor DTE"] = pd.to_numeric(cruzamento.get("Valor DTE"), errors="coerce")

    cruzamento["Diferenca (Dominio - DTE)"] = (
        cruzamento["Valor Contabil Dominio"].fillna(0)
        - cruzamento["Valor DTE"].fillna(0)
    ).round(2)

    def _classificar(row: pd.Series) -> str:
        if pd.isna(row["Valor Contabil Dominio"]):
            return "Somente DTE"
        if pd.isna(row["Valor DTE"]):
            return "Somente Dominio"
        if abs(row["Diferenca (Dominio - DTE)"]) < 0.01:
            return "Valores iguais"
        return "Valores divergentes"

    cruzamento["Status"] = cruzamento.apply(_classificar, axis=1)
    return cruzamento.reset_index(drop=True)


def comparar_nfc(
    caminhos_dte: Iterable[Path | str] | Path | str,
    caminho_dominio: Path | str,
) -> Path:
    caminhos_dte = _forcar_lista_caminhos(caminhos_dte)
    caminho_dominio = Path(caminho_dominio)

    _validar_fontes(caminhos_dte, caminho_dominio)

    dte = carregar_dte(caminhos_dte)
    dominio = carregar_dominio(caminho_dominio)
    cruzamento = montar_cruzamento(dte, dominio)

    ordem_colunas = [
        "Arquivo DTE",
        "Nota DTE",
        "Valor DTE",
        "Chave de Acesso",
        "Nota Dominio",
        "Valor Contabil Dominio",
        "Diferenca (Dominio - DTE)",
        "Status",
    ]
    presentes = [col for col in ordem_colunas if col in cruzamento.columns]
    restantes = [col for col in cruzamento.columns if col not in presentes]
    cruzamento = cruzamento[presentes + restantes]

    destino = Path.cwd() / "Relatorio_Comparacao_NFc.xlsx"
    salvar_relatorio(cruzamento, destino)
    return destino


if __name__ == "__main__":
    base_app = "C:/Projetos/2_SimpleBot/"
    comparar_nfc(
        caminhos_dte=[base_app + "DTE.csv"],
        caminho_dominio=base_app + "Dominio.csv",
    )
