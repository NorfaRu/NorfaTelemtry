// gradient.qml
import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    anchors.fill: parent

    Rectangle {
        id: bg
        anchors.fill: parent

        // Применение градиента с новыми цветами
        gradient: Gradient {
            GradientStop { id: stop0; position: 0.0; color: Qt.rgba(82/255, 82/255, 92/255, 1) }  // #52525C
            GradientStop { id: stop1; position: 0.85; color: Qt.rgba(39/255, 74/255, 53/255, 1) }  // #274A35
        }

        // Анимация — смещаем вторую точку градиента туда-сюда
        SequentialAnimation {
            loops: Animation.Infinite

            NumberAnimation {
                target: stop1
                property: "position"
                from: 0.0; to: 1.0
                duration: 4000
                easing.type: Easing.InOutQuad
            }
            NumberAnimation {
                target: stop1
                property: "position"
                from: 1.0; to: 0.0
                duration: 4000
                easing.type: Easing.InOutQuad
            }
        }
    }
}
