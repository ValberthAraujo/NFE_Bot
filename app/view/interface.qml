import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

// ═══════════════════════════════════════════════════════════════════════════════
//  Paleta  "The Deep Blue"
//  #050a30  →  bg principal (fundo profundo)
//  #f4f3fc  →  texto / elementos claros
//  #233dff  →  destaque / acento
//
//  Derivadas (rgba sobre as três):
//  sidebar bg  : #030720  (5% mais escuro que bg)
//  card bg     : #0a1040
//  divider     : #233dff @ 0.18
//  texto muted : #f4f3fc @ 0.45
//  texto dim   : #f4f3fc @ 0.22
//  accent dim  : #233dff @ 0.12
//  accent hover: #233dff @ 0.22
// ═══════════════════════════════════════════════════════════════════════════════

ApplicationWindow {
    id: root
    width: 1000
    height: 620
    minimumWidth: 820
    minimumHeight: 500
    visible: true
    title: "Bot de Notas Fiscais"
    color: "#050a30"

    // ── Tokens de cor ──────────────────────────────────────────────────────────
    readonly property color colBg:           "#050a30"
    readonly property color colSidebar:      "#030720"
    readonly property color colCard:         "#0a1040"
    readonly property color colAccent:       "#233dff"
    readonly property color colText:         "#f4f3fc"
    readonly property color colTextMuted:    Qt.rgba(0.957, 0.953, 0.988, 0.45)
    readonly property color colTextDim:      Qt.rgba(0.957, 0.953, 0.988, 0.22)
    readonly property color colDivider:      Qt.rgba(0.137, 0.239, 1.0,   0.18)
    readonly property color colAccentDim:    Qt.rgba(0.137, 0.239, 1.0,   0.12)
    readonly property color colAccentHover:  Qt.rgba(0.137, 0.239, 1.0,   0.22)
    readonly property color colAccentBorder: Qt.rgba(0.137, 0.239, 1.0,   0.35)

    // ─── Fundo ─────────────────────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: root.colBg }
            GradientStop { position: 1.0; color: "#080f3a" }
        }
    }

    // Círculo decorativo superior esquerdo
    Rectangle {
        width: 340; height: 340; radius: 170
        x: -100; y: -100
        color: "transparent"
        border.color: root.colAccent; border.width: 1
        opacity: 0.18
    }
    Rectangle {
        width: 200; height: 200; radius: 100
        x: -50; y: -50
        color: root.colAccent; opacity: 0.07
    }

    // Círculo decorativo inferior direito
    Rectangle {
        width: 300; height: 300; radius: 150
        x: root.width - 150; y: root.height - 150
        color: root.colAccent; opacity: 0.06
    }

    // Imagem de fundo opcional
    Image {
        anchors.fill: parent
        source: backend.backgroundSource
        fillMode: Image.PreserveAspectCrop
        opacity: backend.backgroundSource.length > 0 ? 0.05 : 0
    }

    // ─── Layout principal ──────────────────────────────────────────────────────
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ══ Painel lateral ════════════════════════════════════════════════════
        Rectangle {
            Layout.preferredWidth: 240
            Layout.fillHeight: true
            color: root.colSidebar

            // Borda direita
            Rectangle {
                anchors.right: parent.right
                width: 1; height: parent.height
                color: root.colDivider
            }

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                // ── Branding ─────────────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    color: "transparent"

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 12

                        Rectangle {
                            width: 38; height: 38; radius: 10
                            color: root.colAccentDim
                            border.color: root.colAccentBorder; border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "NF"
                                color: root.colAccent
                                font.pixelSize: 13; font.bold: true; font.letterSpacing: 1
                            }
                        }

                        ColumnLayout {
                            spacing: 2
                            Label {
                                text: "NF-e Bot"
                                color: root.colText
                                font.pixelSize: 15; font.bold: true; font.letterSpacing: 0.5
                            }
                            Label {
                                text: "Automação Fiscal"
                                color: root.colTextMuted
                                font.pixelSize: 10; font.letterSpacing: 0.8
                            }
                        }
                    }
                }

                // Divisor
                Rectangle {
                    Layout.fillWidth: true; height: 1
                    color: root.colDivider
                    Layout.leftMargin: 20; Layout.rightMargin: 20
                }

                Item { Layout.preferredHeight: 20 }

                // Label de seção
                Label {
                    text: "AÇÕES"
                    color: root.colAccent
                    font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                    Layout.leftMargin: 24; Layout.bottomMargin: 6
                }

                SidebarButton {
                    icon: "↓"; label: "Baixar NF-e"
                    description: "Download automático"
                    onClicked: downloadDialog.open()
                }
                SidebarButton {
                    icon: "⇄"; label: "Comparar Notas"
                    description: "DTE vs Domínio"
                    onClicked: compararDialog.open()
                }

                Item { Layout.fillHeight: true }

                // Divisor inferior
                Rectangle {
                    Layout.fillWidth: true; height: 1
                    color: root.colDivider
                    Layout.leftMargin: 20; Layout.rightMargin: 20
                }

                // Status
                RowLayout {
                    Layout.fillWidth: true; Layout.margins: 20; spacing: 8

                    Rectangle {
                        width: 8; height: 8; radius: 4
                        color: root.colAccent

                        SequentialAnimation on opacity {
                            running: true; loops: Animation.Infinite
                            NumberAnimation { to: 0.25; duration: 900 }
                            NumberAnimation { to: 1.0;  duration: 900 }
                        }
                    }

                    Label {
                        text: "Sistema pronto"
                        color: root.colTextMuted; font.pixelSize: 11
                    }
                }
            }
        }

        // ══ Conteúdo principal ════════════════════════════════════════════════
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            spacing: 0

            // ── Header ────────────────────────────────────────────────────────
            Rectangle {
                Layout.fillWidth: true; height: 56
                color: "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 28; anchors.rightMargin: 28

                    Label {
                        text: "Painel Principal"
                        color: root.colText; font.pixelSize: 16; font.bold: true
                    }
                    Item { Layout.fillWidth: true }
                    Label {
                        id: clockLabel
                        color: root.colTextMuted; font.pixelSize: 12; font.letterSpacing: 0.5
                        Timer {
                            interval: 1000; running: true; repeat: true
                            onTriggered: clockLabel.text =
                                Qt.formatDateTime(new Date(), "dd/MM/yyyy  hh:mm:ss")
                            Component.onCompleted: triggered()
                        }
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width; height: 1
                    color: root.colDivider
                }
            }

            // ── Cards ─────────────────────────────────────────────────────────
            RowLayout {
                Layout.fillWidth: true
                Layout.margins: 28; Layout.topMargin: 24
                spacing: 20

                ActionCard {
                    Layout.fillWidth: true; Layout.preferredHeight: 170
                    icon: "↓"; title: "Baixar NF-e"
                    subtitle: "Download automático das notas fiscais eletrônicas via portal SEFAZ"
                    onClicked: downloadDialog.open()
                }
                ActionCard {
                    Layout.fillWidth: true; Layout.preferredHeight: 170
                    icon: "⇄"; title: "Comparar Notas"
                    subtitle: "Confronto entre arquivos DTE e Domínio para detectar divergências"
                    onClicked: compararDialog.open()
                }
            }

            // ── Log ───────────────────────────────────────────────────────────
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                Layout.leftMargin: 28; Layout.rightMargin: 28; Layout.bottomMargin: 28
                color: root.colSidebar; radius: 14
                border.color: root.colDivider; border.width: 1
                clip: true

                ColumnLayout {
                    anchors.fill: parent; spacing: 0

                    // Cabeçalho
                    Rectangle {
                        Layout.fillWidth: true; height: 38
                        color: root.colBg; radius: 14

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width; height: 14
                            color: root.colBg
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 16; anchors.rightMargin: 16

                            Row {
                                spacing: 6
                                Repeater {
                                    model: [
                                        Qt.rgba(0.957, 0.953, 0.988, 0.20),
                                        Qt.rgba(0.957, 0.953, 0.988, 0.12),
                                        root.colAccent
                                    ]
                                    Rectangle {
                                        width: 10; height: 10; radius: 5
                                        color: modelData; opacity: 0.85
                                    }
                                }
                            }

                            Label {
                                text: "Log de Atividades"
                                color: root.colTextMuted
                                font.pixelSize: 11; font.letterSpacing: 1.5; font.bold: true
                                Layout.leftMargin: 10
                            }
                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 60; height: 22; radius: 6
                                color: clrArea.containsMouse ? root.colAccentHover : "transparent"
                                border.color: root.colAccentBorder; border.width: 1
                                Label {
                                    anchors.centerIn: parent; text: "Limpar"
                                    color: root.colTextMuted; font.pixelSize: 10
                                }
                                MouseArea {
                                    id: clrArea; anchors.fill: parent
                                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                    onClicked: logModel.clear()
                                }
                                Behavior on color { ColorAnimation { duration: 120 } }
                            }
                        }
                    }

                    // Lista de entradas
                    ListView {
                        id: logView
                        Layout.fillWidth: true; Layout.fillHeight: true
                        Layout.margins: 12
                        model: logModel; clip: true; spacing: 4
                        verticalLayoutDirection: ListView.BottomToTop

                        delegate: RowLayout {
                            width: logView.width; spacing: 10

                            Label {
                                text: model.time; color: root.colAccent
                                font.pixelSize: 11; font.family: "monospace"; opacity: 0.7
                            }
                            Label {
                                text: model.level
                                color: model.level === "INFO"  ? root.colAccent :
                                       model.level === "ERRO"  ? "#ff5252"      :
                                       model.level === "AVISO" ? "#ffab40"      : root.colTextDim
                                font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                            }
                            Label {
                                text: model.message; color: root.colTextMuted
                                font.pixelSize: 12; Layout.fillWidth: true; elide: Text.ElideRight
                            }
                        }

                        Label {
                            anchors.centerIn: parent
                            visible: logModel.count === 0
                            text: "Nenhuma atividade registrada"
                            color: root.colTextDim; font.pixelSize: 13; font.italic: true
                        }

                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    }
                }
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Componente: SidebarButton
    // ═══════════════════════════════════════════════════════════════════════════
    component SidebarButton: Rectangle {
        property string icon: ""
        property string label: ""
        property string description: ""
        signal clicked()

        Layout.fillWidth: true; height: 58
        color: sbArea.containsMouse ? root.colAccentDim : "transparent"

        Rectangle {
            width: 3; radius: 2
            height: parent.height * 0.5
            anchors.verticalCenter: parent.verticalCenter
            color: root.colAccent
            visible: sbArea.containsMouse
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24; anchors.rightMargin: 16; spacing: 12

            Label {
                text: icon; color: root.colAccent; font.pixelSize: 18
                opacity: sbArea.containsMouse ? 1.0 : 0.7
            }
            ColumnLayout {
                spacing: 1; Layout.fillWidth: true
                Label {
                    text: label
                    color: sbArea.containsMouse ? root.colText : root.colTextMuted
                    font.pixelSize: 13; font.bold: true
                }
                Label {
                    text: description; color: root.colAccent
                    font.pixelSize: 10; opacity: 0.6
                }
            }
        }

        MouseArea {
            id: sbArea; anchors.fill: parent
            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: parent.clicked()
        }

        Behavior on color { ColorAnimation { duration: 130 } }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Componente: ActionCard
    // ═══════════════════════════════════════════════════════════════════════════
    component ActionCard: Rectangle {
        property string icon: ""
        property string title: ""
        property string subtitle: ""
        signal clicked()

        radius: 16
        color: acCard.containsMouse ? "#0d143d" : root.colCard
        border.color: acCard.containsMouse ? root.colAccent : root.colDivider
        border.width: acCard.containsMouse ? 1.5 : 1

        Rectangle {
            width: parent.width; height: 3; anchors.top: parent.top
            color: root.colAccent; radius: 2
            opacity: acCard.containsMouse ? 1.0 : 0.35
            Behavior on opacity { NumberAnimation { duration: 150 } }
        }

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 22; spacing: 12

            Rectangle {
                width: 46; height: 46; radius: 12
                color: root.colAccentDim
                border.color: root.colAccentBorder; border.width: 1
                Label { anchors.centerIn: parent; text: icon; color: root.colAccent; font.pixelSize: 20 }
            }

            Label { text: title; color: root.colText; font.pixelSize: 16; font.bold: true }

            Label {
                text: subtitle; color: root.colTextMuted
                font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true
            }

            Item { Layout.fillHeight: true }

            Rectangle {
                height: 34; Layout.fillWidth: true; radius: 8
                color: acBtn.containsMouse ? root.colAccent : root.colAccentDim
                border.color: root.colAccentBorder
                border.width: acBtn.containsMouse ? 0 : 1

                Label {
                    anchors.centerIn: parent; text: "Executar"
                    color: acBtn.containsMouse ? root.colText : root.colAccent
                    font.pixelSize: 12; font.bold: true; font.letterSpacing: 0.8
                }

                MouseArea {
                    id: acBtn; anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: parent.parent.parent.parent.clicked()
                }
                Behavior on color { ColorAnimation { duration: 150 } }
            }
        }

        MouseArea {
            id: acCard; anchors.fill: parent; hoverEnabled: true
            propagateComposedEvents: true
            onClicked: mouse.accepted = false
        }

        Behavior on color        { ColorAnimation { duration: 150 } }
        Behavior on border.color { ColorAnimation { duration: 150 } }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Componente: FileSelector
    // ═══════════════════════════════════════════════════════════════════════════
    component FileSelector: ColumnLayout {
        property string label: ""
        property string filePath: ""
        signal selectClicked()

        spacing: 6

        Label {
            text: label; color: root.colTextMuted
            font.pixelSize: 12; font.bold: true; font.letterSpacing: 0.5
        }

        RowLayout {
            Layout.fillWidth: true; spacing: 8

            Rectangle {
                Layout.fillWidth: true; height: 38; radius: 8
                color: root.colBg
                border.color: filePath.length > 0 ? root.colAccent : root.colDivider
                border.width: filePath.length > 0 ? 1.5 : 1

                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 8
                    Label {
                        text: filePath.length > 0 ? "✓" : "○"; color: root.colAccent
                        font.pixelSize: 12; opacity: filePath.length > 0 ? 1 : 0.35
                    }
                    Label {
                        text: filePath.length > 0 ? filePath : "Nenhum arquivo selecionado"
                        color: filePath.length > 0 ? root.colText : root.colTextDim
                        font.pixelSize: 12; Layout.fillWidth: true; elide: Text.ElideLeft
                    }
                }

                Behavior on border.color { ColorAnimation { duration: 150 } }
            }

            Rectangle {
                width: 90; height: 38; radius: 8
                color: fsBtn.containsMouse ? root.colAccentHover : root.colAccentDim
                border.color: root.colAccentBorder; border.width: 1

                Label {
                    anchors.centerIn: parent; text: "Selecionar"
                    color: root.colAccent; font.pixelSize: 12; font.bold: true
                }

                MouseArea {
                    id: fsBtn; anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: parent.parent.parent.selectClicked()
                }
                Behavior on color { ColorAnimation { duration: 120 } }
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Dialog: Baixar NF-e
    // ═══════════════════════════════════════════════════════════════════════════
    Dialog {
        id: downloadDialog
        modal: true; standardButtons: DialogButtonBox.NoButton
        width: 420
        x: Math.round((parent.width  - width)  / 2)
        y: Math.round((parent.height - height) / 2)

        background: Rectangle {
            color: root.colSidebar; radius: 16
            border.color: root.colAccentBorder; border.width: 1
        }

        contentItem: ColumnLayout {
            spacing: 16

            RowLayout {
                spacing: 12
                Rectangle {
                    width: 42; height: 42; radius: 10
                    color: root.colAccentDim; border.color: root.colAccentBorder; border.width: 1
                    Label { anchors.centerIn: parent; text: "↓"; color: root.colAccent; font.pixelSize: 20 }
                }
                ColumnLayout {
                    spacing: 2
                    Label { text: "Baixar NF-e";        color: root.colText;      font.pixelSize: 16; font.bold: true }
                    Label { text: "Download via SEFAZ"; color: root.colTextMuted; font.pixelSize: 11 }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: root.colDivider }

            Label {
                text: "O bot irá realizar o download automático de todas as notas fiscais eletrônicas disponíveis no portal. Deseja continuar?"
                color: root.colTextMuted; font.pixelSize: 13
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true; height: 36; radius: 8
                color: root.colAccentDim; border.color: root.colAccentBorder; border.width: 1
                RowLayout {
                    anchors.fill: parent; anchors.margins: 10; spacing: 8
                    Label { text: "ℹ"; color: root.colAccent; font.pixelSize: 14 }
                    Label {
                        text: "Certifique-se de que o certificado digital está instalado."
                        color: root.colTextMuted; font.pixelSize: 11; Layout.fillWidth: true
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 10
                Item { Layout.fillWidth: true }

                Rectangle {
                    width: 100; height: 36; radius: 8
                    color: dlCancel.containsMouse ? root.colAccentDim : "transparent"
                    border.color: root.colDivider; border.width: 1
                    Label { anchors.centerIn: parent; text: "Cancelar"; color: root.colTextMuted; font.pixelSize: 13 }
                    MouseArea {
                        id: dlCancel; anchors.fill: parent
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: downloadDialog.close()
                    }
                    Behavior on color { ColorAnimation { duration: 120 } }
                }

                Rectangle {
                    width: 110; height: 36; radius: 8
                    color: dlConfirm.containsMouse ? "#3a55ff" : root.colAccent
                    Label { anchors.centerIn: parent; text: "Confirmar"; color: root.colText; font.pixelSize: 13; font.bold: true }
                    MouseArea {
                        id: dlConfirm; anchors.fill: parent
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (backend.executarDownload()) {
                                root.appendLog("INFO", "Download de NF-e iniciado com sucesso.")
                                downloadDialog.close()
                            } else {
                                root.appendLog("ERRO", "Falha ao iniciar o download de NF-e.")
                            }
                        }
                    }
                    Behavior on color { ColorAnimation { duration: 120 } }
                }
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Dialog: Comparar Notas
    // ═══════════════════════════════════════════════════════════════════════════
    Dialog {
        id: compararDialog
        modal: true; standardButtons: DialogButtonBox.NoButton
        width: 520
        x: Math.round((parent.width  - width)  / 2)
        y: Math.round((parent.height - height) / 2)

        background: Rectangle {
            color: root.colSidebar; radius: 16
            border.color: root.colAccentBorder; border.width: 1
        }

        contentItem: ColumnLayout {
            spacing: 16

            RowLayout {
                spacing: 12
                Rectangle {
                    width: 42; height: 42; radius: 10
                    color: root.colAccentDim; border.color: root.colAccentBorder; border.width: 1
                    Label { anchors.centerIn: parent; text: "⇄"; color: root.colAccent; font.pixelSize: 20 }
                }
                ColumnLayout {
                    spacing: 2
                    Label { text: "Comparar Notas"; color: root.colText;      font.pixelSize: 16; font.bold: true }
                    Label { text: "DTE vs Domínio";  color: root.colTextMuted; font.pixelSize: 11 }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: root.colDivider }

            Label {
                text: "Selecione os arquivos para iniciar a comparação de notas fiscais."
                color: root.colTextMuted; font.pixelSize: 13
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }

            FileSelector {
                Layout.fillWidth: true; label: "Arquivo DTE"
                filePath: backend.dtePath; onSelectClicked: backend.selecionarDte()
            }
            FileSelector {
                Layout.fillWidth: true; label: "Arquivo Domínio"
                filePath: backend.dominioPath; onSelectClicked: backend.selecionarDominio()
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 10
                Item { Layout.fillWidth: true }

                Rectangle {
                    width: 100; height: 36; radius: 8
                    color: cmpCancel.containsMouse ? root.colAccentDim : "transparent"
                    border.color: root.colDivider; border.width: 1
                    Label { anchors.centerIn: parent; text: "Cancelar"; color: root.colTextMuted; font.pixelSize: 13 }
                    MouseArea {
                        id: cmpCancel; anchors.fill: parent
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: compararDialog.close()
                    }
                    Behavior on color { ColorAnimation { duration: 120 } }
                }

                Rectangle {
                    width: 110; height: 36; radius: 8
                    color: cmpConfirm.containsMouse ? "#3a55ff" : root.colAccent
                    Label { anchors.centerIn: parent; text: "Comparar"; color: root.colText; font.pixelSize: 13; font.bold: true }
                    MouseArea {
                        id: cmpConfirm; anchors.fill: parent
                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (backend.compararNotas()) {
                                root.appendLog("INFO", "Comparação de notas iniciada.")
                                compararDialog.close()
                            } else {
                                root.appendLog("ERRO", "Falha ao iniciar a comparação.")
                            }
                        }
                    }
                    Behavior on color { ColorAnimation { duration: 120 } }
                }
            }
        }
    }

    // ─── Modelo do log ────────────────────────────────────────────────────────
    ListModel { id: logModel }

    function appendLog(level, message) {
        logModel.append({
            time:    Qt.formatTime(new Date(), "hh:mm:ss"),
            level:   level,
            message: message
        })
    }

    MessageDialog {
        id: messageDialog
        buttons: MessageDialog.Ok
    }

    Connections {
        target: backend
        function onMessageEmitted(title, text) {
            var lvl = title.toLowerCase().indexOf("erro")  >= 0 ? "ERRO"  :
                      title.toLowerCase().indexOf("aviso") >= 0 ? "AVISO" : "INFO"
            root.appendLog(lvl, text)
            messageDialog.title = title
            messageDialog.text  = text
            messageDialog.open()
        }
    }

    Component.onCompleted: {
        root.appendLog("INFO", "Bot de Notas Fiscais iniciado com sucesso.")
    }
}
