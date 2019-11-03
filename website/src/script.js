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
  if("" !== window.location.hash){
    check_valid_slug();
  }
}

function populateMapAndList(mymap){
  var list_content = "";
  var countries = {};
  var num_locations = 0;
  var num_videos = 0;
  for (let loc in locations) {
    if (locations.hasOwnProperty(loc)) {
      // Add marker on the map
      var markerOptions = {
        title: loc, // location name for the browser tooltip that appear on marker hover
        riseOnHover: true, // the marker will get on top of others when you hover the mouse over it.
        keyboard: true // marker can be tabbed to with a keyboard and clicked by pressing enter
      };
      var marker = L.marker([locations[loc].latitude, locations[loc].longitude], markerOptions).addTo(mymap);
      marker.addEventListener("click", function(){ navigate_to_location(loc); });

      // Group locations per country
      c = loc.split(", ").pop(); // That location's country name
      if (!countries.hasOwnProperty(c)) {
        countries[c] = [];
      }
      countries[c].push(loc);
      num_videos += locations[loc].videos.length;
      num_locations++;
    }
  }

  // Sort countries alphabetically
  countries_sorted = [];
  for (let c in countries) {
    if (countries.hasOwnProperty(c)) {
      countries_sorted.push(c);
    }
  }
  countries_sorted.sort();
  // Add the entire world
  countries["Mundo entero"] = new Array(num_locations);
  countries_sorted.push("Mundo entero");

  var num_countries = 0;
  for (let i in countries_sorted) {
    c = countries_sorted[i];
    if (countries.hasOwnProperty(c)) {
      list_content += `<div class="card">
      <div class="card-header country-card" id="heading` + num_countries + `" data-toggle="collapse" data-target="#collapse` + num_countries + `" aria-expanded="false" aria-controls="collapse` + num_countries + `">
        <div class="mb-0">` + c + `</div>
      </div>
      `;
      list_content += `<div id="collapse` + num_countries + `" class="collapse list-group list-group-flush" aria-labelledby="heading` + num_countries + `" data-parent="#list">`;
      if ("Mundo entero" === c) {
        list_content += `<a href="#mundo-entero" class="card-body list-group-item list-group-item-action d-flex justify-content-between align-items-center">Mundo entero<span class="badge badge-primary badge-pill badge-dark">` + num_videos + `</span><span class="sr-only"> videos</span></a>`;
      } else {
        for (let l in countries[c]) {
          if (countries[c].hasOwnProperty(l)) {
            loc = countries[c][l];
            // Remove the country name to display the location name
            loc_parts = loc.split(", ");
            loc_parts.pop();
            loc_short_name = loc_parts.join(", ");
            list_content += `<a href="#` + locations[loc]["slug"] + `" class="card-body list-group-item list-group-item-action d-flex justify-content-between align-items-center">` + loc_short_name + `<span class="badge badge-primary badge-pill badge-dark">` + locations[loc].videos.length + `</span><span class="sr-only"> videos</span></a>`;
          }
        }
      }
      list_content += `
        </div>
      </div>`;
      num_countries++;
    }
  }
  // Populate the locations list
  document.getElementById('list').innerHTML = list_content;
}

