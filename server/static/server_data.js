var response;
var test;
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}
function updateSensorReadings()
{
    response = JSON.parse(httpGet("http://localhost:8080/api/sensor-data?sensor=gps"));
    test = document.getElementById('long').value;
}


