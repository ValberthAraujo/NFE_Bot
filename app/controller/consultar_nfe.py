import requests
import xmltodict

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Sequence, Union

from app.model.ler_csv import ler_csv
from app.controller.utils import importar_arquivo


PASTA_UNICA_NOTAS = "Notas Fiscais"
_URL_ENVIAR = "https://api.meudanfe.com.br/v2/fd/add/{chave}"
_URL_PEGAR_XML = "https://api.meudanfe.com.br/v2/fd/get/xml/{chave}"


@dataclass
class Nfe:
    chave_acesso: str
    cnpj: str | None = None
    xml: str = ""
    nome_empresa: str | None = None
    tipo_nota: str | None = None
    id: str | None = None
    modelo_nf: str | None = None


def _localizar_inf_nfe(xml_dict: Any) -> Any:
    caminhos = [
        ("nfeProc", "NFe", "infNFe"),
        ("NFe", "infNFe"),
        ("infNFe",),
    ]

    for caminho in caminhos:
        atual: Any = xml_dict
        for chave in caminho:
            if isinstance(atual, list):
                atual = atual[0]

            if not isinstance(atual, dict) or chave not in atual:
                atual = None
                break

            atual = atual[chave]

        if atual:
            return atual

    return None


def _primeiro_dict(no: Any) -> dict[str, Any]:
    if isinstance(no, dict):
        return no
    if isinstance(no, list):
        for item in no:
            if isinstance(item, dict):
                return item
    return {}


def _extrair_documento(*valores: Any) -> str | None:
    for valor in valores:
        if isinstance(valor, str):
            somente_digitos = "".join(filter(str.isdigit, valor))
            if somente_digitos:
                return somente_digitos
    return None


def _detectar_modelo_nf(inf_nfe: dict[str, Any]) -> str | None:
    ide = _primeiro_dict(inf_nfe.get("ide"))
    modelo_valor = ide.get("mod")

    modelo = ""
    if isinstance(modelo_valor, str):
        modelo = modelo_valor.strip()
    elif isinstance(modelo_valor, (int, float)):
        modelo = str(int(modelo_valor))

    if modelo == "55":
        return "NF-e velho"
    if modelo == "65":
        return "NF-e novo"

    versao_valor = inf_nfe.get("@versao") or inf_nfe.get("versao")
    versao = None
    if isinstance(versao_valor, str):
        texto = versao_valor.strip().replace(",", ".")
        try:
            versao = float(texto)
        except ValueError:
            versao = None
    elif isinstance(versao_valor, (int, float)):
        versao = float(versao_valor)

    if versao is not None:
        return "NF-e novo" if versao >= 4 else "NF-e velho"

    return None


def _extrair_dados_xml(xml_data: str) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    nome_empresa: str | None = None
    tipo_nota: str | None = None
    cnpj_afetado: str | None = None
    tipo_nota_nome: str | None = None
    id_infNFe: str | None = None
    modelo_nf: str | None = None

    xml_dict = xmltodict.parse(xml_data)
    inf_nfe = _localizar_inf_nfe(xml_dict)

    if not isinstance(inf_nfe, dict):
        return cnpj_afetado, tipo_nota_nome, nome_empresa, id_infNFe, modelo_nf

    # id_attr must be resolved before use
    id_attr = inf_nfe.get("@Id") or inf_nfe.get("Id")
    if isinstance(id_attr, str):
        id_infNFe = id_attr

    modelo_nf = _detectar_modelo_nf(inf_nfe)
    ide = inf_nfe.get("ide") or {}
    tp_nf = ide.get("tpNF")

    if tp_nf is not None:
        tipo_nota = str(tp_nf)
    if tipo_nota == "0":
        tipo_nota_nome = "Entradas"
    elif tipo_nota == "1":
        tipo_nota_nome = "Saidas"

    emit = _primeiro_dict(inf_nfe.get("emit"))
    dest = _primeiro_dict(inf_nfe.get("dest"))

    cnpj_emit = _extrair_documento(emit.get("CNPJ"), emit.get("CPF"))
    cnpj_dest = _extrair_documento(dest.get("CNPJ"), dest.get("CPF"))

    if tipo_nota == "1":
        cnpj_afetado = cnpj_dest or cnpj_emit
        nome_empresa = dest.get("xNome") or emit.get("xNome")
    elif tipo_nota == "0":
        cnpj_afetado = cnpj_emit or cnpj_dest
        nome_empresa = emit.get("xNome") or dest.get("xNome")
    else:
        cnpj_afetado = cnpj_emit or cnpj_dest
        nome_empresa = emit.get("xNome") or dest.get("xNome")

    return cnpj_afetado, tipo_nota_nome, nome_empresa, id_infNFe, modelo_nf


def consultar_nfe(chave_acesso_nfe: str, token: str) -> Union["Nfe", str]:
    try:
        root_path = Path.cwd()

        headers = {
            "accept": "application/json",
            "Api-Key": token,
        }

        requests.put(
            _URL_ENVIAR.format(chave=chave_acesso_nfe),
            headers=headers,
            timeout=30,
        )
        response = requests.get(
            _URL_PEGAR_XML.format(chave=chave_acesso_nfe),
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        xml_data: str | None = data.get("data")

        if not xml_data:
            return f"Chave {chave_acesso_nfe}: resposta da API não contém XML."

        cnpj, tipo_nota, nome_empresa, id_infNFe, modelo_nf = _extrair_dados_xml(xml_data)

        pasta_empresa = PASTA_UNICA_NOTAS
        pasta_tipo = tipo_nota or "Outros"

        pasta_destino = root_path / pasta_empresa / pasta_tipo
        pasta_destino.mkdir(parents=True, exist_ok=True)

        caminho_xml = pasta_destino / f"NFE-{chave_acesso_nfe}.xml"
        caminho_xml.write_text(xml_data, encoding="utf-8")

        return Nfe(
            chave_acesso=chave_acesso_nfe,
            cnpj=cnpj,
            xml=xml_data,
            nome_empresa=nome_empresa,
            tipo_nota=tipo_nota,
            id=id_infNFe,
            modelo_nf=modelo_nf,
        )

    except requests.RequestException as exc:
        return f"Chave {chave_acesso_nfe}: erro de rede — {exc}"
    except ValueError as exc:
        return f"Chave {chave_acesso_nfe}: resposta inválida — {exc}"
    except Exception as exc:
        return f"Chave {chave_acesso_nfe}: erro inesperado — {exc}"


def obter_xml_nfe(caminho_planilha: str | None = None, token: str = "") -> Sequence[Union[Nfe, str]]:
    caminho = caminho_planilha or importar_arquivo()
    chaves = ler_csv(caminho)

    resultados: List[Union[Nfe, str]] = []
    for chave in chaves:
        resultado = consultar_nfe(chave, token)
        resultados.append(resultado)

    return resultados
