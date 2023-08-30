$(function () {
    // 设置模式图中的点击事件
    setSchemaGraphClickEvent();
})

function initArea1() {
    $.ajax({
        url: '/area1/',
        type: 'get',
        async: "false",
        success: function (data) {
            $('#area1').empty().append(data);
            initSchemaGraph();
        }
    })
}

// 根据节点ID在data.tables中寻找当前节点对象
function getCurNodeInTable(node_id) {
    node_id = Number(node_id);
    let table_num = data.tables.length;
    for (let i = 0; i < table_num; ++i) {
        if (node_id <= Number(data.tables[i].nodes[data.tables[i].nodes.length - 1].id)) {
            let cur_node = getCurNodeInArray(node_id, data.tables[i].nodes);
            if (cur_node != null) return cur_node;
        }
    }
    return null;
}

// 根据节点ID获取数组中的节点对象
function getCurNodeInArray(node_id, nodes) {
    node_id = Number(node_id);
    let node_num = nodes.length;
    // 此处不能使用forEach，因forEach是匿名函数，其不能用return终止循环，return返回的值也无效
    for (let i = 0; i < node_num; ++i) {
        if (node_id === Number(nodes[i].id))
            return nodes[i];
    }
    return null;
}

function initSchemaGraph() {
    let [cur_nodes, cur_links] = HandleSchemaGraphData();

    // 开始绘制
    let e = document.getElementById("area1");
    let e_width = e.offsetWidth, e_height = e.offsetHeight;
    let chart = SchemaGraph({
        original_nodes: cur_nodes,
        original_links: cur_links
    }, {
        width: e_width * 0.75,
        height: e_height - 70,
    });
    $('#div_schema_graph').empty().append(chart);
}

// 拼接数据
function HandleSchemaGraphData() {
    let cur_nodes = [];
    data.tables.forEach(table => {
        cur_nodes = cur_nodes.concat(table.nodes);
    });
    let cur_links = [];
    data.intra_links.forEach(link => {
        cur_links = cur_links.concat(link);
    })
    cur_links = cur_links.concat(data.external_links);

    return [cur_nodes, cur_links];
}

function setSchemaGraphClickEvent() {
    $(document).on("click", "#div_schema_graph svg g g", function (e) {
        // 获取id
        let tmp_array = $(this).attr("id").split("_");
        let id = Number(tmp_array[tmp_array.length - 1]);

        let cur_node = getCurNodeInTable(id);
        $('#node_name').text(cur_node.name);
        if (cur_node.node_type)
            $('#node_type').text("Column Node");
        else $('#node_type').text("Table Node");
        $('#data_type').text(cur_node.data_type);
        $('#table_name').text(data.tables[cur_node.group - 1].name);
    });
}
