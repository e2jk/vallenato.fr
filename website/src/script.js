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

for (let loc in locations) {
    if (locations.hasOwnProperty(loc)) {
        // Add marker on the map
        var marker = L.marker([locations[loc].latitude, locations[loc].longitude]).addTo(mymap);
        marker.bindPopup(loc);

        // Update list on the right side
        var li = document.createElement('li');
        li.addEventListener("click", function(){ overlay_on("list_overlay", loc); });
        ul.appendChild(li);
        li.innerHTML = loc;
    }
}

function overlay_on(id, loc) {
    document.getElementById(id).style.display = "block";
    document.getElementById("list_location").innerHTML = loc;

    var ul = document.getElementById("list_videos");
    // Empty the list, if populated before
    ul.innerHTML = "";

    for (let vid in locations[loc]["videos"]) {
      var li = document.createElement('li');
      //li.addEventListener("click", function(){ overlay_on("list_overlay", loc); });
      ul.appendChild(li);
      vid_title = locations[loc]["videos"][vid].title;
      vid_thumbnail_url = locations[loc]["videos"][vid].thumbnail.url;
      li.innerHTML = "<p>" + vid_title + "</p><img src='" + vid_thumbnail_url + "'/>"
      console.log(locations[loc]["videos"][vid]);
    }
}

function overlay_off(id) {
    document.getElementById(id).style.display = "none";
}

document.onkeydown = function(evt) {
    evt = evt || window.event;
    var isEscape = false;
    if ("key" in evt) {
        isEscape = (evt.key === "Escape" || evt.key === "Esc");
    } else {
        isEscape = (evt.keyCode === 27);
    }
    if (isEscape) {
        overlay_off("list_overlay");
    }
};
