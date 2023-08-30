$(function () {
    // 设置局部刷新
    setLoginEvent();
    // 设置登录对话框中的跳转注册事件
    setSkipToRegisterEvent();
})

function setLoginEvent() {
    let option = {
        // target: "#connecting_database div div div:last",
        url: '/login/',
        type: "post",
        dataType: "JSON",
        beforeSerialize: function () {
            if ($('#id_password').val() !== "")
                $("#id_password").val(md5($('#id_password').val()));
        },
        success: function (data) {
            if (data.status === "success") {
                // 弹出提示消息
                message_alert.message("Login successfully!", "success");

                // 修改用户头像
                let username = $('#id_username').val()[0].toUpperCase();
                $('#dropdown_user_info').children('img')
                    .attr("src", "../static/img/user-" + username + ".png");

                // 改变登录按钮、登出按钮的状态
                $('#btn_login')
                    .attr("disabled", true)
                    .css("color", "#8a8a8a");
                $('#btn_logout')
                    .attr("disabled", false)
                    .css("color", "black");

                $('#modal_for_all').modal('hide');

                initPage();
            } else {
                $('#form_login div span').each(function (i) {
                    $(this).text(data.errors[i]);
                });
            }
        }
    };
    $(document).on('submit', '#form_login', function () {
        $(this).ajaxSubmit(option);
        return false;
    });
}

function setSkipToRegisterEvent() {
    $(document).on("click", "#a_register", function () {
        $('#modal_for_all').modal('hide');
        setTimeout(function () {
            $('#btn_register').trigger("click");
        }, 80);
        // $('#btn_register').trigger('click');
        // $('#btn_register').trigger("click");
        // ajax_load_alert("/register/", "450px", "Register");
    });
}