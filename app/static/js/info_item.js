window.document.onkeydown = function(e) {
  if (!e) {
    e = event;
  }
  if (e.keyCode == 27) {
    lightbox_close();
  }
}

function lightbox_open() {
  var lightBoxVideo = document.getElementById("VisaChipCardVideo");
  lightBoxVideo.src = "https://www.w3schools.com/html/mov_bbb.mp4";
  // lightBoxVideo.src = "https://youtube.com/embed/1xeYl-Ak3qQ";
  window.scrollTo(100, 100);
  var light_div = document.getElementById('light');
  light_div.style.display = 'block';
  document.getElementById('fade').style.display = 'block';
  lightBoxVideo.play();
  var image_height = parseInt(getComputedStyle(light_div).height);
  var body_height = $(window).height();
  light_div.style.top = (body_height/2 - image_height/2).toString();
}

function lightbox_close() {
  var lightBoxVideo = document.getElementById("VisaChipCardVideo");
  document.getElementById('light').style.display = 'none';
  document.getElementById('fade').style.display = 'none';
  lightBoxVideo.pause();
}