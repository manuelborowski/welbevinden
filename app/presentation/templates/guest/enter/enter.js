var stage_2_div = $(".stage-2")
var all_tabs = []
$(document).ready(function() {

    setInterval(function () {
        check_server();
    }, 5000);

    $(".nav-link").on("click", function(){ switch_to_tab($(this))});

    // debug
    stage_2_div.show();

});

function check_server() {
    var jd = {
        "action": "get-timeout-1",
        "code": config.code,
    };
    $.getJSON(Flask.url_for(config.check_server_endpoint, {'jds': JSON.stringify(jd)}),
        function (jd) {
            if (jd.status) {
                stage_2_div.show();
            } else {
            }
        });
}


function switch_to_tab(tab_this) {
    console.log(tab_this);
    $(".nav-link").removeClass('active');
    tab_this.addClass('active');

    var div_id = tab_this[0].id.split("-")[0] + "-div";
    $(".nav-divs").hide();
    $("#" + div_id).show()
}