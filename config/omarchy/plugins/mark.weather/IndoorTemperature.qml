import QtQuick
import Quickshell.Io
import qs.Commons
import qs.Ui

Item {
  id: root
  property var bar: null
  property var reading: ({})
  property double now: Date.now() / 1000
  readonly property bool fresh: reading.ok === true && now - Number(reading.observed_at || 0) < 1200
  visible: fresh
  implicitWidth: fresh ? button.implicitWidth : 0
  implicitHeight: button.implicitHeight

  function refresh() {
    now = Date.now() / 1000
    if (!reader.running) reader.running = true
  }
  Component.onCompleted: refresh()

  Timer {
    interval: 900000
    repeat: true
    running: true
    onTriggered: root.refresh()
  }
  Timer {
    interval: 30000
    repeat: true
    running: true
    onTriggered: {
      root.now = Date.now() / 1000
      if (root.now - Number(root.reading.attempted_at || 0) >= 900) root.refresh()
    }
  }
  Process {
    id: reader
    command: ["/usr/bin/python", Qt.resolvedUrl("read-temperature.py").toString().replace(/^file:\/\//, "")]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try { root.reading = JSON.parse(text) }
        catch (e) { root.reading = ({ok: false, error: "Unable to read sensor"}) }
        root.now = Date.now() / 1000
      }
    }
  }
  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.fresh ? "Indoor " + Number(root.reading.temperature_f).toFixed(1) + "°F" : ""
    fontSize: Style.font.body
    tooltipText: root.fresh
      ? "Aranet4 · " + Number(root.reading.temperature_c).toFixed(1) + "°C\nHumidity " + root.reading.humidity + "% · CO₂ " + root.reading.co2 + " ppm\nBattery " + root.reading.battery + "%\nReceived " + new Date(root.reading.observed_at * 1000).toLocaleTimeString() + " · refreshes every 15 minutes"
      : ""
  }
}
