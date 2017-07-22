
  // Define all variables
var currentVideo, player, playerConfig, videoJustChanged;
var totalDuration = 0;
var progressArray = [];

// Perform some initial setup/calculations
determineCurrentVideoParameter();
setUpVideoPlayer();
populateProgressArray();
window.onload = function(e){
  createUI();
}

// Detect Back or Forward button
window.onpopstate = function(e){
  // Get the p parameter directly from the URL
  determineCurrentVideoParameter();
  changeVideo(false);
};

// From https://stackoverflow.com/a/11582513/185053
function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

// From https://stackoverflow.com/a/1830844/185053
function isNumeric(n) {
  if (n) n = n.replace(/,/,".");
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function determineCurrentVideoParameter(){
  currentVideo = getURLParameter('p');
  if (!isNumeric(currentVideo)) window.location = "?p=1";
  currentVideo -= 1; //URL Parameter/visible ID is 1-based, while array is 0-based
  // currentVideo == -1 means playing the complete video
  if (currentVideo < -1) window.location = "?p=1";
  if (currentVideo > videos.length - 1) window.location = "?p=" + videos.length;
}

function setUpVideoPlayer(){
  // Based on https://webapps.stackexchange.com/a/103450/161341
  var startSeconds, endSeconds;
  var videoId = (currentVideo == -1) ? fullVersion : videos[currentVideo].id;
  if (currentVideo > -1) {
    startSeconds = videos[currentVideo].start;  // set your own video start time when loop play
    endSeconds = videos[currentVideo].end;   // set your own video end time when loop play
  }
  playerConfig = {
    height: '97%',
    width: '100%',
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
      autohide: 0,            // Hide video controls when playing
      //enablejsapi: 1,
      //origin: "https://vallenato.fr"
    },
    events: {
      'onStateChange': onStateChange
    }
  };
}

function onYouTubePlayerAPIReady() {
  // Play the first video in div
  player = new YT.Player('videoPlayer', playerConfig);
}

// Reload the video when onStateChange=YT.PlayerState.ENDED)
function onStateChange(state) {
  if (state.data === YT.PlayerState.ENDED && !videoJustChanged) {
    videoJustChanged = true;
    // Reset videoJustChanged after one second to prevent this block being called twice in succession
    // (messes with the logic to advance video if selected)
    setTimeout(function(){videoJustChanged = false;}, 1000);
    // Advance to next video if checkbox is not checked
    if (!document.getElementById("repeatVideo").checked){
      currentVideo = (currentVideo < videos.length - 1) ? currentVideo + 1 : 0;
      changeVideo(true);
    } else {
      // Replay the same video
      changeVideo(false);
    }
  }
}

function populateProgressArray(){
  // Construct the array used for the progress bar
  for (var i = 0; i < videos.length; i++) {
    var duration = videos[i].end - videos[i].start;
    progressArray.push(totalDuration);
    totalDuration += duration;
  }
}

function createUI() {
  var ul = document.getElementById("navigation");
  for (var i = 0; i < videos.length; i++) {
    var li = document.createElement("li");
    li.appendChild(document.createTextNode("Parte " + (i + 1)));
    li.addEventListener("click", changeVideoEvent, false);
    li.num = i;
    ul.appendChild(li);
  }

  document.getElementById("previousButton").addEventListener("click", previousVideo, false);
  document.getElementById("nextButton").addEventListener("click", nextVideo, false);
  document.getElementById("progress").addEventListener("click", progressbarClicked, false);
  document.getElementById("versionCompleta").addEventListener("click", versionCompletaClicked, false);
  updateUI(false);
}

function versionCompletaClicked(evt){
  currentVideo = -1;
  changeVideo(true);
}

function progressbarClicked(evt){
  desiredDuration = Math.floor(evt.offsetX * totalDuration / evt.target.offsetWidth);
  var i = 0;
  while (desiredDuration > progressArray[i]){
    if (i > videos.length) break; // Safety check
    i++;
  }
  currentVideo = i - 1; // The video that contains the timestamp clicked on
  changeVideo(true);
}

function changeVideoEvent(evt) {
  currentVideo = evt.target.num;
  changeVideo(true);
}

function changeVideo(updateURL) {
  updateUI(updateURL);

  if (currentVideo == -1) {
    player.loadVideoById({videoId: fullVersion});
  } else {
    player.loadVideoById({
      videoId: videos[currentVideo].id,
      startSeconds: videos[currentVideo].start,
      endSeconds: videos[currentVideo].end
    });
  }
}

function previousVideo(video) {
  currentVideo = (currentVideo > 0) ? currentVideo - 1 : 0;
  changeVideo(true);
}

function nextVideo(video) {
  currentVideo = (currentVideo < videos.length - 2) ? currentVideo + 1 : videos.length - 1;
  changeVideo(true);
}

function updateUI(updateURL) {
  if(updateURL){
    // Change the URL, so that if the user refreshes the page he gets back to this specific part
    window.history.pushState({}, document.title, "?p=" + (currentVideo + 1));
  }

  // Show the name of the current video
  var updatedTitle = videoTitle + ((currentVideo == -1) ? ", versión completa" : ", Parte " + (currentVideo + 1));
  document.title = updatedTitle;
  document.getElementById("nameCurrent").innerHTML = updatedTitle;

  // Set the current video as active in the navigation bar
  // First check that the element has child nodes
  var ul = document.getElementById("navigation");
  if (ul.hasChildNodes()) {
    var children = ul.childNodes;
    // First node is a text node, start with 1 and use i-1 to compare to currentVideo
    for (var i = 1; i < children.length; i++) {
      children[i].className = (i - 1 == currentVideo) ? "active" : "";
    }
  }

  // Show the appropriate buttons
  document.getElementById("previousButton").style.visibility = (currentVideo < 1) ? "hidden" : "visible";
  document.getElementById("nextButton").style.visibility = (currentVideo > videos.length - 2) ? "hidden" : "visible";
  document.getElementById("versionCompleta").style.display = (currentVideo == -1) ? "none" : "inline";

  // Update the progress bar
  var pBar = document.getElementById('progress');
  pBar.max = totalDuration;
  pBar.value = (currentVideo == -1) ? 0 : progressArray[currentVideo];
  pBar.getElementsByTagName('span')[0].innerHTML = (currentVideo == -1) ? 0 : Math.floor((100 / totalDuration) * progressArray[currentVideo]);
}
