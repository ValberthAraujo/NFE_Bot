import os
import requests
import xmltodict

from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List, Sequence, Union
from app.model.ler_csv import ler_csv, importar_arquivo


PASTA_UNICA_NOTAS = "Notas Fiscais"


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
    if isinstance(id_attr, str):
        id_infNFe = id_attr

    id_attr = inf_nfe.get("@Id") or inf_nfe.get("Id")
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


def consultar_nfe(chave_acesso_nfe: str) -> Union[Nfe, str]:
    root_path = os.getcwd()
    load_dotenv()

    headers = {
        "accept": "application/json",
        "Api-Key": os.getenv("API_MEUDANFE"),
    }
    url_enviarcodigo = f"https://api.meudanfe.com.br/v2/fd/add/{chave_acesso_nfe}"
    url_pegarxml = f"https://api.meudanfe.com.br/v2/fd/get/xml/{chave_acesso_nfe}"

    requests.put(url_enviarcodigo, headers=headers, timeout=30)
    response = requests.get(url_pegarxml, headers=headers, timeout=30)

    data = response.json()
    xml_data = data.get("data")

    cnpj, tipo_nota, nome_empresa, id_infNFe, modelo_nf = _extrair_dados_xml(xml_data)

    pasta_empresa = PASTA_UNICA_NOTAS
    pasta_tipo = tipo_nota

    os.makedirs(os.path.join(root_path, pasta_empresa, pasta_tipo), exist_ok=True)

    caminho_xml = os.path.join(root_path, pasta_empresa, pasta_tipo, f"NFE-{chave_acesso_nfe}.xml")

    with open(caminho_xml, "w", encoding="utf-8") as arquivo_xml:
        arquivo_xml.write(xml_data)

    return Nfe(
        chave_acesso=chave_acesso_nfe,
        cnpj=cnpj,
        xml=xml_data,
        nome_empresa=nome_empresa,
        tipo_nota=tipo_nota,
        id=id_infNFe,
        modelo_nf=modelo_nf,
    )


def obter_xml_nfe(caminho_planilha: str | None = None) -> Sequence[Union[Nfe, str]]:
    caminho = caminho_planilha or importar_arquivo()
    chaves = ler_csv(caminho)

    resultados: List[Union[Nfe, str]] = []
    for chave in chaves:
        resultado = consultar_nfe(chave)
        resultados.append(resultado)

    return resultados
