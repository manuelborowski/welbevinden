$(function () {
    var $content = add_tab(coworker.profile + "-medewerker");
    add_chat_room($content, coworker.code);
    subscribe_to_room(coworker.profile, coworker.code, coworker.code, own_room.history);
});
