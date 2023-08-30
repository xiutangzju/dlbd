function SearchSpaceGraph(
    {
        original_nodes,
        original_links,
    }, {
        nodeId = d => d.id,
        nodeType = d => d.node_type,
        tableNodeRadius = 7,
        columnNodeRadius = 5,
        linkType = d => d.link_type,
        linkColor,
        types,
        width = 450,
        height = 300,
        nodeColor = ["#6495ED", "#2E8B57"],
        tableNodesDistance = 80,
        tableAndColNodesDistance = 40,
        invalidation,
    } = {}) {
    let links = [];
    $.extend(true, links, original_links);
    links.forEach(d => {
        d.source = "search_space_" + d.source;
        d.target = "search_space_" + d.target;
    });
    let link_num = links.length;
    for (let i = link_num - 1; i >= 0; --i) {
        links[i].link_type ? addLinks(links, i, table_to_table_types) : addLinks(links, i, table_to_column_types);
    }
    let nodes = [];
    $.extend(true, nodes, original_nodes);
    nodes.forEach(d => d.id = "search_space_" + d.id);

    types = Array.from(new Set(links.map(d => d.type)));
    d3.schemePaired[10] = d3.schemePaired[11];
    linkColor = d3.scaleOrdinal(types, d3.schemePaired);

    // console.log(original_links);
    // console.log(nodes);

    // 建立力导向
    const forceNode = d3.forceManyBody().strength(-400);
    const forceLink = d3.forceLink(links)
        .id(nodeId)
        .distance(d => {
            return linkType(d) ? tableNodesDistance : tableAndColNodesDistance;
        });

    const simulation = d3.forceSimulation(nodes)
        .force("link", forceLink)
        .force("charge", forceNode)
        .force("x", d3.forceX())
        .force("y", d3.forceY());

    const svg = d3.create("svg")
        .attr("class", "svg-search-space-graph")
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; max-height: 100%; height: auto; height: intrinsic; font: 12px sans-serif");

    // Per-type markers, as they don't inherit styles.
    svg.append("defs").selectAll("marker")
        .data(types)
        .join("marker")
        .attr("id", d => `arrow_${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -0.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", linkColor)
        .attr("d", "M0,-5L10,0L0,5");

    // svg.append("g")
    //     .append("rect")
    //     .attr("x", 0)
    //     .attr("y", 0)
    //     .attr("width", 180)
    //     .attr("height", 25)
    //     .attr("transform", `translate(${-width / 2}, ${-height / 2})`)
    //     .attr("fill", "#f5f5f5");
    //
    // svg.append("g")
    //     .append("line")
    //     .attr("x1", 0)
    //     .attr("y1", 0)
    //     .attr("x2", `${width / 3 * 2}`)
    //     .attr("y2", 0)
    //     .attr("transform", `translate(${-width / 2},${-height / 2})`)
    //     .attr("stroke", "darkgrey")
    //     .attr("stroke-width", 1.5);
    //
    // svg.append("g")
    //     .append("text")
    //     .attr("x", 15)
    //     .attr("y", 15)
    //     .text("Query Space Exploration")
    //     .attr("transform", `translate(${-width / 2}, ${-height / 2})`);

    const link = svg.append("g")
        .attr("fill", "none")
        .attr("stroke-width", 1.5)
        .selectAll("path")
        .data(links)
        .join("path")
        .attr("stroke", d => linkColor(d.type))
        .attr("marker-end", d => `url(${new URL(`#arrow_${d.type}`, location)})`);

    const node = svg.append("g")
        .attr("stroke-linecap", "round")
        .attr("stroke-linejoin", "round")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .attr("id", d => `search_space_${nodeId(d)}`)
        .attr("fill", d => nodeColor[nodeType(d)])
        .call(searchSpaceGraph(simulation));

    node.append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1.5)
        .attr("r", d => nodeType(d) ? columnNodeRadius : tableNodeRadius);

    node.append("text")
        .attr("x", 8)
        .attr("y", "0.31em")
        .text(d => d.name)
        .clone(true).lower()
        .attr("fill", "none")
        .attr("stroke", "white")
        .attr("stroke-width", 3);

    simulation.on("tick", () => {
        link.attr("d", linkArc);
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    if (invalidation != null) invalidation.then(() => simulation.stop());

    function linkArc(d) {
        let curvature = 0;
        switch (d.type) {
            case "inner join":
                curvature = 42;
                break;
            case "left outer join":
            case "projection":
                curvature = 27;
                break;
            case "right outer join":
            case "group by":
                curvature = 12;
                break;
            case "cross join":
            case "join column":
                curvature = -12;
                break;
            case "semi join":
            case "filter":
                curvature = -27;
                break;
            case "anti join":
                curvature = -42;
                break;
            default:
                break;
        }
        // let [control1_x, control1_y, control2_x, control2_y] =
        //     calControlPoint(d.source.x, d.source.y, d.target.x, d.target.y, curvature);
        // return `
        // M${d.source.x},${d.source.y}
        // C${control1_x},${control1_y},${control2_x},${control2_y},${d.target.x},${d.target.y}`;
        let [control_x, control_y] = calControlPoint(d.source.x, d.source.y, d.target.x, d.target.y, curvature);
        return `M${d.source.x},${d.source.y}Q${control_x},${control_y},${d.target.x},${d.target.y}`;
    }

    function calControlPoint(start_x, start_y, end_x, end_y, curvature) {
        // 三次贝塞尔曲线
        // 两个控制点
        // let control1_x, control1_y, control2_x, control2_y, k = undefined;
        // let gap_x = (end_x - start_x) / 4, gap_y = (end_y - start_y) / 4;
        // let middle1_x = start_x + gap_x, middle1_y = start_y + gap_y, middle2_x = end_x - gap_x, middle2_y = end_y - gap_y;
        // // 计算控制点坐标
        // if (start_x === end_x) {
        //     // 不能计算斜率
        //     control1_x = middle1_x + curvature;
        //     control1_y = middle1_y;
        //     control2_x = middle2_x + curvature;
        //     control2_y = middle2_y;
        // } else {
        //     k = (end_y - start_y) / (end_x - start_x);
        //     let offset = Math.sqrt(Math.pow(curvature, 2) / (Math.pow(k, 2) + 1));
        //     offset = (curvature >= 0) ? offset : -offset;
        //     control1_x = middle1_x - k * offset;
        //     control1_y = middle1_y + offset;
        //     control2_x = middle2_x - k * offset;
        //     control2_y = middle2_y + offset;
        // }
        // return [control1_x, control1_y, control2_x, control2_y];

        // 二次贝塞尔曲线
        let middle_x = (end_x + start_x) / 2, middle_y = (end_y + start_y) / 2;
        let control_x, control_y;
        if (start_x === end_x) {
            control_x = start_x + curvature;
            control_y = middle_y;
        } else {
            let k = (end_y - start_y) / (end_x - start_x);
            let offset = Math.sqrt(Math.pow(curvature, 2) / (Math.pow(k, 2) + 1));
            offset = (curvature >= 0) ? offset : -offset;
            control_x = middle_x - k * offset;
            control_y = middle_y + offset;
        }
        return [control_x, control_y];

    }

    // 向search_space_links中加入新的type的边
    function addLinks(links, i, types) {
        links[i].type = types[0];
        let len = types.length;
        for (let j = 1; j < len; ++j) {
            let tmp_link = {};
            $.extend(true, tmp_link, links[i]);
            tmp_link.type = types[j];
            links.splice(i + 1, 0, tmp_link);
        }
    }

    function searchSpaceGraph(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    return [svg.node(), linkColor];
}