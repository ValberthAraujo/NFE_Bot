# Modulo para comparar NF-e
import csv
import io
import os
import unicodedata
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from app.model.salvar_excel import salvar_relatorio


def _parse_decimal(valor: str) -> float | None:
    """Converte valores em formato brasileiro para float."""
    if not valor:
        return None

    texto = (
        valor.strip()
        .replace(".", "")
        .replace(",", ".")
        .replace('"', "")
    )

    if not texto:
        return None

    try:
        return round(float(texto), 2)
    except ValueError:
        return None


def _validar_fontes(caminhos_dte: list[Path], caminho_dominio: Path) -> None:
    todos = caminhos_dte + [caminho_dominio]
    faltantes = [c.name for c in todos if not c.exists()]

    if faltantes:
        raise FileNotFoundError("Arquivos nao localizados: " + ", ".join(faltantes))


def _abrir_csv(caminho: Path, delimiter: str = ",") -> Iterator[list[str]]:
    dados = caminho.read_bytes()
    ultimo_erro: Exception | None = None

    for encoding in ("utf-8-sig", "latin-1"):
        try:
            texto = dados.decode(encoding)
            return csv.reader(io.StringIO(texto), delimiter=delimiter)
        except UnicodeDecodeError as exc:
            ultimo_erro = exc

    raise ValueError(
        f"Nao foi possivel decodificar {caminho.name} com encodings conhecidos"
    ) from ultimo_erro


def _normalizar_texto(texto: str) -> str:
    if not texto:
        return ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower().strip()


def _identificar_indices_dte(header: list[str]) -> dict[str, int]:
    normalizados = [_normalizar_texto(col) for col in header]

    def localizar(possiveis: tuple[str, ...]) -> int:
        for termo in possiveis:
            if termo in normalizados:
                return normalizados.index(termo)
        raise ValueError(
            "Cabecalho de DTE nao possui colunas esperadas: " + ", ".join(possiveis)
        )

    return {
        "chave": localizar(("chave de acesso",)),
        "nota": localizar(("numero nota", "numero da nota", "nota")),
        "valor": localizar(("valor da nf-e", "valor nf-e", "valor nf", "valor da nf")),
    }


def _eh_header_dte(linha: list[str]) -> bool:
    linha_unida = " ".join(
        _normalizar_texto(col) for col in linha if _normalizar_texto(col)
    )
    return "chave de acesso" in linha_unida and "valor da nf" in linha_unida


def _identificar_indices_dominio(header: list[str]) -> dict[str, int]:
    normalizados = [_normalizar_texto(col) for col in header]

    def localizar(possiveis: tuple[str, ...]) -> int:
        for termo in possiveis:
            if termo in normalizados:
                return normalizados.index(termo)
        raise ValueError(
            "Cabecalho de Dominio nao possui colunas esperadas: " + ", ".join(possiveis)
        )

    return {
        "nota": localizar(("numero nota", "numero da nota", "nota")),
        "valor": localizar(("valor contabil", "valor contabilidade")),
    }


def _eh_header_dominio(linha: list[str]) -> bool:
    linha_unida = " ".join(
        _normalizar_texto(col) for col in linha if _normalizar_texto(col)
    )
    contem_valor = "valor contabil" in linha_unida
    contem_nota = any(
        termo in linha_unida for termo in ("data emissao", "numero nota", "nota")
    )
    return contem_valor and contem_nota


def carregar_dte(caminhos: list[Path]) -> pd.DataFrame:
    registros: list[dict[str, object]] = []

    for caminho in caminhos:
        if not caminho.exists():
            continue

        leitor = _abrir_csv(caminho)
        indices_colunas: dict[str, int] | None = None

        for linha in leitor:

            if indices_colunas is None:
                if _eh_header_dte(linha):
                    indices_colunas = _identificar_indices_dte(linha)
                continue

            if _eh_header_dte(linha):
                indices_colunas = _identificar_indices_dte(linha)
                continue

            if not linha or not linha[0].strip():
                continue

            if any(idx >= len(linha) for idx in indices_colunas.values()):
                continue

            numero_raw = linha[indices_colunas["nota"]].strip().split("/")[0]
            chave = linha[indices_colunas["chave"]].strip().replace('"', "")
            valor_raw = linha[indices_colunas["valor"]]

            if not numero_raw.isdigit() or not chave:
                continue

            valor = _parse_decimal(valor_raw)
            if valor is None:
                continue

            registros.append(
                {
                    "Arquivo DTE": caminho.name,
                    "Nota DTE": int(numero_raw),
                    "Valor DTE": valor,
                    "Chave de Acesso": chave,
                }
            )

    if not registros:
        raise ValueError("Nenhum registro valido encontrado nos arquivos DTE.")

    return pd.DataFrame(registros)


def carregar_dominio(caminho: Path) -> pd.DataFrame:
    """Le Entradas.csv (Dominio) e retorna Nota x Valor agrupado."""
    registros: list[dict[str, object]] = []

    leitor = _abrir_csv(caminho, delimiter=";")
    indices_colunas: dict[str, int] | None = None

    for linha in leitor:
        if indices_colunas is None:
            if _eh_header_dominio(linha):
                indices_colunas = _identificar_indices_dominio(linha)
            continue

        if _eh_header_dominio(linha):
            indices_colunas = _identificar_indices_dominio(linha)
            continue

        if not linha:
            continue

        if any(idx >= len(linha) for idx in indices_colunas.values()):
            continue

        nota_raw = linha[indices_colunas["nota"]].strip().split("/")[0]
        valor_raw = linha[indices_colunas["valor"]].strip()

        if not nota_raw.isdigit():
            continue

        valor = _parse_decimal(valor_raw)
        if valor is None:
            continue

        registros.append(
            {
                "Nota Dominio": int(nota_raw),
                "Valor Contabil Dominio": valor,
            }
        )

    if not registros:
        raise ValueError("Nenhum registro valido encontrado em Entradas.csv.")

    df = pd.DataFrame(registros)
    agrupado = (
        df.groupby("Nota Dominio", as_index=False)["Valor Contabil Dominio"]
        .sum()
        .round(2)
    )
    return agrupado


def montar_cruzamento(dte: pd.DataFrame, dominio: pd.DataFrame) -> pd.DataFrame:
    """Une as bases e indica diferencas."""
    cruzamento = dte.merge(
        dominio,
        how="outer",
        left_on="Nota DTE",
        right_on="Nota Dominio",
    ).sort_values(["Nota DTE", "Nota Dominio", "Chave de Acesso"])

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


def comparar_nfe(caminhos_dte: list[str | Path], caminho_dominio: str | Path):
    caminhos_dte = [Path(c) for c in caminhos_dte]
    caminho_dominio = Path(caminho_dominio)

    _validar_fontes(caminhos_dte, caminho_dominio)

    dte = carregar_dte(caminhos_dte)
    dominio = carregar_dominio(caminho_dominio)
    cruzamento = montar_cruzamento(dte, dominio)

    caminho_saida = Path(os.getcwd()) / "relatorio_cruzamento.xlsx"
    salvar_relatorio(cruzamento, caminho_saida)

    return caminho_saida


if __name__ == "__main__":
    comparar_nfe(
        caminhos_dte = [r"C:\Projetos\2_SimpleBot\DTE.csv"],
        caminho_dominio= r"C:\Projetos\2_SimpleBot\Dominio.csv",
    )
