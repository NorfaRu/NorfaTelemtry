import QtQuick 2.15
// import QtQuick.Controls 2.15 // Removed as not used in the new code
import QtPositioning 5.15
import QtLocation 5.15

// MapView.qml - Rewritten based on provided snippet
Item {
    id: mapRoot // Root item with an ID
    anchors.fill: parent

    // --- Properties for coordinates from Python ---
    // Initialize to 0,0 so marker is initially hidden. Python should set these to actual values.
    property real latitude: 0.0
    property real longitude: 0.0

    // Optional: Background rectangle if needed (kept from original for visual consistency)
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#1a1a1a" }
            GradientStop { position: 1.0; color: "#252525" }
        }
    }

    Map {
        id: mapView
        anchors.fill: parent
        plugin: Plugin { id: osmPlugin; name: "osm" } // Using the osm plugin
        // Center the map initially at a default location (e.g., St. Petersburg).
        // The center will be updated via Connections when valid coordinates arrive.
        center: QtPositioning.coordinate(59.94, 30.31) // Default initial center
        zoomLevel: 14 // Default zoom level

        // --- Marker ---
        MapQuickItem {
            id: mapMarker
            // Anchor point at the bottom-center of the marker image
            anchorPoint.x: markerImage.width / 2
            anchorPoint.y: markerImage.height
            // Marker position is bound to the root item's properties (initially 0,0)
            coordinate: QtPositioning.coordinate(mapRoot.latitude, mapRoot.longitude)

            sourceItem: Image {
                id: markerImage
                source: Qt.resolvedUrl("marker.png") // Marker icon file
                // Set size explicitly if needed, otherwise uses image's natural size
                width: 36
                height: 36
                smooth: true
            }
            // Make marker visible only when coordinates are valid (not 0,0)
            // This ensures the marker is hidden until valid coordinates are received from Python.
            visible: mapRoot.latitude !== 0.0 || mapRoot.longitude !== 0.0
            z: 1 // Ensure marker is above map tiles
        }

        // Optional: Add zoom/pan behaviors back if needed
        // Behavior on zoomLevel { NumberAnimation { duration: 400; easing.type: Easing.InOutQuad } }
        // Behavior on center { CoordinateAnimation { duration: 400; easing.type: Easing.InOutQuad } } // Requires QtLocation 5.6+
    }

     Connections {
         target: mapRoot
         function onLatitudeChanged() {
             if (mapRoot.latitude !== 0.0 || mapRoot.longitude !== 0.0) {
                 // Use CoordinateAnimation for smoother transition if available and desired
                 // mapView.center = QtPositioning.coordinate(mapRoot.latitude, mapRoot.longitude) // Direct jump
                 mapView.pan(mapView.center.longitude - mapRoot.longitude, mapView.center.latitude - mapRoot.latitude) // Pan to new center
             }
         }
         function onLongitudeChanged() {
             if (mapRoot.latitude !== 0.0 || mapRoot.longitude !== 0.0) {
                 // Use CoordinateAnimation for smoother transition if available and desired
                 // mapView.center = QtPositioning.coordinate(mapRoot.latitude, mapRoot.longitude) // Direct jump
                 mapView.pan(mapView.center.longitude - mapRoot.longitude, mapView.center.latitude - mapRoot.latitude) // Pan to new center
             }
         }
         // Note: The marker's coordinate is already bound, so it updates automatically.
         // The visibility is also bound and will become true when lat/lon are non-zero.
     }

    // Keep MouseArea for panning and zooming if manual interaction is desired
    MouseArea {
        id: dragArea
        anchors.fill: parent
        property point lastPosition
        property bool isDragging: false

        onPressed: function(event) {
            lastPosition = Qt.point(event.x, event.y)
            isDragging = true
        }

        onPositionChanged: function(event) {
            if (isDragging) {
                var dx = event.x - lastPosition.x
                var dy = event.y - lastPosition.y
                mapView.pan(-dx, -dy) // Use the Map's pan method
                lastPosition = Qt.point(event.x, event.y)
            }
        }

        onReleased: function(event) {
            isDragging = false
        }

        onWheel: function(event) {
            var zoomFactor = 1.0
            if (event.angleDelta.y > 0)
                mapView.zoomLevel = Math.min(mapView.zoomLevel + zoomFactor, 20)
            else
                mapView.zoomLevel = Math.max(mapView.zoomLevel - zoomFactor, 2)
        }
    }

    // Keep zoom buttons if desired
    Column {
        spacing: 8
        anchors {
            right: parent.right; top: parent.top
            rightMargin: 16; topMargin: 16
        }
        Rectangle {
            width: 40; height: 40; radius: 8
            color: "#333333"; opacity: 0.8
            border.color: "#555555"; border.width: 1
            MouseArea {
                anchors.fill: parent
                onClicked: function() { mapView.zoomLevel = Math.min(mapView.zoomLevel + 1, 20) }
                hoverEnabled: true
                onEntered: function() { parent.color = "#444444" }
                onExited: function() { parent.color = "#333333" }
            }
            Text { text: "+"; anchors.centerIn: parent; font.pixelSize: 24; color: "#ffffff" }
        }
        Rectangle {
            width: 40; height: 40; radius: 8
            color: "#333333"; opacity: 0.8
            border.color: "#555555"; border.width: 1
            MouseArea {
                anchors.fill: parent
                onClicked: function() { mapView.zoomLevel = Math.max(mapView.zoomLevel - 1, 2) }
                hoverEnabled: true
                onEntered: function() { parent.color = "#444444" }
                onExited: function() { parent.color = "#333333" }
            }
            Text { text: "–"; anchors.centerIn: parent; font.pixelSize: 24; color: "#ffffff" }
        }
    }

    // Note: The signal 'updateCoordinate' and its handler 'onUpdateCoordinate'
    // are removed as the new approach uses property bindings (latitude, longitude)
    // set from Python instead of a signal emitted from QML.
    // Python code should now set mapRoot.latitude and mapRoot.longitude properties.
}