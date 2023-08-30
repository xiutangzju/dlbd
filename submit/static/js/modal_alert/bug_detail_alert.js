$(function () {//放在这里是为了保证在文档加载完再进行这些函数
    // 在此处绑定这个事件没有作用，具体看下面解释
    // bindScrollBar();
    setSameDisplayOfMouseEvent();  // 设置真值表和查询结果表同步鼠标事件
    bindBtnShowWrongDetail(); // 设置错误列表中Detail按钮的点击事件
    bindBtnChangeQueryTypeEvent(); // 设置original Query和simplified Query的转换事件
    bindBtnRetest(); // 设置detail模态框中的retest事件
    // 设置execution plan每一行的点击事件
    // setExecutionPlanSpanClickEvent();
    // 设置模态框关闭的监听事件
    listeningBugModalCloseEvent();
    downloadsqlfile();//下载sql文件
})

function setExecutionPlan(execution_plan) {
    let plans = execution_plan.split("\n");
    let margin_left = 0;
    $('#execution_plan').empty().append($('<br>'))
    plans.forEach((plan, index) => {
        if (index > 0) $('#execution_plan').append($('<br>'));
        $('#execution_plan').append(
            $('<span>')
                .attr("row_id", index)
                .css({"margin-left": margin_left})
            //     .append(
            //     $('<img>')
            //         .attr("src", "../static/img/ul-icon-black.png")
            //         .css({"margin-right": "3px", "margin-bottom": "2px"})
            // )
                .append(
                $('<span>').text(plan)
            )
        );
        if (index === plans.length - 2) margin_left = 0;
        else if (index !== 2) margin_left += 30;
    });
}

// function setExecutionPlanSpanClickEvent() {
//     $(document).on("click", "#execution_plan span", function () {
//         $('#execution_plan span').removeClass("execution-plan-span-focus");
//         $(this).addClass("execution-plan-span-focus");
//         switch ($(this).attr("row_id")) {
//             case "0":
//                 setResultTables(ground_truth_test1, query_result_test1);
//                 break;
//             case "1":
//                 setResultTables(ground_truth_test2, query_result_test2);
//                 break;
//             case "6":
//                 setResultTables(ground_truth_test6, query_result_test6);
//                 break;
//             default:
//                 break;
//         }
//     });
// }

// 将后端传入的真值和查询结果字符串转换为数组
function stringToArray(str) {
    let array = str.split("/");
    array.forEach((tr, i) => {
        array[i] = tr.split(";");
    });
    return array;
}

// 比对真值数组和查询结果数组，选出不同的
function matchTruthAndResult(truth_list, result_list) {
    let truth_match = Array(truth_list.length).fill(false, 0, truth_list.length);
    let result_match = Array(result_list.length).fill(false, 0, result_list.length);

    truth_list.forEach((truth, i) => {
        for (let j = 0; j < result_list.length; ++j) {
            if (result_match[j])
                continue;

            // 判断当前行的真值和当前行的查询结果是否相等
            let tmp_array = [...truth];
            tmp_array.push(...result_list[j]);
            let tmp_set = new Set(tmp_array);
            if ([...tmp_set].length === result_list[j].length) {
                // 两者相同
                truth_match[i] = true;
                result_match[j] = true;
            }
        }
    });

    return {truth_match, result_match};
}

// 生成表格元素
function createTable(array, table_id, match, not_match_class) {
    let cur_e = $("#" + table_id + " tbody");
    cur_e.empty();

    array.forEach((tr, i) => {
        cur_e.append($('<tr>'));
        tr.forEach((td, j) => {
            cur_e.children("tr:last").append(
                i === 0 ? $('<th>').text(td) : $('<td>').text(td));
            if (!match[i]) {
                cur_e.children("tr:last").children("td:last").addClass(not_match_class);
            }
        })
    });
}

function setResultTables(cur_ground_truth, cur_query_result) {
    let truth_list = stringToArray(cur_ground_truth);
    let result_list = stringToArray(cur_query_result);

    let {truth_match, result_match} = matchTruthAndResult(truth_list, result_list);

    createTable(truth_list, "table_ground_truth", truth_match, "td-right");
    createTable(result_list, "table_query_result", result_match, "td-wrong");
}

function bindBtnShowWrongDetail() { //展示错误列表
    $(document).on("click", "#table_wrong_info tbody tr td button", function (e) {
        let bug_id = $(this).attr("bug_id");
        $.ajax({
            url: '/bug_detail/',
            type: 'get',
            data: {
                "bug_id": bug_id
            },
            success: function (data) {
                // $('#modal_wrong_detail').find(".modal-content").append(data);
                $('#modal_wrong_detail').find(".modal-body").append(data);
                getDynamicData(bug_id, "original")

                bindScrollBar();
            }
        })
    });
}

function getDynamicData(bug_id, detail_type) {
    $.ajax({
        url: "/dynamic_bug_detail/",
        type: 'get',
        data: {
            "bug_id": bug_id,
            "detail_type": detail_type
        },
        dataType: "JSON",
        success: function (res) {
            if (res.status === "success") {
                $('#wrong_detail_query').text(res.bug[0]);
                setResultTables(res.bug[1], res.bug[2]);
                setExecutionPlan(res.bug[3]);
            }
        }
    })
}

