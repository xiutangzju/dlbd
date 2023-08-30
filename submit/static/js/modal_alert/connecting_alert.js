$(function () {
    // 设置局部刷新
    setConnectingEvent();
    // 当改变数据库时，url自动改变
    // bindSelectDataSourceEvent();
    // 当输入信息改变时，自动改变url
    // bindInputChangeURLEvent();
    // 绑定标签页的点击事件
    bindTabClickEvent();
    // 仅提交数据库名事件
    bindBtnSubmitDatabaseName();
})

function setConnectingEvent() {
    let option = {
        // target: "#connecting_database div div div:last",
        url: '/connect_public_database/',
        type: "post",
        // 在表单数据的基础上新增数据
        // data: {"type": 1},
        dataType: "JSON",
        success: function (data) {
            console.log(data);
            if (data.status === "success") {
                $('#form_public_database div div span').text("");
                $('#icon_connecting').addClass("glyphicon glyphicon-ok-circle");
            } else {
                $('#form_public_database div div span').each(function (i) {
                    $(this).text(data.errors[i]);
                });
            }
        }
    };
    $(document).on('submit', '#form_public_database', function () {
        $(this).ajaxSubmit(option);
        return false;
    });
}

function bindBtnSubmitDatabaseName() {
    $(document).on("click", "#btn_submit_database_name", function () {
        $.ajax({
            url: "/connect_server_database/",
            type: "post",
            data: {
                "database_name": $("#input_database_name").val(),
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
            },
            dataType: "JSON",
            success: function (data) {
                $('#modal_for_all').modal("hide");
                if (data.status === 'success') {
                    message_alert.message("Connecting successfully", "success");
                } else {
                    message_alert.message("You have " + data.status + " yet!", "danger");
                }
            }
        })
    });
}

// function bindSelectDataSourceEvent() {
//     $(document).on("change", "#select_data_source", function () {
//         let id = $("#select_data_source").val();
//         $("#id_port").val(data_source[id][2]);
//         let url = data_source[id][3] + $("#id_host").val() + ":" + data_source[id][2];
//         $("#id_url").val(url);
//     })
// }

// function bindAutoChangeURLEvent() {
//     let id = $("#select_data_source option:selected").val();
//     let url = data_source[id][3] + $("#id_host").val() + ":" + $("#id_port").val();
//     $("#id_url").val(url);
// }

// function bindInputChangeURLEvent() {
//     $(document).on("input propertychange", "#id_host", function () {
//         bindAutoChangeURLEvent();
//     });
//     $(document).on("input propertychange", "#id_port", function () {
//         bindAutoChangeURLEvent();
//     });
// }

function bindTabClickEvent() {
    $(document).on("click", "#tab_connection_choice li a", function (e) {
        e.preventDefault();
        $(this).tab('show');

        $('#tab_connection_choice li a')
            .removeClass("tab-a-focus").addClass("tab-a")
            .next().removeClass("tab-hr-focus").addClass("tab-hr");
        $(this)
            .removeClass("tab-a").addClass("tab-a-focus")
            .next().removeClass("tab-hr").addClass("tab-hr-focus");
    });
}