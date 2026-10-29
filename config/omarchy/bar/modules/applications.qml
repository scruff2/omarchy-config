import QtQuick
import Quickshell.Hyprland

Item {
  id: root
  property var bar
  property string moduleName
  property var settings
  readonly property int count: Hyprland.toplevels.values.length
  readonly property real buttonWidth: Math.min(150, 500 / Math.max(1, count))
  implicitWidth: row.width
  implicitHeight: bar ? bar.barSize : 26

  Row {
    id: row
    spacing: 4
    Repeater {
      model: Hyprland.toplevels
      Rectangle {
        id: button
        required property var modelData
        width: root.buttonWidth
        height: root.implicitHeight
        radius: 4
        color: modelData.activated ? Qt.rgba(1, 1, 1, 0.18) : (mouse.containsMouse ? Qt.rgba(1, 1, 1, 0.10) : "transparent")
        Text {
          anchors.fill: parent
          anchors.leftMargin: 8
          anchors.rightMargin: 8
          verticalAlignment: Text.AlignVCenter
          text: button.modelData.title || button.modelData.lastIpcObject.class || "Window"
          textFormat: Text.PlainText
          elide: Text.ElideRight
          color: root.bar ? root.bar.foreground : "white"
          font.family: root.bar ? root.bar.fontFamily : "sans-serif"
          font.pixelSize: 12
        }
        MouseArea {
          id: mouse
          anchors.fill: parent
          hoverEnabled: true
          cursorShape: Qt.PointingHandCursor
          onClicked: {
            var address = String(button.modelData.address)
            if (!/^(0x)?[0-9a-fA-F]+$/.test(address)) return
            if (address.indexOf("0x") !== 0) address = "0x" + address
            if (root.bar) root.bar.run("~/.config/omarchy/scripts/window-control activate " + address)
          }
          onEntered: if (root.bar) root.bar.showTooltip(button, button.modelData.title || button.modelData.lastIpcObject.class)
          onExited: if (root.bar) root.bar.hideTooltip(button)
        }
      }
    }
  }
}
