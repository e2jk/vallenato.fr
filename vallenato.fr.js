// Define [global] variables
/*jslint browser: true, white, devel: true */
/*global window, videos, fullVersion, YT */
var localPlayer = false;
var currentVideo;
var videoTitle;
var player;
var playerConfig;
var videoJustChanged;
var totalDuration = 0;
var progressArray = [];

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
    window.location = "?p=1" + (localPlayer ? "&local=1" : "");
  }
  currentVideo -= 1; //URL Parameter/visible ID is 1-based, while array is 0-based
  // currentVideo == -1 means playing the complete video
  if (currentVideo < -1) {
    window.location = "?p=1" + (localPlayer ? "&local=1" : "");
  }
  if (currentVideo > videos.length - 1) {
    window.location = "?p=" + videos.length + (localPlayer ? "&local=1" : "");
  }
}

function updateUI(updateURL) {
  "use strict";
  if (updateURL) {
    // Change the URL, so that if the user refreshes the page he gets back to this specific part
    var newURL = "?p=" + (currentVideo + 1) + (localPlayer ? "&local=1" : "");
    window.history.pushState({}, document.title, newURL);
  }

  // Show the name of the current video
  var updatedTitle = videoTitle + ((currentVideo === -1) ? ", versión completa" : ", Parte " + (currentVideo + 1));
  document.title = updatedTitle;
  document.getElementById("nameCurrent").innerHTML = updatedTitle;

  // Set the current video as active in the navigation bar
  // First check that the element has child nodes
  var ul = document.getElementById("navigation");
  if (ul.hasChildNodes()) {
    // First node is a text node, start with 1 and use i-1 to compare to currentVideo
    ul.childNodes.forEach(function (child, i) {
      child.className = (i - 1 === currentVideo) ? "active" : "";
    });
  }

  // Show the appropriate buttons
  document.getElementById("previousButton").style.visibility = (currentVideo < 1) ? "hidden" : "visible";
  document.getElementById("nextButton").style.visibility = (currentVideo > videos.length - 2) ? "hidden" : "visible";
  document.getElementById("versionCompleta").style.display = (currentVideo === -1) ? "none" : "inline";

  // Update the progress bar
  var pBar = document.getElementById("progress");
  pBar.max = totalDuration;
  pBar.value = (currentVideo === -1) ? 0 : progressArray[currentVideo];
  pBar.getElementsByTagName("span")[0].innerHTML = (currentVideo === -1) ? 0 : Math.floor((100 / totalDuration) * progressArray[currentVideo]);
}

function getVideoValues() {
  "use strict";
  var startSeconds;
  var endSeconds;
  var localVideoURL;
  var videoId = (currentVideo === -1) ? fullVersion : videos[currentVideo].id;
  if (currentVideo > -1) {
    startSeconds = videos[currentVideo].start;
    endSeconds = videos[currentVideo].end;
  }

  if (localPlayer) {
    // The local videos are available at:
    // videos/<folder with the same name as current file>/<YouTube ID>.mp4
    // Get the name of the current file, i.e. after last / and before .html
    var localVideoFolderName = window.location.href.split("/").slice(-1)[0].split(".")[0];
    localVideoURL = "videos/" + localVideoFolderName + "/" + videoId + ".mp4";
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
  if (localPlayer && player.paused) {
    // The local player needs a little push when the full version played to the end and stopped.
    player.play();
  }
}

function changeVideoEvent(evt) {
  "use strict";
  currentVideo = evt.target.num;
  changeVideo(true);
}

function playFollowing() {
  "use strict";
  // Replays the same video or advances to the next, depending on the checkbox
  if (!document.getElementById("repeatVideo").checked) {
    currentVideo = (currentVideo < videos.length - 1) ? currentVideo + 1 : 0;
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
  player.setAttribute("height", "96%");
  player.setAttribute("width", "99%");
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
}

function setUpYouTubeVideoPlayer() {
  "use strict";
  // Load the YouTube JavaScript, per https://stackoverflow.com/a/3973468/185053
  var script = document.createElement("script");
  script.async = "async";
  script.type = "text/javascript";
  script.src = "https://www.youtube.com/iframe_api";
  document.body.appendChild(script);

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
}

function determineLocalOrYouTubePlayer() {
  "use strict";
  localPlayer = (null !== getURLParameter("local"));
}

function onYouTubePlayerAPIReady() {
  "use strict";
  if (!localPlayer) {
    // Play the first video in div
    player = new YT.Player("videoPlayer", playerConfig);
  }
}

// From https://stackoverflow.com/a/3733257/185053
function str_pad_left(string,pad,length) {
  "use strict";
  return (new Array(length+1).join(pad)+string).slice(-length);
}

function populateProgressArray() {
  "use strict";
  // Construct the array used for the progress bar
  videos.forEach(function (video) {
    var duration = video.end - video.start;
    progressArray.push(totalDuration);
    totalDuration += duration;
  });

  // Use the following to output the total duration and number of parts, used to update the index.html when adding a new song.
  if (false) {
    var totDur = "totalDuration: " + totalDuration + "s - " + str_pad_left(Math.floor(totalDuration / 60),"0",2) + "m" + str_pad_left(totalDuration % 60,"0",2) + "s en " +  videos.length + " partes";
    console.log(totDur);
    alert(totDur);
  }
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

function progressbarClicked(evt) {
  "use strict";
  var desiredDuration = Math.floor(evt.offsetX * totalDuration / evt.target.offsetWidth);
  var i = 0;
  while (desiredDuration > progressArray[i]) {
    if (i > videos.length) {
      break;
    } // Safety check
    i += 1;
  }
  currentVideo = i - 1; // The video that contains the timestamp clicked on
  changeVideo(true);
}

function versionCompletaClicked() {
  "use strict";
  currentVideo = -1;
  changeVideo(true);
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

function createUI() {
  "use strict";
  var ul = document.getElementById("navigation");
  videos.forEach(function (ignore, i) {
    var li = document.createElement("li");
    li.appendChild(document.createTextNode("Parte " + (i + 1)));
    li.addEventListener("click", changeVideoEvent, false);
    li.num = i;
    ul.appendChild(li);
  });

  // Save the initial Title, as it contains the name of the current song
  videoTitle = document.title;

  if (localPlayer) {
    // Link to local index page instead of online version on vallenato.fr
    document.getElementById("linkAndName").childNodes[1].href = "index.html?local=1";
  }

  document.getElementById("previousButton").addEventListener("click", previousVideo, false);
  document.getElementById("nextButton").addEventListener("click", nextVideo, false);
  document.getElementById("progress").addEventListener("click", progressbarClicked, false);
  document.getElementById("versionCompleta").addEventListener("click", versionCompletaClicked, false);
  document.addEventListener("keydown", keyPressed, false); // Keyboard shortcuts
  updateUI(false);
}

// Perform some initial setup/calculations
determineLocalOrYouTubePlayer();
determineCurrentVideoParameter();
populateProgressArray();
window.onload = function () {
  "use strict";
  createUI();
  if (!localPlayer) {
    setUpYouTubeVideoPlayer();
  } else {
    setUpLocalVideoPlayer();
  }
};

// Detect Back or Forward button
window.onpopstate = function () {
  "use strict";
  // Get the p parameter directly from the URL
  determineCurrentVideoParameter();
  changeVideo(false);
};