/* 此处由于scroll事件不会冒泡，而$(document).on()是基于冒泡事件做的，
所以此处无法用$(document).on()为动态添加的元素绑定滚动条监听事件
此处使用以下简易方法：在构造好模态框之后，再声明此函数，即可成功绑定监听事件
* */
function bindScrollBar() {
    $('#div_ground_truth').scroll(function () {
        $('#div_query_result')
            .scrollTop($('#div_ground_truth').scrollTop())
            .scrollLeft($('#div_ground_truth').scrollLeft());
    });
    $('#div_query_result').scroll(function () {
        $('#div_ground_truth')
            .scrollTop($('#div_query_result').scrollTop())
            .scrollLeft($('#div_query_result').scrollLeft());
    });
}

function setSameDisplayOfMouseEvent() {
    $(document).on("mouseenter", "#table_ground_truth tbody tr *", function () {
        // 为当前hover的元素添加样式
        let row = $(this).parent().index();
        let col = $(this).index();
        let td_query_res = $('#table_query_result tr').eq(row).children().eq(col);

        td_query_res.attr("class") === "td-wrong" ?
            td_query_res.removeClass("td-wrong").addClass("td-wrong-hover") :
            td_query_res.addClass("active");
    });
    $(document).on("mouseenter", "#table_query_result tbody tr *", function () {
        let row = $(this).parent().index();
        let col = $(this).index();
        let td_ground_truth = $('#table_ground_truth tr').eq(row).children().eq(col);

        td_ground_truth.attr("class") === "td-right" ?
            td_ground_truth.removeClass("td-right").addClass("td-right-hover") :
            td_ground_truth.addClass("active");
    });
    $(document).on("mouseleave", "#table_ground_truth tbody tr *", function () {
        $('#table_query_result tr').children().removeClass("active");
        $('#table_query_result tr').children().filter(".td-wrong-hover")
            .removeClass("td-wrong-hover")
            .addClass("td-wrong");
    });
    $(document).on("mouseleave", "#table_query_result tbody tr *", function () {
        $('#table_ground_truth tr').children().removeClass("active");
        $('#table_ground_truth tr').children().filter(".td-right-hover")
            .removeClass("td-right-hover")
            .addClass("td-right");
    });
}

// 修改original query和minimal query两个按钮的状态-图标、颜色
function changeBtnStatus(cur_e, another_e) {
    if (cur_e.children("span").attr("class") !== "glyphicon glyphicon-ok") {
        cur_e
            .removeClass("btn-primary").addClass("btn-success")
            .children("span").addClass("glyphicon glyphicon-ok");
        another_e
            .removeClass("btn-success").addClass("btn-primary")
            .children("span").removeClass("glyphicon glyphicon-ok");
    }
}

function bindBtnChangeQueryTypeEvent() { //转换Minimal和Original
    $(document).on("click", "#btn_minimal_query", function () {//点击了对应id的按钮，才会触发后续函数
        changeBtnStatus($(this), $('#btn_original_query')); //调用上面的函数，将两个按钮作为参数传进去
        let bug_id = $("#table_bug_detail").attr("bug_id"); //这里获取了bug_id！！
        getDynamicData(bug_id, "minimal");
        // $('#wrong_detail_query').text(minimal_query);
        // setExecutionPlan(minimal_execution_plan);
        // setResultTables(minimal_ground_truth, minimal_query_result);
    });
    $(document).on("click", "#btn_original_query", function () {
        changeBtnStatus($(this), $('#btn_minimal_query'));
        let bug_id = $("#table_bug_detail").attr("bug_id");
        getDynamicData(bug_id, "original");
        // $('#wrong_detail_query').text(original_query);
        // setExecutionPlan(original_execution_plan);
        // setResultTables(original_ground_truth, original_query_result);
    })
}

function bindBtnRetest() {
    $(document).on("click", "#btn_retest", function () {
        let cur_wrong_id = $('#table_bug_detail').attr("bug_id");

        $.ajax({
            url: "/retest/",
            type: "get",
            dataType: "JSON",
            data: {
                "bug_id": cur_wrong_id,
            },
            success: function (res) {
                if (res.status === "success") {
                    message_alert.message("You have fixed it!", "success");
                }
            }
        });

        $('#modal_wrong_detail').modal('hide');
        $('#table_wrong_info tbody tr').each(function () {
            if (cur_wrong_id === $(this).attr("bug_id")) {
                $(this).children("td:first").empty().append(
                    $('<img>').attr("src", "/static/img/fixed.png")
                );
                $(this).children("td").eq(4).text("Fixed");
                $(this).children().css("color", "#bfbfbf");
            }
        });
    })
}

function listeningBugModalCloseEvent() {
    $('#modal_wrong_detail').on("hide.bs.modal", function () {
        setTimeout(function () {
             $('#modal_wrong_detail').find(".modal-body").empty();
            // $('#modal_wrong_detail').find(".modal-content").empty();
        }, 500);
    })
}

//let routing = "../../../../../sql_file/"+databasename+".sql";
//下面编写一个函数，实现下载sql文件的功能
function saveContentToFile(content, filename) {
  var blob = new Blob([content], { type: 'text/plain' });
  var link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(link.href);
}

function downloadsqlfile(){
    $(document).on("click", "#download", function () {
        let bug_id = $("#bug_ididid").text() ;
        let bug_sqlfile = $("#table_bug_detail").attr("bug_sqlfile");
        saveContentToFile(bug_sqlfile,"bug"+bug_id+".sql");

//目前这里啥也没有
    });
}