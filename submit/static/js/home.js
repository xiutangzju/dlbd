$(function () {
    // 初始化用户头像
    initUserImg();
    // 初始化页面
    initHomePage();
    // 绑定登录按钮的点击事件
    bindBtnLogin();
    // 绑定注册按钮的点击事件
    bindBtnRegister();
    // 绑定登出按钮的点击事件
    bindBtnLogout();
    // 绑定connecting按钮的点击事件
    bindBtnConnecting();
    // 上传dataset事件
    bindUploadDatasetEvent();
    // 绑定generate按钮的点击事件
    bindBtnGenerate();
    // 设置session
    setSession();
    // 绑定start按钮的点击事件
    bindBtnStart();
    // 绑定pause按钮的点击事件
    bindBtnPause();

    // 设置模态框关闭的监听事件
    listeningModalForAllCloseEvent();
    listeningRegisterModalCloseEvent();
})

function initUserImg() {
    $.ajax({
        url: "/user_img/",
        type: "get",
        success: function (data) {
            $('#dropdown_user_info').children("img")
                .attr("src", "../static/img/" + data + ".png");
            if (data !== "user") {
                // 已经存在cookie
                // 改变登录按钮、登出按钮的状态
                $('#btn_login')
                    .attr("disabled", true)
                    .css("color", "#8a8a8a");
                $('#btn_logout')
                    .attr("disabled", false)
                    .css("color", "black");
            }
        }
    })
}

function initHomePage() {
    initPage();
    $.ajax({
        url: "/detection_status/",
        type: "get",
        dataType: "JSON",
        success: function (res) {
            if (res.status === "success") {
                if (res.detection_status !== "none") {
                    $('#btn_start')
                        .removeClass("btn-success").addClass("btn-danger")
                        .children("span:first").removeClass().addClass("glyphicon glyphicon-stop")
                        .next("span").text("Stop");
                    $('#btn_pause').attr("disabled", false);

                    if (res.detection_status === "start") {
                        setPolling();
                    } else {
                        $('#btn_pause')
                            .removeClass("btn-warning").addClass("btn-success")
                            .children("span:first").removeClass().addClass("glyphicon glyphicon-play")
                            .next("span").text("Continue");
                    }
                }
            }
        }
    })
}

function initPage() { //这里是在点击start之后进行一系列的初始化操作
    let cur_step = getCurStep();
    if (cur_step >= 4) {
        generateEvent();
        if (cur_step >= 5) {
            setTimeout(function () {
                initArea2();
                initArea3();
                initArea4();
                setTimeout(function () {
                    $.ajax({
                        url: "/review/",
                        type: "get",
                        async: "false",
                        success: function (res) {
                            if (res.status === "success") {
                                loadData(res);
                            }
                        }
                    })
                }, 100);
            }, 100);
        }
    }
}

function bindBtnLogin() {
    $('#btn_login').click(function () {
        ajax_load_alert("/login/", "450px", "Login");
    });
}

function bindBtnRegister() {
    $('#btn_register').click(function () {
        $.ajax({
            url: "/register/",
            type: "get",
            success: function (data) {
                // 设置模态框
                $('#modal_register').find(".modal-body").append(data);
            }
        })
    });
}

function bindBtnLogout() {
    $('#btn_logout').click(function () {
        let msg = confirm("Do you confirm to logout?");
        if (msg === true) {
            $.ajax({
                url: "/logout/",
                type: "get",
                dataType: "JSON",
                success: function (data) {
                    if (data.status === "success") {
                        message_alert.message("Logout successfully", "success");

                        $('#dropdown_user_info').children('img')
                            .attr("src", "../static/img/user.png");

                        // 改变登录按钮、登出按钮的状态
                        $('#btn_logout')
                            .attr("disabled", true)
                            .css("color", "#8a8a8a");
                        $('#btn_login')
                            .attr("disabled", false)
                            .css("color", "black");

                        // 将四个区域内容置空
                        $('#area1').empty();
                        $('#area2').empty();
                        $('#area3').empty();
                        $('#area4').empty();
                    }
                }
            })
        } else {
            return;
        }
    });
}

function bindBtnConnecting() {
    $('#btn_connecting').click(function () {
        ajax_load_alert("/get_connecting_alert/", "600px", "Connecting Database");
    });
}

function getCurStep() {
    let cur_step = 0;
    // 同步
    $.ajax({
        url: "/get_step/",
        type: "get",
        async: false,
        dataType: "JSON",
        success: function (data) {
            if (data.status === "success") {
                cur_step = data.cur_step;
            } else {
                message_alert.message("You have " + data.status + " yet!", "danger");
            }
        }
    })
    return cur_step;
}

function bindUploadDatasetEvent() {
    $('#btn_dataset_upload').click(function () {
        $('#dataset_upload').trigger("click");
    });

    $('#dataset_upload').change(function () {
        // 首先获取当前的step
        let cur_step = getCurStep();
        if (cur_step < 2) {
            message_alert.message("You have not connected yet!", "danger");
            return;
        } else if (cur_step >= 3) {
            let msg = confirm("Do you confirm to upload the file? Which means that your database will be cleaned!");
            if (msg === false) {
                return;
            }
        }

        let file = $('#dataset_upload')[0].files[0];
        let form_file = new FormData();
        form_file.append('file', file);
        $.ajax({
            url: '/upload/',
            type: "post",
            data: form_file,
            processData: false,
            contentType: false,
            success: function (data) {
                if (data.status === "success") {
                    alert("upload dataset success: " + file.name);
                } else {
                    message_alert.message("You have " + data.status + " yet!", "danger");
                }
            },
        });
    });
}

