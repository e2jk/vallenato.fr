/*jslint browser: true, white */
var mymap = L.map('map').setView([20,10], 2);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 2,
    maxZoom: 15,
    id: 'mapbox.light',
    accessToken: 'pk.eyJ1IjoidmFsbGVuYXRvLWZyIiwiYSI6ImNqejNncnM2bTAzYzgzY3A2ZWpvNHZodjkifQ.YDKDLobdK27Gr7RKvinyLw'
}).addTo(mymap);

var ul = document.createElement('ul');
document.getElementById('list').appendChild(ul);

for (var loc in locations) {
    if (locations.hasOwnProperty(loc)) {
        // Add marker on the map
        var marker = L.marker([locations[loc].latitude, locations[loc].longitude]).addTo(mymap);
        marker.bindPopup(loc);
        // Update list on the right side

        var li = document.createElement('li');
        ul.appendChild(li);
        li.innerHTML = loc;
    }
}
