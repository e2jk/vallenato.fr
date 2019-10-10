/*jslint browser: true, white */
function main(){
  // Create and initialize the map
  var mymap = L.map('map').setView([20,10], 2);
  L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 2,
    maxZoom: 15,
    id: 'mapbox.light',
    accessToken: 'pk.eyJ1IjoidmFsbGVuYXRvLWZyIiwiYSI6ImNqejNncnM2bTAzYzgzY3A2ZWpvNHZodjkifQ.YDKDLobdK27Gr7RKvinyLw'
  }).addTo(mymap);

  // Populate the map and the list on the right side
  populateMapAndList(mymap);
}

function populateMapAndList(mymap){
  var ul = document.createElement('ul');
  document.getElementById('list').appendChild(ul);

  var i = 0;
  for (let loc in locations) {
    if (locations.hasOwnProperty(loc)) {
      // Add marker on the map
      var markerOptions = {
        title: loc, // location name for the browser tooltip that appear on marker hover
        riseOnHover: true, // the marker will get on top of others when you hover the mouse over it.
        keyboard: true // marker can be tabbed to with a keyboard and clicked by pressing enter
      };
      var marker = L.marker([locations[loc].latitude, locations[loc].longitude], markerOptions).addTo(mymap);
      marker._icon.id = "location_marker_" + i;
      marker.addEventListener("click", function(){ overlay_on("list_overlay", loc); });
      marker.addEventListener("mouseover", function(evt){ marker_hover(evt.target._icon.id, "highlighted"); });
      marker.addEventListener("mouseout", function(evt){ marker_hover(evt.target._icon.id, ""); });

      // Update list on the right side
      var li = document.createElement('li');
      li.id = "location_list_" + i;
      li.addEventListener("click", function(){ overlay_on("list_overlay", loc); });
      ul.appendChild(li);
      li.innerHTML = loc;

      // Increment marker ID
      i++;
    }
  }
}

function overlay_on(id, loc) {
  document.getElementById(id).style.display = "block";
  document.getElementById("list_location").innerHTML = loc;

  var ul = document.getElementById("list_videos");
  // Empty the list, if populated before
  ul.innerHTML = "";

  for (let vid in locations[loc]["videos"]) {
    // Show all the videos taken at that location
    var li = document.createElement('li');
    ul.appendChild(li);
    vid_title = locations[loc]["videos"][vid].title;
    vid_thumbnail_url = locations[loc]["videos"][vid].thumbnail.url;
    li.innerHTML = "<p>" + vid_title + "</p><img src='" + vid_thumbnail_url + "'/>"
  }
}

function overlay_off(id) {
  // Hide the overlay
  document.getElementById(id).style.display = "none";
}

function marker_hover(marker_id, highlight) {
  var location_list_id = marker_id.replace("location_marker_", "location_list_");
  document.getElementById(location_list_id).className = highlight;
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

main();
