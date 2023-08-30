$(function () {
    setRegisterEvent();
})

function setRegisterEvent() {
    let option = {
        // target: "#connecting_database div div div:last",
        url: '/register/',
        type: "post",
        dataType: "JSON",
        // 这里不能用beforeSubmit，处理事件的先后顺序是先序列化后再处理提交事件
        beforeSerialize: function () {
            if($('#id_password').val() !== "")
                $("#id_password").val(md5($('#id_password').val()));
            if($('#id_confirm_password').val() !== "")
                $('#id_confirm_password').val(md5($('#id_confirm_password').val()));
        },
        success: function (data) {
            if (data.status === "success") {
                // 弹出提示消息
                $('#modal_register').modal('hide');
                message_alert.message("Register successfully!", "success");
            } else {
                $('#form_register div span').each(function (i) {
                    $(this).text(data.errors[i]);
                });
            }
        },
    };
    $(document).on('submit', '#form_register', function () {
        $(this).ajaxSubmit(option);
        return false;
    });
}