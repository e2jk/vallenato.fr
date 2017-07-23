// Define [global] variables
/*jslint browser: true, white */
/*global window, videoTitle, videos, fullVersion, YT */
var currentVideo;
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
    window.location = "?p=1";
  }
  currentVideo -= 1; //URL Parameter/visible ID is 1-based, while array is 0-based
  // currentVideo == -1 means playing the complete video
  if (currentVideo < -1) {
    window.location = "?p=1";
  }
  if (currentVideo > videos.length - 1) {
    window.location = "?p=" + videos.length;
  }
}

function updateUI(updateURL) {
  "use strict";
  if (updateURL) {
    // Change the URL, so that if the user refreshes the page he gets back to this specific part
    window.history.pushState({}, document.title, "?p=" + (currentVideo + 1));
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

function changeVideo(updateURL) {
  "use strict";
  updateUI(updateURL);

  if (currentVideo === -1) {
    player.loadVideoById({videoId: fullVersion});
  } else {
    player.loadVideoById({
      videoId: videos[currentVideo].id,
      startSeconds: videos[currentVideo].start,
      endSeconds: videos[currentVideo].end
    });
  }
}

function changeVideoEvent(evt) {
  "use strict";
  currentVideo = evt.target.num;
  changeVideo(true);
}

// Reload the video when onStateChange=YT.PlayerState.ENDED)
function onStateChange(state) {
  "use strict";
  if (state.data === YT.PlayerState.ENDED && !videoJustChanged) {
    videoJustChanged = true;
    // Reset videoJustChanged after one second to prevent this block being called twice in succession
    // (messes with the logic to advance video if selected)
    setTimeout(function () {
      videoJustChanged = false;
    }, 1000);
    // Advance to next video if checkbox is not checked
    if (!document.getElementById("repeatVideo").checked) {
      currentVideo = (currentVideo < videos.length - 1) ? currentVideo + 1 : 0;
      changeVideo(true);
    } else {
      // Replay the same video
      changeVideo(false);
    }
  }
}

function setUpVideoPlayer() {
  "use strict";
  // Based on https://webapps.stackexchange.com/a/103450/161341
  var startSeconds;
  var endSeconds;
  var videoId = (currentVideo === -1) ? fullVersion : videos[currentVideo].id;
  if (currentVideo > -1) {
    startSeconds = videos[currentVideo].start;  // set your own video start time when loop play
    endSeconds = videos[currentVideo].end;   // set your own video end time when loop play
  }
  playerConfig = {
    height: "97%",
    width: "100%",
    videoId: videoId,
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
      start: startSeconds,
      end: endSeconds,
      autohide: 0            // Hide video controls when playing
      //enablejsapi: 1,
      //origin: "https://vallenato.fr"
    },
    events: {
      "onStateChange": onStateChange
    }
  };
}

function onYouTubePlayerAPIReady() {
  "use strict";
  // Play the first video in div
  player = new YT.Player("videoPlayer", playerConfig);
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
  //console.log("totalDuration: " + totalDuration + "s - " + str_pad_left(Math.floor(totalDuration / 60),'0',2) + 'm' + str_pad_left(totalDuration % 60,'0',2) + "s en " +  videos.length + " partes");
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

  // Toggle Repeat: "r"
  if ("r" === character) {
    var repeatVideo = document.getElementById("repeatVideo");
    repeatVideo.checked = !repeatVideo.checked;
  }

  // Support some default Youtube embed player shortcuts that are made available if the focus in not in the player
  // Pause/Play: <space> (code 32)
  if (32 === code) {
    if (player.getPlayerState() === YT.PlayerState.PLAYING) {
      player.pauseVideo();
    } else {
      player.playVideo();
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
  videos.forEach(function (video, i) {
    var li = document.createElement("li");
    li.appendChild(document.createTextNode("Parte " + (i + 1)));
    li.addEventListener("click", changeVideoEvent, false);
    li.num = i;
    ul.appendChild(li);
  });

  document.getElementById("previousButton").addEventListener("click", previousVideo, false);
  document.getElementById("nextButton").addEventListener("click", nextVideo, false);
  document.getElementById("progress").addEventListener("click", progressbarClicked, false);
  document.getElementById("versionCompleta").addEventListener("click", versionCompletaClicked, false);
  document.addEventListener("keydown", keyPressed, false); // Keyboard shortcuts
  updateUI(false);
}

// Perform some initial setup/calculations
determineCurrentVideoParameter();
setUpVideoPlayer();
populateProgressArray();
window.onload = function () {
  "use strict";
  createUI();
};

// Detect Back or Forward button
window.onpopstate = function () {
  "use strict";
  // Get the p parameter directly from the URL
  determineCurrentVideoParameter();
  changeVideo(false);
};
