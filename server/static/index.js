var map = null;
var directionService = null;
var directionRenderer = null;
var Robocon_lab;
var response_readings;
var response_dropDown;
var test;
var sel;
var output;
var i;

window.addEventListener('load', getValuesFromServer);
window.addEventListener('load', updateSensorReadings);
window.addEventListener('load', updateDropList);

function initMap()
{
    Robocon_lab = new google.maps.LatLng(12.823, 80.043);
    var Tech_Park = new google.maps.LatLng(12.823, 80.043);
    
    var mapOptions = {
        zoom:19,
        center: Robocon_lab
    }
    
    
            
    

    directionService = new google.maps.DirectionsService;
    directionRenderer = new google.maps.DirectionsRenderer;
    map = new google.maps.Map(
        document.getElementById('map'), mapOptions);
    directionRenderer.setMap(map);

    getValuesFromServer();
    var currentPosition = {lat: response_readings.lat,lng: response_readings.lng};
	var marker = new google.maps.Marker({
			position: currentPosition,
			map: map,
			title: 'I am here'
            });
    marker.setMap(map);

    var updater = function(){
        var data = new google.maps.LatLng(document.getElementById('lat').value,document.getElementById('long').value);
        calcRoute(directionService, directionRenderer, data);
        google.maps.event.trigger(map, 'resize');
      };

    // var data = new google.maps.LatLng(document.getElementById('lat').value,document.getElementById('long').value);
    document.getElementById('starting').addEventListener('click', updater);
    
    
    
}

function calcRoute(directionService, directionRenderer, data)
{
    // console.log("hi");
    var Robocon_lab = new google.maps.LatLng(12.823, 80.043);
    directionService.route({
        origin: Robocon_lab,
        destination: data,
        travelMode: 'DRIVING'
    }, function(response, status){
        if(status == 'OK')
        {
            directionRenderer.setDirections(response);
        }
        else
        {
            window.alert('Directions request failed due to '+ status);
        }
    });
}


function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function getValuesFromServer()
{
    response_readings = JSON.parse(httpGet("http://localhost:8080/api/sensor-data?sensor=gps"));
    response_dropDown = JSON.parse(httpGet("http://localhost:8080/api/location"));
    // response_readings = httpGet("http://localhost:8080/api/sensor-data?sensor=gps");
    
}
function updateSensorReadings()
{
    document.getElementById('latitude_input').innerText = response_readings.lat;
    document.getElementById('longitude_input').innerText = response_readings.lng;
    document.getElementById('compass_input').innerText = response_readings.sat;
}
function updateDropList()
{
    
    sel = document.getElementById('end');
    var length = sel.length;
    for(i = 0; i<length; i++)
    {
        sel.options[sel.value = i].innerText = response_dropDown[i].description;
    }
    
}
function httpPOST(theUrl)
{
    var xhr = new XMLHttpRequest();
    xhr.open("POST", theUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
            latitude:12.00,
            longitude:80.00,
            loc_type:"JUNCTION",
            pretty_name:"Y zone",
            description:"Sixth location"
    }));
}


