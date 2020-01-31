var map = null;
var directionService = null;
var directionRenderer = null;
var live_loc_marker = null, destination_marker = null;
var Robocon_lab;
var all_locations = null;
var location_now = { latitude: null, longitude: null };
var bounds = null;

window.addEventListener('load', loadComponents);

var Location = function (latitude, longitude, pretty_name, description, type) {
    this.latitude = latitude;
    this.longitude = longitude;
    this.pretty_name = pretty_name;
    this.description = description;
    this.loc_type = type;
}

function initMap() {
    Robocon_lab = new google.maps.LatLng(12.823, 80.043);
    var map_style = JSON.parse(httpGet('/static/mapStyle.json'));
    var mapOptions = {
        zoom: 19,
        styles: map_style,
        center: Robocon_lab
    }
    directionService = new google.maps.DirectionsService;
    directionRenderer = new google.maps.DirectionsRenderer;
    map = new google.maps.Map(
        document.getElementById('map'), mapOptions);
    directionRenderer.setMap(map);

    live_loc_marker = new google.maps.Marker({
        position: Robocon_lab,
        map: map,
        icon: '/static/blue-dot.png',
        title: 'Live Location'
    });
    destination_marker = new google.maps.Marker({
        position: null,
        map: map,
        title: "Destination"
    });
    var updater = function () {
        var data = new google.maps.LatLng(document.getElementById('lat').value, document.getElementById('long').value);
        calcRoute(directionService, directionRenderer, data);
        google.maps.event.trigger(map, 'resize');
    };
    // var data = new google.maps.LatLng(document.getElementById('lat').value,document.getElementById('long').value);
    document.getElementById('start-button').addEventListener('click', updater);
}

function calcRoute(directionService, directionRenderer, data) {
    // console.log("hi");
    var Robocon_lab = new google.maps.LatLng(12.823, 80.043);
    directionService.route({
        origin: Robocon_lab,
        destination: data,
        travelMode: 'DRIVING'
    }, function (response, status) {
        if (status == 'OK') {
            directionRenderer.setDirections(response);
        }
        else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}


function httpGet(theUrl) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", theUrl, false); // false for synchronous request
    xhr.send(null);
    return xhr.responseText;
}

function httpPOST(theUrl, json) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", theUrl, false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(json));
    return { response: xhr.response, status: xhr.status };
}

function updateSensorReadings() {
    var response = JSON.parse(httpGet('./api/sensor-data?sensor=gps'));
    document.getElementById('sensor-latitude').textContent = response.lat;
    document.getElementById('sensor-longitude').textContent = response.lng;
    location_now.latitude = response.lat;
    location_now.longitude = response.lng;
    document.getElementById('sensor-sats').textContent = response.sat;
    document.getElementById('sensor-heading').textContent = JSON.parse(httpGet('./api/sensor-data?sensor=compass')).heading;
}
function updateDropList() {
    var sel = document.getElementById('end');
    sel.innerHTML = "";
    var length = all_locations.length;
    var index = 0, i;
    for (var i = 0; i < length; i++) {
        if (all_locations[i].pretty_name != null) {
            var option = document.createElement("OPTION");
            option.innerText = all_locations[i].pretty_name;
            option.value = i;
            sel.add(option);
            index += 1;
        }
    }
    sel.selectedIndex = -1;
}

function fetchAllLocations() {
    response = JSON.parse(httpGet('./api/location'));
    all_locations = response;
}

function pasteCurrentLocation() {
    document.getElementById('new-loc-lat').value = location_now.latitude;
    document.getElementById('new-loc-lng').value = location_now.longitude;
}

function setDestAndVelocity() {
    var set_lat = parseFloat(document.getElementById('lat').value);
    var set_lng = parseFloat(document.getElementById('long').value);
    var set_vel = parseFloat(document.getElementById('velocity').value);
    if (isNaN(set_lng) || isNaN(set_lng) || isNaN(set_vel)) {
        alert('Destination coordinates or velocity not in proper format.');
        return;
    }
    destination_marker.setPosition({ lat: set_lat, lng: set_lng });
    var response = httpPOST('./api/set/destination', { latitude: set_lat, longitude: set_lng });
    var response2 = httpPOST('./api/set/velocity', { velocity: set_vel });
    if (response.status != 200 || response2.status != 200) {
        alert('Failed to set destination. Check console for info.');
        console.log(response);
    }
    bounds = new google.maps.LatLngBounds();
    bounds.extend(live_loc_marker.position);
    bounds.extend({ lat: set_lat, lng: set_lng });
    map.fitBounds(bounds);
}

function addNewLocation() {
    var lat_input = parseFloat(document.getElementById('new-loc-lat').value);
    var lng_input = parseFloat(document.getElementById('new-loc-lng').value);
    var desc_input = document.getElementById('new-loc-desc').value;
    var pname_input = document.getElementById('new-loc-pname').value;
    var type_input = document.getElementById('new-loc-type').value;
    if (isNaN(lat_input) || isNaN(lng_input)) {
        alert('Latitude or Longitude not in proper format');
        return;
    }
    var location = new Location(lat_input, lng_input, pname_input, desc_input, type_input);
    response = httpPOST('./api/location', location);
    if (response.status == 200) {
        alert('New Location Added');
        fetchAllLocations();
        updateDropList();
    }
    else {
        alert('Error Occured in adding Location. Check console for output.');
        console.log(response);
    }
}

function selectLocation() {
    var i = document.getElementById('end').value;
    document.getElementById('lat').value = all_locations[i].latitude;
    document.getElementById('long').value = all_locations[i].longitude;
}

function loadComponents() {
    document.getElementById("webcam-stream").src = window.location.origin + ':8081';
    updateSensorReadings();
    fetchAllLocations();
    updateDropList();
}
