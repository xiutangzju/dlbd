function ajax_load_alert(url, width, title) {
    $.ajax({
        url: url,
        type: "get",
        success: function (data) {
            if (typeof data === "object") {
                $('#modal_for_all').modal('hide');
                message_alert.message("You have " + data.status + " yet!", "danger");
            } else {
                // 设置模态框
                $('#modal_for_all')
                    .modal('show')
                    .children(".modal-dialog").css("width", width)
                    .find('#modal_title').text(title)
                    .parent().next().append(data);
            }
        }
    })
}