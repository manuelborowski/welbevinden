$(document).ready(function(){
    var type_sel = $("#user_type");
    var change_sel = $("#change_password");
    var passwords_div = $("#passwords_div");
    var change_password_div = $("#change_password_div");
    var original_type = type_sel.val();
    
    type_sel.change(visibility_passwords);
    change_sel.change(visibility_passwords);
    visibility_passwords();

    function visibility_passwords() {
        if (original_type == "oauth" || "{{common_details.action}}" == "add") {
            if (type_sel.val() == "oauth") {
                passwords_div.hide();
                change_password_div.hide();
            } else {
                passwords_div.show();
                change_password_div.hide();
                change_sel.val('True');
            }
        } else {
            if (type_sel.val() == "oauth") {
                passwords_div.hide();
                change_password_div.hide();
            } else {
                if(change_sel.val() == "True") {
                    passwords_div.show();
                } else {
                    passwords_div.hide();
                }
                change_password_div.show();
            }
        }
    }
});

