# Bot de Notas Fiscais

Automação desktop em PySide6 para agilizar rotinas fiscais. O app baixa XMLs de NF-e diretamente da API do MeuDanfe, cruza notas emitidas contra registros do Domínio e consulta dados cadastrais de empresas (Open CNPJa + Sintegra). Ele foi pensado para operadores administrativos: basta apontar planilhas/CSVs e o robô organiza os arquivos, gera relatórios e registra logs locais.

## Principais recursos

- **Download em massa de NF-e**: lê planilhas com chaves de acesso, consulta a API MeuDanfe e salva cada XML no padrão `Nome - CNPJ/tipo/NFE-<chave>.xml`.
- **Comparação DTE x Domínio**: importa múltiplos arquivos DTE (CSV) e o relatório de Entradas do Domínio, reconcilia valores e destaca divergências em um Excel formatado.
- **Consulta cadastral**: expõe utilitário para obter CNAE, situação, porte e inscrições estaduais via Open CNPJa e Sintegra/CE.
- **Interface pronta para usuários finais**: pop-ups dedicados em PySide6, execução assíncrona e empacotamento PyInstaller (`nfe-bot.spec`).
- **Logs e estrutura organizada**: cada execução gera `api_events.log`, pastas por empresa e relatórios em `relatorios/`.

## Estrutura do projeto
```text
app/
├── controller/        # Regras de negócio (consultar_nfe, comparar_nfe, consultar_cnpj, etc.)
├── model/             # Camada de dados (tratamento de CSV/XLSX, salvamento em Excel)
├── view/              # Layouts QML utilizados pela camada de apresentação
├── assets/            # Imagens e recursos visuais do app
└── interface.py       # Ponto de entrada da aplicação PySide6
nfe-bot.spec           # Script PyInstaller para gerar o executável
.env                   # Variáveis de ambiente (API_MEUDANFE)
```

## Requisitos
- Python 3.11
- Pipenv (ou pip tradicional, se preferir)
- Dependências principais: `pyside6`, `requests`, `pandas`, `openpyxl`, `python-dotenv`, `xmltodict`, `beautifulsoup4`
- Acesso às APIs externas:
  - [MeuDanfe](https://api.meudanfe.com.br/) – chave em `API_MEUDANFE`
  - [Open CNPJa](https://open.cnpja.com/) – endpoint público utilizado por `consultar_cnpj`
  - Sintegra/CE para consulta de IE (apenas para empresas do Ceará)

> **Importante:** o `Pipfile` lista somente as bibliotecas usadas diretamente pelo código. Garanta que todas as dependências (incluindo o PySide6) estejam instaladas antes de executar o aplicativo.

## Configuração rápida
1. Clone o repositório e acesse a pasta do projeto.
2. Copie `.env.example` (ou crie manualmente) e defina `API_MEUDANFE=<sua-chave>`.
3. Crie o ambiente virtual com Pipenv e instale as dependências:
   ```bash
   pipenv install
   pipenv shell
   ```
4. (Opcional) Para instalação com `pip`, rode `pip install -r requirements.txt` se você preferir gerar um arquivo a partir do Pipfile (`pipenv requirements > requirements.txt`).

## Execução
Basta rodar a interface PySide6 diretamente do código-fonte:
```bash
python app/interface.py
```

O PyInstaller já possui um spec file (`nfe-bot.spec`). Para empacotar:
```bash
pipenv run pyinstaller nfe-bot.spec
```
O executável ficará em `dist/Bot de NF-e/`.

## Fluxos suportados
### 1. Baixar NF-e
1. Abra o app e clique em **Baixar NF-e**.
2. Selecione a planilha (CSV/XLS/XLSX) com as chaves na coluna "Chave de Acesso".
3. O robô envia cada chave para a API MeuDanfe, baixa o XML retornado e cria pastas seguindo:
   ```text
   <Nome - CNPJ>/<Entradas|Saidas|tipo_desconhecido>/NFE-<chave>.xml
   ```
4. O log `api_events.log` registra sucessos ou erros de comunicação.

### 2. Comparar notas
1. Clique em **Comparar Notas** e selecione:  
   - Um ou mais arquivos DTE (`*.csv`) exportados pelo fiscal.  
   - O arquivo `Entradas.csv` do Domínio.
2. O sistema padroniza cabeçalhos/encodes, soma valores por número de nota e cruza os dois conjuntos.
3. O relatório final (`relatorios/Relatorio_Comparacao_NFe.xlsx`) traz:
   - Diferenças monetárias (`Diferença (Domínio - DTE)`),  
   - status (`Somente DTE`, `Somente Domínio`, `Valores iguais`, `Valores divergentes`),  
   - chaves de acesso concatenadas e rastreabilidade do arquivo DTE.

### 3. Consulta cadastral (utilitário)
- `app/controller/consultar_cnpj.py` expõe `consultar_cnpj(cnpj)` e `consultar_ie(cnpj)` para integrações externas ou linhas de comando.
- Retorna um `dataclass Empresa` com CNAE, situação, porte, Simples/Simei, membros e inscrições estaduais.

## Arquivos gerados
- `api_events.log`: histórico de requisições às APIs.
- `relatorios/Relatorio_Comparacao_NFe.xlsx`: cruzamento DTE x Domínio com formatação contábil.
- Pastas de NF-e: agrupadas por `Nome - CNPJ` e subpastas `Entradas`/`Saidas`.

## Desenvolvimento e contribuição
1. Ative o ambiente virtual e rode `python app/interface.py` para validar mudanças na UI.
2. Utilize `pipenv run python -m pytest` (caso adicione testes) ou scripts equivalentes.
3. Antes de submeter PRs/commits, valide:
   - `.env` não versionado (já listado em `.gitignore`).
   - Quebras de layout na interface PySide6/QML (`app/view/interface.qml`) ao tocar widgets.
   - Ajustes em `consultar_nfe` com requisições reais ou simuladas (mock de `requests`).

Sinta-se à vontade para abrir issues e sugerir novos fluxos (ex.: download automático via agenda, suporte a NFC-e de outros estados ou análises adicionais no relatório). Cada automação foi isolada em módulos específicos para facilitar novas integrações.
