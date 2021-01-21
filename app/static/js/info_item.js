var items_cache = {}
$(document).ready(function () {
    var $videoSrc;
    $('.video-btn').click(function () {
        $videoSrc = $(this).data("src");
    });
    $('#myModal').on('shown.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc + "?rel=0&amp;showinfo=0&amp;modestbranding=1&amp;autoplay=1");
    })
    $('#myModal').on('hide.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc);
    })


});


window.document.onkeydown = function (e) {
    if (!e) {
        e = event;
    }
    if (e.keyCode == 27) {
        lightbox_close();
    }
}

function info_item_clicked(e) {
    var item = items_cache[e.currentTarget.id];
    if (item.type === "mp4") {
        show_mp4_video(item);
    } else if (item.type === "youtube") {
        show_youtube_video(item);
    }
}

function show_mp4_video(item) {
    var lightBoxVideo = document.getElementById("VisaChipCardVideo");
    // lightBoxVideo.src = "https://www.w3schools.com/html/mov_bbb.mp4";
    lightBoxVideo.src = item.item;
    // lightBoxVideo.src = "https://youtube.com/embed/1xeYl-Ak3qQ";
    window.scrollTo(100, 100);
    var light_div = document.getElementById('light');
    light_div.style.display = 'block';
    document.getElementById('fade').style.display = 'block';
    lightBoxVideo.play();
    var image_height = parseInt(getComputedStyle(light_div).height);
    var body_height = $(window).height();
    light_div.style.top = (body_height / 2 - image_height / 2).toString();
}

function lightbox_close() {
    var lightBoxVideo = document.getElementById("VisaChipCardVideo");
    document.getElementById('light').style.display = 'none';
    document.getElementById('fade').style.display = 'none';
    lightBoxVideo.pause();
}


function show_youtube_video(item) {
    var $videoSrc = item.item;
    // $videoSrc = $(this).data("src");
    $('#myModal').on('shown.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc + "?rel=0&amp;showinfo=0&amp;modestbranding=1&amp;autoplay=1");
    })
    $('#myModal').on('hide.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc);
    })

}


function add_info_items(where, items) {
    var id_index = 0;
    $.each(items, function (i, v) {
        var id = "info-item-" + i;
        items_cache[id] = v;
        var div_string = "<div class='thin-green-border'>";
        
        if(v.type === "mp4") {
            div_string += "<a class='info-item-text' id='" + id + "'>" + v.text + "</a>";
        } else if (v.type === "youtube") {
            div_string += "<a class='info-item-text video-btn img-fluid cursor-pointer' data-toggle='modal' data-src='" + v.item + "' data-target='#myModal' id='" + id + "'>" + v.text + "</a>";
        }
        div_string += "</div>";
        where.append(div_string);
    });
    $(".info-item-text").on("click", info_item_clicked);
}