function setSession() {
    if (!sessionStorage.getItem("step")) {
        // alert("当前还没有session")
        sessionStorage.setItem("step", "0");
    }
}

function generateEvent() {
    $.ajax({
        url: '/generate/',
        type: 'get',
        dataType: 'JSON',
        async: "false",
        success: function (res) {
            if (res.status === "success") {
                data = res;
                initArea1();
            } else {
                message_alert.message("You have " + res.status + " yet!", "danger");
            }
        }
    });
}

function bindBtnGenerate() {
    $('#btn_generate').click(function () {
        generateEvent();
    });
}

function bindBtnStart() {
    $('#btn_start').click(function () {
        if ($(this).children("span:first").attr("class") === "glyphicon glyphicon-play") {
            let cur_step = getCurStep();
            if (cur_step < 4) {
                message_alert.message("You have not generated yet!", "danger");
                return;
            }

            $.ajax({
                url: '/start/',
                type: 'get',
                async: false,
                dataType: 'JSON',
                success: function (res) {
                    if (res.status === "success") {
                        message_alert.message("Start detection!", "success");
                    }
                }
            })

            // 判断是否需要加载area1
            let cur_area1 = $('#area1').children().html();
            if (cur_area1 == null || cur_area1.length === 0) {
                $('#btn_generate').trigger("click");
            }
            initArea2();
            initArea3();
            initArea4();
            setPolling();

            // 改变按钮状态
            $('#btn_start')
                .removeClass("btn-success").addClass("btn-danger")
                .children("span:first").removeClass().addClass("glyphicon glyphicon-stop")
                .next("span").text("Stop");
            if ($('#btn_pause').children("span:first").attr("class") === "glyphicon glyphicon-play")
                $('#btn_pause')
                    .removeClass("btn-success").addClass("btn-warning")
                    .children("span:first").removeClass().addClass("glyphicon glyphicon-pause")
                    .next("span").text("Pause");
            $('#btn_pause').attr("disabled", false);
        } else {
            $.ajax({
                url: "/stop_detection/",
                type: "get",
                dataType: 'JSON',
                success: function (res) {
                    if (res.status === "success") {
                        message_alert.message("Stop detection!", "success");
                    }
                }
            })

            $(this)
                .removeClass("btn-danger").addClass("btn-success")
                .children("span:first").removeClass().addClass("glyphicon glyphicon-play")
                .next("span").text("Start");
            $('#btn_pause')
                .removeClass("btn-success").addClass("btn-warning")
                .attr("disabled", true)
                .children("span:first").removeClass().addClass("glyphicon glyphicon-pause")
                .next("span").text("Pause");
            pause_prog();
        }
    })
}

function bindBtnPause() {
    $("#btn_pause").click(function () {
        if ($(this).children("span:first").attr("class") === "glyphicon glyphicon-pause") {
            $(this)
                .removeClass("btn-warning").addClass("btn-success")
                .children("span:first").removeClass().addClass("glyphicon glyphicon-play")
                .next("span").text("Continue");

            $.ajax({
                url: "/pause_detection/",
                type: "get",
                dataType: "JSON",
                success: function (res) {
                    if (res.status === "success") {
                        message_alert.message("pause success", "success");
                    }
                }
            })

            pause_prog();
        } else {
            $(this)
                .removeClass("btn-success").addClass("btn-warning")
                .children("span:first").removeClass().addClass("glyphicon glyphicon-pause")
                .next("span").text("Pause");

            $.ajax({
                url: "/continue_detection/",
                type: "get",
                dataType: "JSON",
                success: function (res) {
                    if (res.status === "success") {
                        message_alert.message("continue to detection", "success");
                    }
                }
            })

            if (!is_polling) {
                setPolling();
            } else {
                continue_prog();
            }
        }
    });
}
let x = 100;//模拟每次处理的查询语句大小
function creatQueryNum(){
    x = x+(Math.floor(Math.random() * (1001)) + 1000)
    return x;
}

function loadData(res) {
    res.bug_list.forEach(bug => {
        loadBug(bug);
        load_pie_data(bug.operator);
    })
    $('#query_num').text(creatQueryNum());//这里放置一个增加数值的函数
    $('#query_type_num').text(res.bug_type);//这里存放种类bug的种类
    $('#bug_num').text($('#table_wrong_info tbody tr').length - 1);
}

/* 此处的函数调用说明“页面框架加载完成后自动执行”指的是当其它所有内容（包括JS）执行完毕后（统称页面加载）最后自动执行这些函数。
在页面加载过程中，当JS中有单独的、不以函数体形式存在的JS语句时，也会自动执行这些语句。
*/
function setPolling() {
    is_polling = true;
    let polling = setInterval(frame, 1000);

    function frame() {
        $.ajax({
            url: "/polling/",
            type: 'get',
            success: function (res) {
                if (res.status === "success") {
                    loadData(res);
                }
            }
        });
    }

    function pauseEvent() {
        clearInterval(polling);
    }

    function continueEvent() {
        polling = setInterval(frame, 1000);
    }

    pause_prog = pauseEvent;``
    continue_prog = continueEvent;
}

function listeningModalForAllCloseEvent() {
    $('#modal_for_all').on("hide.bs.modal", function () {
        // 这一句不能放在下一次初始化模态框之前，这样的话模态框关闭后，里面的元素没有删掉，防止出现同id的元素
        setTimeout(function () {
            $('#modal_for_all').find('.modal-body').empty();
        }, 500);
    })
}

function listeningRegisterModalCloseEvent() {
    $('#modal_register').on("hide.bs.modal", function () {
        setTimeout(function () {
            $('#modal_register').find('.modal-body').empty();
        }, 500);
    })
}