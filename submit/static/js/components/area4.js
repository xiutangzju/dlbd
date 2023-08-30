$(function () {
    // bindHighlightBugEvent();
})

function initArea4() {
    $.ajax({
        url: '/area4/',
        type: 'get',
        async: "false",
        success: function (data) {
            $('#area4').empty().append(data);
        }
    })
}

// 载入数据
function loadBug(bug) {
    $('#table_wrong_info').children().append(
        $('<tr>').addClass("form-group tr-wrong").attr("bug_id", bug.id).append(
            $('<td>').append(
                $('<img>').attr("src", bug.status ? "/static/img/fixed.png" :
                    "/static/img/S" + bug.severity + ".png")
            )
        ).append(
            $('<td>').text(bug.bug_id)
        ).append(
            $('<td>').text(bug.category)
        ).append(
            $('<td>').text(bug.operator)
        ).append(
            $('<td>').text(bug.status ? "Fixed" : "Unfixed")
        ).append(
            $('<td>').css("padding", "5px 8px").append(
                $('<button>').addClass("btn btn-primary btn-wrong-detail")
                    .attr({
                        "data-toggle": "modal",
                        "data-target": "#modal_wrong_detail",
                        "bug_id": bug.id
                    })
                    .text("Detail")
            )
        )
    );

    if (bug.status) {
        $('#table_wrong_info tbody tr:last').css("color", "#bfbfbf");
    }
}

function bindHighlightBugEvent() {
    $(document).on('click', '.tr-wrong', function () {
        if ($(this).attr("class") === "form-group tr-wrong active") {
            // 复原模式图
            $(this).removeClass("active");

            $('#div_schema_graph svg g path').each(function () {
                if ($(this).attr("type") === "1") {
                    $(this).attr({
                        "stroke": "#FF4500",
                        "marker-end": `url(${new URL(`#arrow_schema_graph_1`, location)})`
                    });
                } else {
                    $(this).attr({
                        "stroke": "#778899",
                        "marker-end": `url(${new URL(`#arrow_schema_graph_0`, location)})`
                    })
                }
            });
            $('#div_schema_graph svg g g').each(function () {
                $(this).attr("fill", $(this).attr("type") === "1" ? "#2E8B57" : "#6495ED");
            });
        } else {
            // 首先仅将当前bug行设置为高亮
            $(this).parent().children('tr').removeClass("active");
            $(this).addClass("active");

            // 高亮模式图中相关部分
            $('#div_schema_graph svg g path').each(function () {
                let link_path = $(this).attr("id").split("_")[2].split("-");
                let source = link_path[0], target = link_path[1];
                if (source < 7 || target < 7) {
                    $(this).attr({
                        "stroke": "#bfbfbf",
                        "marker-end": `url(${new URL(`#arrow_schema_graph_grey`, location)})`
                    });
                }
            });
            $('#div_schema_graph svg g g').each(function () {
                if ($(this).attr("id").split("_")[2] < 7)
                    $(this).attr("fill", "#bfbfbf");
            });

            // 重新绘制搜索空间图
            $('#checkbox_bar label input').prop("checked", false);
            $('#checkbox_bar label').eq(2).children("input").prop("checked", true);
            $('#checkbox_bar label').eq(3).children("input").prop("checked", true);
            $('#btn_create_graph').trigger("click");
        }
    });
}