from pathlib import Path
from threading import Thread
import sys

_BASE_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _BASE_DIR.parent

for _path in (_PROJECT_DIR, _BASE_DIR):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtQml import QQmlApplicationEngine
from app.controller.consultar_nfe import obter_xml_nfe
from app.controller.comparar_nfe import comparar_nfe as comparar_nfe_documentos
from app.controller.comparar_nfc import comparar_nfe as comparar_nfc_documentos
from app.controller.utils import detectar_tipo_csv, TIPO_NFE, TIPO_NFC

def resource_path(*relative_parts: str) -> Path:
    relative = Path(*relative_parts)
    pyinstaller_root = getattr(sys, "_MEIPASS", None)
    if pyinstaller_root:
        candidate = Path(pyinstaller_root).joinpath(*relative_parts)
        if candidate.exists():
            return candidate
    return _BASE_DIR.joinpath(*relative_parts)


def executar_em_thread(funcao, *args, **kwargs) -> Thread:
    thread = Thread(target=funcao, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def selecionar_arquivo(titulo: str) -> str:
    arquivo, _ = QFileDialog.getOpenFileName(
        None,
        titulo,
        str(Path.home()),
        "Arquivos CSV (*.csv);;Todos os arquivos (*.*)",
    )
    return arquivo


BACKGROUND_IMAGE = resource_path("assets", "nfe-bot-fundo.png")
QML_INTERFACE = resource_path("view", "interface.qml")


class InterfaceBackend(QObject):
    messageEmitted = Signal(str, str)
    dtePathChanged = Signal()
    dominioPathChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._dte_path = ""
        self._dominio_path = ""
        self._background = BACKGROUND_IMAGE.as_uri() if BACKGROUND_IMAGE.exists() else ""

    def _emit_message(self, titulo: str, mensagem: str) -> None:
        self.messageEmitted.emit(titulo, mensagem)

    def _set_dte_path(self, caminho: str) -> None:
        if self._dte_path != caminho:
            self._dte_path = caminho
            self.dtePathChanged.emit()

    def _set_dominio_path(self, caminho: str) -> None:
        if self._dominio_path != caminho:
            self._dominio_path = caminho
            self.dominioPathChanged.emit()

    @Property(str, constant=True)
    def backgroundSource(self) -> str:
        return self._background

    @Property(str, notify=dtePathChanged)
    def dtePath(self) -> str:
        return self._dte_path

    @Property(str, notify=dominioPathChanged)
    def dominioPath(self) -> str:
        return self._dominio_path

    @Slot()
    def selecionarDte(self) -> None:
        arquivo = selecionar_arquivo("Selecione o arquivo DTE")
        if arquivo:
            self._set_dte_path(arquivo)

    @Slot()
    def selecionarDominio(self) -> None:
        arquivo = selecionar_arquivo("Selecione o arquivo Domínio")
        if arquivo:
            self._set_dominio_path(arquivo)

    @Slot(str, result=bool)
    def executarDownload(self, token: str) -> bool:
        arquivo = selecionar_arquivo("Selecione o CSV com as chaves")
        if not arquivo:
            return False
        executar_em_thread(obter_xml_nfe, arquivo, token)
        self._emit_message("Baixar NF-e", "Download iniciado em segundo plano.")
        return True

    @Slot(result=bool)
    def compararNotas(self) -> bool:
        if not self._dte_path or not self._dominio_path:
            self._emit_message("Arquivos obrigatórios", "Selecione os arquivos DTE e Domínio.")
            return False

        caminho_dte = Path(self._dte_path)
        caminho_dominio = Path(self._dominio_path)

        tipo_dte = detectar_tipo_csv(caminho_dte)
        if tipo_dte not in (TIPO_NFE, TIPO_NFC):
            self._emit_message(
                "Arquivo DTE inválido",
                f"Não foi possível identificar se {caminho_dte.name} é NFe ou NFC.",
            )
            return False

        funcao = comparar_nfc_documentos if tipo_dte == TIPO_NFC else comparar_nfe_documentos
        executar_em_thread(funcao, [caminho_dte], caminho_dominio)
        self._emit_message("Comparar Notas", "Comparação iniciada em segundo plano.")
        return True


def main() -> int:
    app = QApplication(sys.argv)
    backend = InterfaceBackend()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(str(QML_INTERFACE))

    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
