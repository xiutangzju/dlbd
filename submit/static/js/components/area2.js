$(function () {
    // 设置搜索空间swatch-bar的悬停事件
    setSwatchDisplayEvent();
    // 设置点击生成搜索空间图的点击事件
    bindCreateSearchSpaceGraphEvent();
})

function initArea2() {
    $.ajax({
        url: '/area2/',
        type: 'get',
        async: "false",
        success: function (data) {
            // 设置area2
            $('#area2').empty().append(data);
            let area2 = document.getElementById("area2");
            $('#div_search_space_graph')
                .css({
                    "width": "100%",
                    "height": area2.offsetHeight - 90,
                });
        }
    })
}

function bindCreateSearchSpaceGraphEvent() {
    $(document).on("click", "#btn_create_graph", function () {
        // 遍历寻找被选中的复选框
        let selected_list = [];
        let cur_nodes = [], cur_links = [];
        $("#checkbox_bar label").each(function (index) {
            if ($(this).children("input").prop('checked')) {
                selected_list.push(index);
                cur_nodes = cur_nodes.concat(data.tables[index].nodes);
                cur_links = cur_links.concat(data.intra_links[index])
            }
        });

        // 遍历寻找外键连接
        data.external_links.forEach(link => {
            if ($.inArray(link.source_group - 1, selected_list) >= 0 &&
                $.inArray(link.target_group - 1, selected_list) >= 0) {
                cur_links.push({
                    "source": data.tables[link.source_group - 1].nodes[0].id,
                    "target": data.tables[link.target_group - 1].nodes[0].id,
                    "link_type": 1
                });
            }
        });

        // 生成图
        let e = document.getElementById("div_search_space_graph");
        let e_width = e.offsetWidth, e_height = e.offsetHeight;
        let [chart, color] = SearchSpaceGraph({
            original_nodes: cur_nodes,
            original_links: cur_links,
        }, {
            width: e_width,
            height: e_height - 5,
        });

        let swatch_bar = $('<div>')
            .attr("style", "display: flex; align-items: center; margin-left: 0; font: 10px sans-serif; justify-content: center;");
        for (let i = 0; i < color.domain().length; ++i) {
            swatch_bar.append(
                $('<a>')
                    .attr({
                        "tabindex": "0",
                        "class": "btn",
                        "role": "button",
                        "data-toggle": "popover",
                        "data-trigger": "focus",
                        "data-content": color.domain()[i],
                        "style": "padding: 0; margin-right: 2px",
                    }).append(
                    $('<span>').addClass("glyphicon glyphicon-stop")
                        .css({"color": color(color.domain()[i]), "font-size": "14px"})
                )
            )
        }
        $('[data-toggle="popover"]').popover();
        swatch_color = color;

        $('#div_search_space_graph').empty().append(swatch_bar).append(chart);
    });
}

function setSwatchDisplayEvent() {
    $(document).on("mouseenter", ".glyphicon-stop", function (e) {
        $(this).parent().popover('show');
    })
    $(document).on("mouseout", ".glyphicon-stop", function (e) {
        $(this).parent().popover('hide');
    })
}

function getTranslateX(obj) {
    const style = window.getComputedStyle(obj);
    const matrix = new WebKitCSSMatrix(style.transform);
    return matrix.m41;
}

function handlePreCheck() {
    const checkListDom = $('#area2-check-list');
    let x = getTranslateX(checkListDom[0]);
    x = x + 200
    if (x >= 0) {
        x = 0
    }
    console.log(x);
    checkListDom.css({
        "transform": `translateX(${x}px)`
    })
}

function handleNextCheck() {
    const checkboxBar = $('#checkbox_bar');
    const checkListDom = $('#area2-check-list');
    let x = getTranslateX(checkListDom[0]);
    x = x - 200
    if ((checkListDom[0].clientWidth - checkboxBar[0].clientWidth) < x) {
        x = checkboxBar[0].clientWidth - checkListDom[0].clientWidth
    }
    checkListDom.css({
        "transform": `translateX(${x}px)`
    })
}
