"""Graph visualization generator for wiki pages.

Generates an interactive HTML file showing how wiki pages connect via [[links]].
Uses D3.js for force-directed graph layout.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GraphData:
    """Nodes and edges for the wiki graph."""
    
    nodes: list[dict]
    edges: list[dict]
    
    def to_json(self) -> str:
        return json.dumps({"nodes": self.nodes, "edges": self.edges})


def extract_graph_data(wiki_dir: Path) -> GraphData:
    """Extract nodes and edges from wiki pages."""
    pages = list(wiki_dir.glob("**/*.md"))
    
    # Build node list
    nodes = []
    page_name_to_id = {}
    
    for i, page_path in enumerate(pages):
        name = page_path.stem
        page_name_to_id[name.lower()] = i
        
        # Get page size for node sizing
        content = page_path.read_text()
        size = len(content)
        
        # Determine node type based on path or content
        node_type = "page"
        if name.lower() == "index":
            node_type = "index"
        elif name.lower() == "log":
            node_type = "log"
        elif "/sources/" in str(page_path) or name.startswith("source"):
            node_type = "source"
        elif "/concepts/" in str(page_path):
            node_type = "concept"
        elif "/synthesis/" in str(page_path):
            node_type = "synthesis"
        
        nodes.append({
            "id": i,
            "name": name,
            "type": node_type,
            "size": min(max(size // 100, 5), 30),  # Scale size between 5-30
            "path": str(page_path.relative_to(wiki_dir)),
        })
    
    # Build edge list
    edges = []
    for page_path in pages:
        content = page_path.read_text()
        source_name = page_path.stem.lower()
        source_id = page_name_to_id.get(source_name)
        
        if source_id is None:
            continue
        
        # Find all [[wiki links]]
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        seen_targets = set()
        
        for link in links:
            target_name = link.lower()
            target_id = page_name_to_id.get(target_name)
            
            # Only add edge if target exists and we haven't added this edge yet
            if target_id is not None and target_id != source_id and target_id not in seen_targets:
                edges.append({
                    "source": source_id,
                    "target": target_id,
                })
                seen_targets.add(target_id)
    
    return GraphData(nodes=nodes, edges=edges)


def generate_graph_html(graph_data: GraphData, title: str = "Wiki Graph") -> str:
    """Generate a self-contained HTML file with interactive graph visualization."""
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            overflow: hidden;
        }}
        
        #header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            padding: 16px 24px;
            background: rgba(13, 17, 23, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #30363d;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        #header h1 {{
            font-size: 18px;
            font-weight: 600;
        }}
        
        #stats {{
            font-size: 14px;
            color: #8b949e;
        }}
        
        #graph {{
            width: 100vw;
            height: 100vh;
        }}
        
        .node {{
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        
        .node:hover {{
            opacity: 0.8;
        }}
        
        .node-label {{
            font-size: 11px;
            fill: #c9d1d9;
            pointer-events: none;
            text-anchor: middle;
            dominant-baseline: middle;
        }}
        
        .link {{
            stroke: #30363d;
            stroke-opacity: 0.6;
            fill: none;
        }}
        
        .link:hover {{
            stroke: #58a6ff;
            stroke-opacity: 1;
        }}
        
        #tooltip {{
            position: fixed;
            padding: 8px 12px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s;
            z-index: 200;
        }}
        
        #tooltip.visible {{
            opacity: 1;
        }}
        
        #legend {{
            position: fixed;
            bottom: 24px;
            left: 24px;
            padding: 16px;
            background: rgba(22, 27, 34, 0.9);
            border: 1px solid #30363d;
            border-radius: 8px;
            font-size: 12px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 6px;
        }}
        
        .legend-item:last-child {{
            margin-bottom: 0;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        #controls {{
            position: fixed;
            top: 80px;
            right: 24px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        button {{
            padding: 8px 16px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.15s;
        }}
        
        button:hover {{
            background: #30363d;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>📚 {title}</h1>
        <div id="stats"></div>
    </div>
    
    <div id="tooltip"></div>
    
    <div id="legend">
        <div class="legend-item"><div class="legend-dot" style="background: #58a6ff;"></div>Index</div>
        <div class="legend-item"><div class="legend-dot" style="background: #8b949e;"></div>Log</div>
        <div class="legend-item"><div class="legend-dot" style="background: #f778ba;"></div>Source</div>
        <div class="legend-item"><div class="legend-dot" style="background: #a371f7;"></div>Concept</div>
        <div class="legend-item"><div class="legend-dot" style="background: #3fb950;"></div>Synthesis</div>
        <div class="legend-item"><div class="legend-dot" style="background: #f0883e;"></div>Page</div>
    </div>
    
    <div id="controls">
        <button onclick="resetZoom()">Reset View</button>
        <button onclick="toggleLabels()">Toggle Labels</button>
    </div>
    
    <svg id="graph"></svg>
    
    <script>
        const data = {graph_data.to_json()};
        
        const colors = {{
            index: "#58a6ff",
            log: "#8b949e",
            source: "#f778ba",
            concept: "#a371f7",
            synthesis: "#3fb950",
            page: "#f0883e"
        }};
        
        // Update stats
        document.getElementById("stats").textContent = 
            `${{data.nodes.length}} pages · ${{data.edges.length}} connections`;
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform));
        
        svg.call(zoom);
        
        // Force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 10));
        
        // Draw links
        const links = g.append("g")
            .selectAll("line")
            .data(data.edges)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", 1.5);
        
        // Draw nodes
        const nodes = g.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => colors[d.type] || colors.page)
            .call(drag(simulation));
        
        // Draw labels
        let showLabels = true;
        const labels = g.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .attr("class", "node-label")
            .text(d => d.name)
            .attr("dy", d => d.size + 14);
        
        // Tooltip
        const tooltip = document.getElementById("tooltip");
        
        nodes.on("mouseover", (event, d) => {{
            tooltip.innerHTML = `<strong>${{d.name}}</strong><br>Type: ${{d.type}}<br>Path: ${{d.path}}`;
            tooltip.classList.add("visible");
        }}).on("mousemove", (event) => {{
            tooltip.style.left = (event.clientX + 10) + "px";
            tooltip.style.top = (event.clientY + 10) + "px";
        }}).on("mouseout", () => {{
            tooltip.classList.remove("visible");
        }});
        
        // Tick function
        simulation.on("tick", () => {{
            links
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            nodes
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        // Drag behavior
        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}
            
            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}
            
            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
        
        // Controls
        function resetZoom() {{
            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity.translate(width / 2, height / 2).scale(1).translate(-width / 2, -height / 2)
            );
        }}
        
        function toggleLabels() {{
            showLabels = !showLabels;
            labels.style("opacity", showLabels ? 1 : 0);
        }}
        
        // Handle resize
        window.addEventListener("resize", () => {{
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            svg.attr("width", newWidth).attr("height", newHeight);
            simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }});
    </script>
</body>
</html>'''
