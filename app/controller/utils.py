from pathlib import Path

TIPO_NFE = "nfe"
TIPO_NFC = "nfc"
_DETECTION_ENCODINGS = ("utf-8-sig", "latin-1")


def _parse_decimal(valor: str) -> float | None:
    """Converte valores em formato brasileiro para float."""
    if not valor:
        return None
    texto = valor.strip().replace(".", "").replace(",", ".").replace('"', "")
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
        raise FileNotFoundError("Arquivos não localizados: " + ", ".join(faltantes))


def _ler_primeira_linha(caminho: Path) -> str:
    for encoding in _DETECTION_ENCODINGS:
        try:
            with caminho.open("r", encoding=encoding) as arquivo:
                return arquivo.readline().strip()
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return ""
    return ""


def detectar_tipo_csv(caminho: Path | str) -> str | None:
    primeira_linha = _ler_primeira_linha(Path(caminho)).lower()
    if not primeira_linha:
        return None
    if "nfc" in primeira_linha:
        return TIPO_NFC
    if "nf-e" in primeira_linha or "nfe" in primeira_linha:
        return TIPO_NFE
    return None


def importar_arquivo() -> str:
    # Import deferred to avoid loading tkinter at module level in a PySide6 app.
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    return filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=(
            ("Arquivos CSV", "*.csv"),
            ("Todos os arquivos", "*.*"),
        ),
    )
