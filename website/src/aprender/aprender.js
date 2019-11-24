// Define [global] variables
/*jslint browser: true, white, devel: true */
/*global window, tutoriales, YT */
var current_page_is_tutorial = false;
var localPlayer = false;
var editMode = false;
var currentVideo;
var player;
var playerConfig;
var YouTubeVideoPlayerInitialized = false;
var videoJustChanged;
var tutorial_slug;
var videos;
var videosFullTutorial;
var fullVersion;
var tutorialTitle;
var tutorialAuthor;
var tutorialFullTitle;

function main(){
  // Populate the list of tutorials
  populateTutorials();

  // Set up click handler for all the links on the page
  $("a").click(function(e) {
    // All links, except home and the YouTube channel links
    if(-1 === ["home-brand-link", "home-link", "yt-channel-link"].indexOf(this.id)) {
      e.preventDefault();
      history.pushState(null, null, this.href);
      check_valid_slug();
    }
  });

  if (null !== getURLParameter("local")) {
    // Update tutorials links to use local video files instead of the YouTube-hosted videos
    $("#tutoriales > div > div > a").each(function (link, i) {
      $(this)[0].href += "?local=1";
    });
  }

  // Check if we started with another page than the root
  if("/aprender/" !== window.location.pathname){
    check_valid_slug();
  }
}

function populateTutorials() {
  tutoriales.forEach(function (tuto, i) {
    var tuto_duration = getDuration(tuto.videos, false);
    var tuto_string = `<!-- Tutorial ` + (i+1) + ` -->
      <div class="card mb-3" style="max-width: 17rem;">
        <div class="card-body">
          <h5 class="card-title">` + tuto["title"] + (tuto["author"] ? ` - ` + tuto["author"] : "") + `</h5>
          <a href="` + tuto["slug"] + `" class="stretched-link text-hide">Ver el tutorial</a>
        </div>
        <div class="card-footer"><small class="text-muted">` + tuto_duration + `</small></div>
      </div>\n`;
    if (0 === (i+1)%2) {
      tuto_string += `<div class="w-100 d-none d-sm-block d-md-none"><!-- wrap every 2 on sm--></div>`;
    }
    if (0 === (i+1)%3) {
      tuto_string += `<div class="w-100 d-none d-md-block d-lg-none"><!-- wrap every 3 on md--></div>`;
    }
    if (0 === (i+1)%4) {
      tuto_string += `<div class="w-100 d-none d-lg-block d-xl-none"><!-- wrap every 4 on lg--></div>`;
    }
    if (0 === (i+1)%5) {
      tuto_string += `<div class="w-100 d-none d-xl-block"><!-- wrap every 5 on xl--></div>`;
    }
    $("#tutoriales").append(tuto_string);
  });
}

// Inspired from https://stackoverflow.com/a/11582513/185053 , modified for JSLint
function getURLParameter(name) {
  "use strict";
  // This function will return null if this specific parameter is not found
  var parameterValue = null;
  // Perform a regex match to find the value of the parameter from the query string
  var parameterRegex = new RegExp("[?|&]" + name + "=" + "([^&;]+?)(&|#|;|$)").exec(location.search);
  if (parameterRegex) {
    // If the regex found a match, replace any occurrence of + by %20
    parameterValue = parameterRegex[1].replace(/\+/g, "%20");
    // and perform proper decoding of the URI
    parameterValue = decodeURIComponent(parameterValue);
  }
  // Returns either null or the value of that parameter
  return parameterValue;
}

