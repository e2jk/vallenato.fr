/*jslint browser: true, white */
var video_location = null;
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

  // Handle overlay closing via cross icon
  document.getElementById('list_overlay_close').addEventListener("click", close_current_overlay);
  document.getElementById('video_overlay_close').addEventListener("click", close_current_overlay);

  // Check if we started with another page than the root
  check_initial_page();
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
      marker.addEventListener("click", function(){ navigate_to_location(loc); });
      marker.addEventListener("mouseover", function(evt){ marker_hover(evt.target._icon.id, "highlighted"); });
      marker.addEventListener("mouseout", function(evt){ marker_hover(evt.target._icon.id, ""); });

      // Update list on the right side
      var li = document.createElement('li');
      li.id = "location_list_" + i;
      li.addEventListener("click", function(){ navigate_to_location(loc); });
      ul.appendChild(li);
      li.innerHTML = loc;

      // Increment marker ID
      i++;
    }
  }
}

function check_initial_page() {
  if("" === window.location.hash){
    // Nothing to do, it's the home page
  } else {
    // Identify for which page this slug is
    var slug_found = false;
    // Check if it's a location's slug
    for (let loc in locations) {
      if (locations.hasOwnProperty(loc)) {
        if("#" + locations[loc].slug === window.location.hash){
          slug_found = true;
          show_location_overlay(loc);
          break;
        }
      }
    }

    if (!slug_found) {
      // Check if it's an individual video's slug
      for (let loc in locations) {
        if (locations.hasOwnProperty(loc)) {
          for (let vid in locations[loc]["videos"]) {
            if (locations[loc]["videos"].hasOwnProperty(vid)) {
              let vid_id = locations[loc]["videos"][vid].id;
              let vid_title_slug = locations[loc]["videos"][vid].slug;
              if("#" + vid_title_slug + "/" + vid_id === window.location.hash){
                slug_found = true;
                // First load that location's overlay, to handle closing the video overlay nicely
                show_location_overlay(loc);
                // Keep a reference to that video's location for history handling
                video_location = loc;
                // Load that page's video
                // Note: autoplay will likely be disabled by the browser, as it won't have detected an explicit user action
                show_video_overlay(vid_id, vid_title_slug);
                break;
              }
            }
          }
          if(slug_found) {
            break;
          }
        }
      }
    }

    if (!slug_found) {
      // Invalid slug, redirecting to home page
      window.location = "/";
    }
  }
}

function update_history_for_home() {
  // Update the URL for that location
  history.pushState({"type": "home"}, "Vallenato.fr", "#");
}

function navigate_to_location(loc) {
  update_history_for_location(loc);
  show_location_overlay(loc);
}

function update_history_for_location(loc) {
  // Update the URL for that location
  history.pushState({"type": "location", "loc": loc}, loc, "#" + locations[loc]["slug"]);
}

function show_location_overlay(loc) {
  overlay_show("list_overlay");
  // In case a video was shown
  overlay_hide("video_overlay");
  // Also remove the iframe (in case the YouTube video is playing)
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = "";

  document.getElementById("list_location").innerHTML = loc;

  var ul = document.getElementById("list_videos");
  // Empty the list, if populated before
  ul.innerHTML = "";

  for (let vid in locations[loc]["videos"]) {
    if (locations[loc]["videos"].hasOwnProperty(vid)) {
      // Show all the videos taken at that location
      var li = document.createElement('li');
      ul.appendChild(li);
      let vid_id = locations[loc]["videos"][vid].id;
      vid_title = locations[loc]["videos"][vid].title;
      let vid_title_slug = locations[loc]["videos"][vid].slug;
      vid_thumbnail_url = locations[loc]["videos"][vid].thumbnail.url;
      li.innerHTML = "<p id='vid_title_" + vid_id + "'>" + vid_title + "</p><img id='vid_img_" + vid_id + "' src='" + vid_thumbnail_url + "'/>"
      // Handle clicks on the title or the image to play the video
      document.getElementById("vid_title_" + vid_id).addEventListener("click", function(){ navigate_to_video(vid_id, vid_title_slug, loc); });
      document.getElementById("vid_img_" + vid_id).addEventListener("click", function(){ navigate_to_video(vid_id, vid_title_slug, loc); });
    }
  }
}

function overlay_show(id) {
  // Show the overlay
  document.getElementById(id).style.display = "block";
}

function overlay_hide(id) {
  // Hide the overlay
  document.getElementById(id).style.display = "none";
}

function marker_hover(marker_id, highlight) {
  var location_list_id = marker_id.replace("location_marker_", "location_list_");
  document.getElementById(location_list_id).className = highlight;
}

function navigate_to_video(id, title_slug, loc) {
  // Keep a reference to that video's location for history handling
  video_location = loc;
  update_history_for_video(id, title_slug);
  show_video_overlay(id, title_slug);
}

function update_history_for_video(id, title_slug) {
  // Update the URL for that video
  history.pushState({"type": "video", "id": id, "title_slug": title_slug}, id, "#" + title_slug + "/" + id);
}

function show_video_overlay(id, title_slug) {
  // Update the video overlay with the url for this video
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = `<iframe id="video_overlay_iframe" width="560" height="315" src="https://www.youtube.com/embed/` + id + `?autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`
  // Show the overlay containing the YouTube Embed iframe
  overlay_show("video_overlay");
  // Hide the overlay containing the list of videos at that location
  overlay_hide("list_overlay");
}

function show_home_page() {
  // Hide both location and video overlays
  overlay_hide("list_overlay");
  overlay_hide("video_overlay");
  // Also remove the iframe (in case the YouTube video is playing)
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = "";
}

function close_current_overlay() {
  if ("block" === document.getElementById("list_overlay").style.display) {
    // If the Location List overlay is shown, go to the home page
    show_home_page();
    // Add an entry to the history, back to home
    update_history_for_home();
  } else if("block" === document.getElementById("video_overlay").style.display) {
    // If the Video overlay is shown, hide it and show the Location List overlay
    overlay_show("list_overlay");
    overlay_hide("video_overlay");
    // Also remove the iframe (in case the YouTube video is playing)
    document.getElementById("video_overlay_iframe_placeholder").innerHTML = "";
    // Add an entry to the history, back to the location's page
    update_history_for_location(video_location);
  }
}

function key_down(evt) {
  evt = evt || window.event;
  var isEscape = false;
  if ("key" in evt) {
    isEscape = (evt.key === "Escape" || evt.key === "Esc");
  } else {
    isEscape = (evt.keyCode === 27);
  }
  if (isEscape) {
    close_current_overlay();
  }
};

function URL_changed() {
  if(!window.location.hash) {
    // No hash, go to the home page
    show_home_page();
  } else {
    if (history.state && history.state.hasOwnProperty("type")) {
      // Use back and forward buttons
      if("location" === history.state.type) {
        show_location_overlay(history.state.loc);
      } else if ("video" === history.state.type) {
        show_video_overlay(history.state.id, history.state.title_slug);
      } else {
        // Fallback to the home page (should never happen)
        show_home_page();
      }
    } else {
      // Probably a hand-typed hash URL
      check_initial_page();
    }
  }
};

document.onkeydown = key_down;
window.onhashchange = URL_changed;

main();
