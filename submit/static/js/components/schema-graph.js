// Copyright 2021 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/force-directed-graph
function SchemaGraph(
    {
        original_nodes,
        original_links
    }, {
        nodeId = d => d.id,
        nodeType = d => d.node_type,
        tableNodeRadius = 7,
        columnNodeRadius = 5,
        nodeColor = d3.scaleOrdinal([0, 1], ["#6495ED", "#2E8B57"]),
        tableNodesDistance = 100,
        tableAndColNodesDistance = 50,

        linkType = d => d.link_type,
        linkTypes = [0, 1],
        linkColor = d3.scaleOrdinal([0, 1], ["#778899", "#FF4500"]),
        linkStrokeWidth = 1.5,
        linkStrokeOpacity = 0.6,
        linkStrokeLinecap = "round",

        width = 620,
        height = 310,
    } = {}) {
    // 深拷贝数据
    const nodes = [];
    $.extend(true, nodes, original_nodes);
    nodes.forEach(node => node.id = "schema_graph_" + node.id);

    const links = [];
    $.extend(true, links, original_links);
    links.forEach(link => {
        link.source = "schema_graph_" + link.source;
        link.target = "schema_graph_" + link.target;
    });

    // 建立力导向
    const forceNode = d3.forceManyBody();
    const forceLink = d3.forceLink(links)
        .id(nodeId)
        .distance(d => {
            return linkType(d) ? tableNodesDistance : tableAndColNodesDistance;
        });

    const simulation = d3.forceSimulation(nodes)
        .force("link", forceLink)
        .force("charge", forceNode)
        .force("center", d3.forceCenter())
        .on("tick", ticked);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; max-height: 100%; height: auto; font: 12px sans-serif;");

    svg.append("defs").selectAll("marker")
        .data(linkTypes)
        .join("marker")
        .attr("id", d => `arrow_schema_graph_${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -0.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", linkColor)
        .attr("d", "M0,-5L10,0L0,5");

    svg.select("defs").append("marker")
        .attr("id", "arrow_schema_graph_grey")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -0.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", "#bfbfbf")
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
    //     .append("text")
    //     .attr("x", 15)
    //     .attr("y", 15)
    //     .text("Database Schema Graph")
    //     .attr("transform", `translate(${-width / 2}, ${-height / 2})`);

    // const link = svg.append("g")
    //     .attr("stroke-opacity", linkStrokeOpacity)
    //     .attr("stroke-width", typeof linkStrokeWidth !== "function" ? linkStrokeWidth : null)
    //     .attr("stroke-linecap", linkStrokeLinecap)
    //     .selectAll("line")
    //     .data(links)
    //     .join("line")
    //     .attr("stroke", d => linkColor(linkType(d)))
    //     .attr("marker-end", d => `url(${new URL(`#arrow_schema_graph_${d.type}`, location)})`);

    const link = svg.append("g")
        .attr("stroke-opacity", linkStrokeOpacity)
        .attr("stroke-width", typeof linkStrokeWidth !== "function" ? linkStrokeWidth : null)
        .attr("stroke-linecap", linkStrokeLinecap)
        .selectAll("path")
        .data(links)
        .join("path")
        .attr("id", d => `${d.source.id}-${d.target.id.split("_")[2]}`)
        .attr("type", d => linkType(d))
        .attr("stroke", d => linkColor(linkType(d)))
        .attr("fill", "none")
        .attr("marker-end", d => `url(${new URL(`#arrow_schema_graph_${d.link_type}`, location)})`);

    const node = svg.append("g")
        .attr("stroke-linecap", "round")
        .attr("stroke-linejoin", "round")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .attr("id", d => `${nodeId(d)}`)
        .attr("fill", d => nodeColor(nodeType(d)))
        .attr("type", d => nodeType(d))
        .call(schemaGraphDrag(simulation));

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

    function ticked() {
        // link
        //     .attr("x1", d => d.source.x)
        //     .attr("y1", d => d.source.y)
        //     .attr("x2", d => d.target.x)
        //     .attr("y2", d => d.target.y);
        link.attr("d", linkArc);

        node.attr("transform", d => `translate(${d.x},${d.y})`);
    }

    function linkArc(d) {
        const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
        return `
        M${d.source.x},${d.source.y}
        A${r},${r} 0 0,1 ${d.target.x},${d.target.y}`;
    }

    function schemaGraphDrag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    return svg.node();
}