function check_valid_slug() {
  // Identify for which page this slug is
  var slug_found = false;

  // Check if it's a location's slug
  if("#mundo-entero" === window.location.hash){
    slug_found = true;
    show_location_overlay("Mundo entero");
    return;
  }

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
              show_video_overlay(vid_id, vid_title_slug, locations[loc]["videos"][vid].title);
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
  document.getElementById("list_videos").innerHTML = "";
  overlay_show("list_overlay");
  // In case a video was shown
  overlay_hide("video_overlay");
  // Also remove the iframe (in case the YouTube video is playing)
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = "";
  // Update page title and header
  document.title = loc + " - El Vallenatero Francés";
  document.getElementById("list_location").innerHTML = loc;

  // Populate the global array if displaying the entire world for the first time
  if ("Mundo entero" === loc && undefined === locations[loc]) {
    var global_videos = new Array();
    for (let loc2 in locations) {
      if (locations.hasOwnProperty(loc2)) {
        global_videos = global_videos.concat(locations[loc2]["videos"]);
      }
    }
    // Sort by publishedAt timestamp (most recent first)
    global_videos.sort((a,b) => (a.publishedAt < b.publishedAt) ? 1 : ((a.publishedAt > b.publishedAt) ? -1 : 0));
    locations[loc] = {};
    locations[loc]["videos"] = global_videos;
  }

  // Show all the videos taken at that location
  var content = "";
  var num_vid = 0;
  var vid_array = [];
  for (let vid in locations[loc]["videos"]) {
    if (locations[loc]["videos"].hasOwnProperty(vid)) {
      let vid_id = locations[loc]["videos"][vid].id;
      let vid_title = locations[loc]["videos"][vid].title;
      let vid_title_slug = locations[loc]["videos"][vid].slug;
      let vid_thumbnail_url = locations[loc]["videos"][vid].thumbnail.url;
      let vid_description = locations[loc]["videos"][vid].description.replace(/\n/g, "<br/>");
      // Replace URLs in the description with clickable links
      if (vid_description.startsWith("Para aprender a tocar esta canción: https://vallenato.fr/aprender/")) {
        vid_description = vid_description.replace(/Para aprender a tocar esta canción: https:\/\/vallenato.fr(\/aprender\/.*\.html)/, `<a href="$1" onClick="event.stopPropagation();">Aprender a tocar esta canción</a>.`);
      }
      if (vid_description.startsWith("Para aprender a tocar estas canciones: https://vallenato.fr/aprender/")) {
        vid_description = vid_description.replace(/Para aprender a tocar estas canciones: https:\/\/vallenato.fr(\/aprender\/.*\.html) y https:\/\/vallenato.fr(\/aprender\/.*\.html)/, `Aprender a tocar estas canciones: <a href="$1" onClick="event.stopPropagation();">1</a> y <a href="$2" onClick="event.stopPropagation();">2</a>.`);
      }
      let vid_publishedAt = locations[loc]["videos"][vid].publishedAt.substring(0, 10);
      content += `<div id="vid_card_` + vid_id + `" class="card mb-3 vid_card" style="max-width: 17rem;">
        <img id="vid_img_` + vid_id + `" src="` + vid_thumbnail_url + `" class="card-img-top" alt="Image for ` + vid_title + `">
        <div class="card-body">
          <h5 id="vid_title_` + vid_id + `" class="card-title">` + vid_title + `</h5>
          <p class="card-text">` + vid_description + `</p>
        </div>
        <div class="card-footer">
          <small class="text-muted">Publicado: ` + vid_publishedAt + `</small>
        </div>
      </div>`;
      // Force a wrap every X columns on different viewport width (breakpoints)
      num_vid++;
      if (num_vid%2 === 0) {
        content += `<div class="w-100 d-none d-sm-block d-md-none"><!-- wrap every 2 on sm--></div>`;
      }
      if (num_vid%3 === 0) {
        content += `<div class="w-100 d-none d-md-block d-lg-none"><!-- wrap every 3 on md--></div>`;
      }
      if (num_vid%4 === 0) {
        content += `<div class="w-100 d-none d-lg-block d-xl-none"><!-- wrap every 4 on lg--></div>`;
      }
      if (num_vid%5 === 0) {
        content += `<div class="w-100 d-none d-xl-block"><!-- wrap every 5 on xl--></div>`;
      }
      // Keep the video's info to handle the click events
      vid_array.push({vid_id:vid_id, vid_title:vid_title, vid_title_slug:vid_title_slug});
    }
  }
  // Populate the list of videos
  document.getElementById("list_videos").innerHTML = content;

  // Add an event handler on the entire card to play the video
  for (var i = 0; i < num_vid; i++) {
    let vid_id = vid_array[i]["vid_id"];
    let vid_title = vid_array[i]["vid_title"];
    let vid_title_slug  = vid_array[i]["vid_title_slug"];
    document.getElementById("vid_card_" + vid_id).addEventListener("click", function(){ navigate_to_video(vid_id, vid_title_slug, loc, vid_title); });
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

function navigate_to_video(id, title_slug, loc, title) {
  // Keep a reference to that video's location for history handling
  video_location = loc;
  update_history_for_video(id, title_slug, title);
  show_video_overlay(id, title_slug, title);
}

function update_history_for_video(id, title_slug, title) {
  // Update the URL for that video
  history.pushState({"type": "video", "id": id, "title_slug": title_slug, "title": title}, id, "#" + title_slug + "/" + id);
}

function show_video_overlay(id, title_slug, title) {
  // Update the video overlay with the url for this video
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = `<iframe id="video_overlay_iframe" src="https://www.youtube.com/embed/` + id + `?autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`
  // Show the overlay containing the YouTube Embed iframe
  overlay_show("video_overlay");
  // Hide the overlay containing the list of videos at that location
  overlay_hide("list_overlay");
  // Update page title
  document.title = title + " - El Vallenatero Francés";
}

function show_home_page() {
  // Hide both location and video overlays
  overlay_hide("list_overlay");
  overlay_hide("video_overlay");
  // Also remove the iframe (in case the YouTube video is playing)
  document.getElementById("video_overlay_iframe_placeholder").innerHTML = "";

  // Update page title
  document.title = "El Vallenatero Francés";
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
    // Update page title
    document.title = video_location + " - El Vallenatero Francés";
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
        show_video_overlay(history.state.id, history.state.title_slug, history.state.title);
      } else {
        // Fallback to the home page (should never happen)
        show_home_page();
      }
    } else {
      // Probably a hand-typed hash URL
      check_valid_slug();
    }
  }
};

document.onkeydown = key_down;
window.onhashchange = URL_changed;

main();