// From https://stackoverflow.com/a/1830844/185053
function isNumeric(n) {
  "use strict";
  if (n) {
    n = n.replace(/,/, ".");
  }
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function determineCurrentVideoParameter() {
  "use strict";
  currentVideo = getURLParameter("p");
  if (!isNumeric(currentVideo)) {
    // Assume we want the first video of that tutorial
    currentVideo = 1;
  }
  currentVideo = parseInt(currentVideo);
  currentVideo -= 1; //URL Parameter/visible ID is 1-based, while array is 0-based
  // currentVideo == -1 means playing the complete video
  if (currentVideo < -1) {
    window.location = "?p=1" + (localPlayer ? "&local=1" : "") + (editMode ? "&editar=1" : "");
  }
  if (currentVideo > videos.length - 1) {
    // If this video has no full tutorial videos, go back to the latest regular part
    if (typeof videosFullTutorial == 'undefined' || (videosFullTutorial && currentVideo > videos.length + videosFullTutorial.length - 1)) {
      window.location = "?p=1" + (localPlayer ? "&local=1" : "") + (editMode ? "&editar=1" : "");
    }
  }
}

function updateUI(updateURL) {
  "use strict";
  if (updateURL) {
    // Change the URL, so that if the user refreshes the page he gets back to this specific part
    var newURL = "?p=" + (currentVideo + 1) + (localPlayer ? "&local=1" : "") + (editMode ? "&editar=1" : "");
    window.history.pushState({}, document.title, newURL);
  }

  // Set the current video as active in the partsList bar
  $("#partsList").children().each(function (i) {
    if (i === currentVideo) {
      $(this).addClass("active");
    } else {
      $(this).removeClass("active");
    }
  });
  // Version completa
  if (currentVideo === -1) {
    $("#versionCompleta").addClass("active");
  } else {
    $("#versionCompleta").removeClass("active");
  }

  // Show the appropriate buttons
  document.getElementById("previousButton").style.visibility = (currentVideo < 1) ? "hidden" : "visible";
  document.getElementById("nextButton").style.visibility = (currentVideo > videos.length - 2) ? "hidden" : "visible";
}

function getVideoValues() {
  "use strict";
  var startSeconds;
  var endSeconds;
  var localVideoURL;
  var videoId;
  if (currentVideo === -1) {
    videoId = fullVersion;
  } else if (currentVideo < videos.length) {
    videoId = videos[currentVideo].id;
  } else {
    videoId = videosFullTutorial[currentVideo - videos.length].id;
  }
  if (currentVideo > -1 && currentVideo < videos.length) {
    startSeconds = videos[currentVideo].start;
    endSeconds = videos[currentVideo].end;
  } else if (currentVideo > videos.length - 1) {
    startSeconds = videosFullTutorial[currentVideo - videos.length].start;
    endSeconds = videosFullTutorial[currentVideo - videos.length].end;
  }

  if (localPlayer) {
    // The local videos are available at:
    // videos/<tutorial slug>/<YouTube ID>.mp4
    localVideoURL = "videos/" + tutorial_slug + "/" + videoId + ".mp4";
  }

  return{"videoId": videoId, "localVideoURL": localVideoURL, "startSeconds": startSeconds, "endSeconds": endSeconds};
}

function isSameLocalVideo(currentVideo, newVideo) {
  "use strict";
  var shortURL = currentVideo.substring(currentVideo.length - newVideo.length, currentVideo.length);
  return (shortURL === newVideo);
}

function changeVideo(updateURL) {
  "use strict";
  updateUI(updateURL);

  var vidValues = getVideoValues();
  if (currentVideo === -1) {
    if (!localPlayer) {
      player.loadVideoById({videoId: fullVersion});
    } else {
      if (!isSameLocalVideo(player.src, vidValues.localVideoURL)) {
        player.src = vidValues.localVideoURL;
      }
      player.startSeconds = null;
      player.endSeconds = null;
    }
  } else {
    if (!localPlayer) {
      player.loadVideoById({
        videoId: vidValues.videoId,
        startSeconds: vidValues.startSeconds,
        endSeconds: vidValues.endSeconds
      });
    } else {
      if (!isSameLocalVideo(player.src, vidValues.localVideoURL)) {
        player.src = vidValues.localVideoURL;
      }
      // Set the player at the timestamp we want to start on
      player.currentTime = vidValues.startSeconds;
      // Keep the start and end timestamps on the video object to check from the timeupdate event
      player.startSeconds = vidValues.startSeconds;
      player.endSeconds = vidValues.endSeconds;
    }
  }
  updatePlaybackSpeed();
  if (localPlayer && player.paused) {
    // The local player needs a little push when the full version played to the end and stopped.
    player.play();
  }
}

function changeVideoEvent(evt) {
  "use strict";
  if ("INPUT" === evt.target.nodeName) {
    // When in Edit Mode, and clicking inside a timestamp input element
    // Don't restart this part if we were already playing it
    if (parseInt(evt.target.parentNode.parentNode.id.substring(4)) === currentVideo) {
      return;
    }
    currentVideo = evt.target.parentNode.parentNode.id.substring(4);
  } else if ("SPAN" === evt.target.nodeName) {
    currentVideo = evt.target.parentNode.id.substring(4);
  } else if ("BUTTON" === evt.target.nodeName) {
    currentVideo = evt.target.id.substring(4);
  }

  if(currentVideo.startsWith("Full")) {
    // This is part of Full videos, update currentVideo accordingly
    currentVideo = parseInt(currentVideo.substring(4)) + videos.length;
  } else {
    // Make sure it's numeric, since it comes from the id that's a string
    currentVideo = parseInt(currentVideo);
  }

  changeVideo(true);
}

function playFollowing() {
  "use strict";
  // Replays the same video or advances to the next, depending on the checkbox
  if (!document.getElementById("repeatVideo").checked) {
    if (videos.length - 1 === currentVideo) {
      // If we're at the last of the regular tutorial parts, start again at the first regular tutorial part
      currentVideo = 0;
    } else if (videos.length + videosFullTutorial.length - 1 === currentVideo) {
      // If we're at the last of the full tutorial parts, start again at the first full tutorial part
      currentVideo = videos.length;
    } else if (currentVideo > videos.length + videosFullTutorial.length - 1) {
      // If we're at an invalid part ID, start again at the first regular tutorial part
      currentVideo = 0;
    } else {
      // Otherwise just continue with the next video
      currentVideo = currentVideo + 1;
    }
    // Go to the next video
    changeVideo(true);
  } else {
    changeVideo(false);
  }
}

// Reload the video when onStateChange=YT.PlayerState.ENDED)
function onStateChange(state) {
  "use strict";
  var doSomething = false;
  if (!localPlayer) {
    if (state.data === YT.PlayerState.ENDED && !videoJustChanged) {
      videoJustChanged = true;
      doSomething = true;
      // Reset videoJustChanged after one second to prevent this block being called twice in succession (messes with the logic to advance video if selected)
      setTimeout(function () {
        videoJustChanged = false;
      }, 1000);
    }
  } else {
    if (player.endSeconds && (player.currentTime > player.endSeconds)) {
      doSomething = true;
    }
  }

  if (doSomething) {
    playFollowing();
  }
}

function playPauseLocalVideo() {
  "use strict";
  if (!player.paused) {
    player.pause();
  } else {
    player.play();
  }
}

function setUpLocalVideoPlayer() {
  "use strict";
  // Playing the videos via local HTML5 video
  var vidValues = getVideoValues();
  player = document.createElement("video");
  player.setAttribute("id", "localVideoPlayer");
  player.setAttribute("height", "95%");
  player.setAttribute("width", "98%");
  player.controls = "controls";
  player.autoplay = "autoplay";
  player.src = vidValues.localVideoURL;
  if (vidValues.startSeconds) {
    // Set the player at the timestamp we want to start on
    player.currentTime = vidValues.startSeconds;
    // Keep that start timestamp on the video object to check from the timeupdate event
    player.startSeconds = vidValues.startSeconds;
  }
  if (vidValues.endSeconds) {
    // Keep that end timestamp on the video object to check from the timeupdate event
    player.endSeconds = vidValues.endSeconds;
  }
  document.getElementById("videoPlayer").appendChild(player);

  // Use the timeupdate event to determine when playing this part is over
  player.addEventListener("timeupdate", onStateChange, false);
  // Listen to ended to identify when playing the full version is done
  player.addEventListener("ended", playFollowing, false);
  // Clicking on the video will pause or play it
  player.addEventListener("click", playPauseLocalVideo, false);
  // Take into account the playback speed checkbox (in case a refresh keeps it checked)
  updatePlaybackSpeed();
}

function setUpYouTubeVideoPlayer() {
  "use strict";

  var vidValues = getVideoValues();
  // Based on https://webapps.stackexchange.com/a/103450/161341
  playerConfig = {
    height: "96%",
    width: "99%",
    videoId: vidValues.videoId,
    playerVars: {
      // https://developers.google.com/youtube/player_parameters
      autoplay: 1,            // Auto-play the video on load
      controls: 1,            // Show pause/play buttons in player
      showinfo: 0,            // Hide the video title
      rel: 0,                 // Hide related videos when pausing video
      //modestbranding: 1,      // Hide the Youtube Logo
      fs: 1,                  // Show the full screen button
      cc_load_policy: 0,      // Hide closed captions
      iv_load_policy: 3,      // Hide the Video Annotations
      start: vidValues.startSeconds,
      end: vidValues.endSeconds,
      autohide: 0            // Hide video controls when playing
      //enablejsapi: 1,
      //origin: "https://vallenato.fr"
    },
    events: {
      "onStateChange": onStateChange
    }
  };

  if (!YouTubeVideoPlayerInitialized) {
    // Load the YouTube JavaScript, per https://stackoverflow.com/a/3973468/185053
    var script = document.createElement("script");
    script.async = "async";
    script.type = "text/javascript";
    script.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(script);
    YouTubeVideoPlayerInitialized = true;
  } else {
    // The YT player script was already loaded when playing another tutorial
    // Just re-trigger the creation of the YT player object
    onYouTubeIframeAPIReady();
  }
}

function determineTutorial(tutorial) {
  "use strict";
  tutorial_slug = tutorial;
  // TODO: handle invalid tutorial slug
  tutoriales.forEach(function (tuto, i) {
    if (tuto["slug"] === tutorial_slug) {
      videos = tuto["videos"];
      videosFullTutorial = tuto["videos_full_tutorial"];
      fullVersion = tuto["full_version"];
      tutorialTitle = tuto["title"]
      tutorialAuthor = tuto["author"];
      tutorialFullTitle = tuto["title"];
      if (tuto["author"]) {
        tutorialFullTitle += " - " + tuto["author"];
      }
    }
  });
}

function determineLocalOrYouTubePlayer() {
  "use strict";
  localPlayer = (null !== getURLParameter("local"));
}

function determineEditMode() {
  "use strict";
  editMode = (null !== getURLParameter("editar"));
}

function onYouTubeIframeAPIReady() {
  "use strict";
  if (!localPlayer) {
    // Play the first video in div
    player = new YT.Player("videoPlayer", playerConfig);
    // Take into account the playback speed checkbox (in case a refresh keeps it checked)
    // (wait 2 seconds, since the player might take some time to load - there's probably a cleaner way to do this)
    setTimeout(updatePlaybackSpeed, 2000);
  }
}

// From https://stackoverflow.com/a/3733257/185053
function str_pad_left(string,pad,length) {
  "use strict";
  return (new Array(length+1).join(pad)+string).slice(-length);
}

function previousVideo() {
  "use strict";
  // The button can't go lower than 0 (by design), but with the "p" shortcut we want to be able to go to the Full Version
  currentVideo = (currentVideo > -1) ? currentVideo - 1 : -1;
  changeVideo(true);
}

function nextVideo() {
  "use strict";
  currentVideo = (currentVideo < videos.length - 2) ? currentVideo + 1 : videos.length - 1;
  changeVideo(true);
}

function fullscreenVideo() {
  "use strict";
  var vidply = $('#videoPlayer').get(0);
  var requestFullScreen = vidply.requestFullScreen || vidply.mozRequestFullScreen || vidply.webkitRequestFullScreen;
  if (requestFullScreen) {
    requestFullScreen.bind(vidply)();
  }
}

function versionCompletaClicked() {
  "use strict";
  currentVideo = -1;
  changeVideo(true);
}

function updatePlaybackSpeed() {
  "use strict";
  var playbackSpeed = (document.getElementById("slowPlayback").checked ? 0.70 : 1);
  if (!localPlayer) {
    player.setPlaybackRate(playbackSpeed);
  } else {
    player.playbackRate = (playbackSpeed);
  }
}

function keyPressed(evt) {
  "use strict";
  var code;
  //Find which key is pressed
  if (evt.keyCode) {
    code = evt.keyCode;
  } else if (evt.which) {
    code = evt.which;
  }
  var character = String.fromCharCode(code).toLowerCase();

  // Previous video: "p"
  if ("p" === character) {
    previousVideo();
  }

  // Next video: "n" or "s" (siguiente)
  if ("n" === character || "s" === character) {
    nextVideo();
  }

  // Restart this fragment: <home> (code 36)
  if (36 === code) {
    changeVideo(false); // No need to change the URL
  }

  // Toggle Lento: "v" (velocidad)
  if ("v" === character) {
    var slowPlayback = document.getElementById("slowPlayback");
    slowPlayback.checked = !slowPlayback.checked;
    updatePlaybackSpeed();
  }

  // Toggle Repeat: "r"
  if ("r" === character) {
    var repeatVideo = document.getElementById("repeatVideo");
    repeatVideo.checked = !repeatVideo.checked;
  }

  // Support some default Youtube embed player shortcuts that are made available if the focus in not in the player
  // Pause/Play: <space> (code 32)
  if (32 === code) {
    if (!localPlayer) {
      if (player.getPlayerState() === YT.PlayerState.PLAYING) {
        player.pauseVideo();
      } else {
        player.playVideo();
      }
    } else {
      playPauseLocalVideo();
    }
    //Stop the event
    // If there are too many parts, pressing <Space> would also perform a Page Down
    // IE
    evt.cancelBubble = true;
    evt.returnValue = false;
    if (evt.stopPropagation) {
      evt.stopPropagation();
      evt.preventDefault();
    }
  }

  // These shortcuts need enablejsapi and origin, disabled for now as it makes local testing more complex
  /*
  // Mute: "m"
  if ("m" === character) {
  console.log("Mute");
  if (player.isMuted()) {
  console.log("unmute");
  player.unMute();
} else {
console.log("mute");
player.unMute();
}
}
*/
}

function newPart() {
  "use strict";
  var i = videos.length;
  // The start time of this new part is the end time of the previous part
  if (isNumeric(document.getElementById("endVal" + (i - 1)).value)) {
    var startTime = parseInt(document.getElementById("endVal" + (i - 1)).value);
  } else {
    var startTime = videos[videos.length - 1].end;
  }
  // The end time is the end of the video
  var endTime = parseInt(player.duration + 1);
  // Add new UI elements
  partsList.insertAdjacentHTML('beforeend', newPartMarkup(i, false, startTime, endTime));
  // Add stub for this new part in the videos array
  videos.push({"id": videos[videos.length - 1].id, "start": startTime, "end": endTime});
  // Start playing this new part
  currentVideo = videos.length - 1;
  changeVideo(true);
}

function getPartsTimestamps(vids) {
  "use strict";
  var outputJSPart = "";
  vids.forEach(function (vid, i) {
    var startTime = vids[i].start;
    var endTime = vids[i].end;
    if (vids === videos) {
      if (isNumeric(document.getElementById("startVal" + i).value)) {
        startTime = parseInt(document.getElementById("startVal" + i).value);
      }
      if (isNumeric(document.getElementById("endVal" + i).value)) {
        endTime = parseInt(document.getElementById("endVal" + i).value);
      }
      vids[i].start = startTime;
      vids[i].end = endTime;
      // To handle the cases where the input was empty, repopulate with same value or default start/end times
      document.getElementById("startVal" + i).value = startTime;
      document.getElementById("endVal" + i).value = endTime;
    }
    outputJSPart += '      {"id": "' + vids[i].id + '", "start": ' + startTime + ', "end": ' + endTime + '}' + (i < vids.length - 1 ? ",": "") + '\n';
  });
  return outputJSPart;
}

function saveTimestamps() {
  "use strict";
  var outputJS = `,
  {
    "slug": "` + tutorial_slug + `",
    "author": "` + tutorialAuthor + `",
    "title": "` + tutorialTitle + `",
    "videos": [\n` + getPartsTimestamps(videos) + `    ],
    "videos_full_tutorial": [\n` + getPartsTimestamps(videosFullTutorial) + `    ],
    "full_version": "` + fullVersion + `"
  }`;
  document.getElementById("outputJS").value = outputJS;
  // Temporarily change the color of the element containing the output JS
  document.getElementById("outputJS").style.color = "red";
  setTimeout(function () {
    document.getElementById("outputJS").style.color = "black";
  }, 1500);
  // Update the duration information and print that out to the console
  var totDur = getDuration(videos, true);
  console.log(totDur);
  // Restart playing the current part, to give sensory feedback to the user that something happened
  changeVideo(false);
}

function getDuration(vids, fullInfo) {
  var totalDuration = 0;
  vids.forEach(function (video) {
    totalDuration += video.end - video.start;
  });
  var totDur = (fullInfo ? "totalDuration: " + totalDuration + "s - " : "") + str_pad_left(Math.floor(totalDuration / 60),"0",2) + "m" + str_pad_left(totalDuration % 60,"0",2) + "s en " +  vids.length + " partes";
  return totDur;
}

function startButton() {
  "use strict";
  document.getElementById("startVal" + currentVideo).value = parseInt(player.currentTime);
}

function endButton() {
  "use strict";
  document.getElementById("endVal" + currentVideo).value = parseInt(player.currentTime);
}

function newPartMarkup(i, full, startTime, endTime) {
  "use strict";
  var newPartContent = `<button id="part` + (full ? "Full" : "") + i + `" class="list-group-item list-group-item-action" onclick="changeVideoEvent(event);">` + (full ? "Full " : "Parte ") + (i + 1);
  if (!full && editMode) {
    // Input for new timeslots only supported for regular parts, not Full parts
    newPartContent += "<span class='d-inline-block ml-1'><input class='editInput' type='text' id='startVal" + i + "' onkeydown='(function (e) { if (e.keyCode === 13) { saveTimestamps(); } })(event);' value='" + startTime + "'>-<input class='editInput' type='text' id='endVal" + i + "' onkeydown='(function (e) { if (e.keyCode === 13) { saveTimestamps(); } })(event);' value='" + endTime + "'></span>";
  }
  newPartContent += `</button>`;
  return newPartContent;
}

function createUI() {
  "use strict";
  // Update page title
  $("title").html(tutorialFullTitle);
  $("#tutorialFullTitle").html(tutorialFullTitle);
  if (editMode) {
    // Adapt UI for Edit Mode
    $("#editBox").removeClass("d-none");
    // Button click events
    document.getElementById("newPart").addEventListener("click", newPart, false);
    document.getElementById("saveTimestamps").addEventListener("click", saveTimestamps, false);
    document.getElementById("startButton").addEventListener("click", startButton, false);
    document.getElementById("endButton").addEventListener("click", endButton, false);
  }
  var partsList = document.getElementById("partsList");
  var partsListContent = "";
  videos.forEach(function (vid, i) {
    partsListContent += newPartMarkup(i, false, vid.start, vid.end);
  });
  partsList.innerHTML = partsListContent;
  if (typeof videosFullTutorial !== 'undefined') {
    var partsListFullContent = "";
    videosFullTutorial.forEach(function (vid, i) {
      partsListFullContent += newPartMarkup(i, true, null, null);
    });
    document.getElementById("partsListFull").innerHTML = partsListFullContent;
  }

  if (localPlayer) {
    // Link to use local video files instead of the YouTube-hosted videos
    document.getElementById("aprender-link").href = "/aprender/?local=1";
  }

  document.getElementById("previousButton").addEventListener("click", previousVideo, false);
  document.getElementById("nextButton").addEventListener("click", nextVideo, false);
  document.getElementById("fullscreenButton").addEventListener("click", fullscreenVideo, false);
  document.getElementById("versionCompleta").addEventListener("click", versionCompletaClicked, false);
  document.getElementById("slowPlayback").addEventListener("CheckboxStateChange", updatePlaybackSpeed, false);
  document.addEventListener("keydown", keyPressed, false); // Keyboard shortcuts

  // Hide the aprender page
  $("#aprender_page").addClass("d-none");
  // Show the tutorial page
  $("#tutorial_page").removeClass("d-none");

  updateUI(false);
}

function check_valid_slug() {
  // Collapse the navbar, if it was expanded on small devices
  $("#navbarCollapse").collapse('hide');

  // Identify which page to display
  if("/aprender/" === window.location.pathname) {
    // Go to the /aprender/ page
    current_page_is_tutorial = false;
    show_aprender_page();
    return;
  }

  tutoriales.some(function (tuto) {
    if("/aprender/" + tuto["slug"] === window.location.pathname) {
      if (current_page_is_tutorial) {
        // Just changing parts within the same tutorial (probably Back or Forward button)
        determineCurrentVideoParameter();
        changeVideo(false);
      } else {
        // Go to that tutorial's page
        current_page_is_tutorial = true;
        show_tutorial_page(window.location.pathname.substring(10));
      }
      return true;
    }
  });
}

function show_tutorial_page(tutorial) {
  // Perform some initial setup/calculations
  determineTutorial(tutorial);
  determineLocalOrYouTubePlayer();
  determineEditMode();
  determineCurrentVideoParameter();
  createUI();
  if (!localPlayer) {
    setUpYouTubeVideoPlayer();
  } else {
    setUpLocalVideoPlayer();
  }
}

function show_aprender_page() {
  // Hide the tutorial page
  $("#tutorial_page").addClass("d-none");
  // Show the aprender page
  $("#aprender_page").removeClass("d-none");
  // Remove any tutorial player
  $("#player").html(`<div id="videoPlayer"></div>`);
  // Update page title
  document.title = "Aprender a tocar el Acordeón Vallenato - El Vallenatero Francés";
}

// Detect Back or Forward buttons
window.onpopstate = check_valid_slug;

main();
