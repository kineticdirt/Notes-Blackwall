/**
 * Enhanced node-based editor with connection ports.
 * Similar to the image style with proper node connections.
 */

class NodeEditor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.connections = [];
        this.selectedNode = null;
        this.dragging = false;
        this.connecting = false;
        this.connectionStart = null;
        this.scale = 1.0;
        this.panX = 0;
        this.panY = 0;
        
        this.setupCanvas();
        this.setupEventListeners();
    }
    
    setupCanvas() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        // Initial redraw after a short delay to ensure canvas is ready
        setTimeout(() => {
            this.redraw();
        }, 100);
    }
    
    resizeCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.redraw();
    }
    
    setupEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
        
        // Prevent context menu
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    addNode(nodeType, x, y, blockData) {
        const node = {
            id: `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: nodeType,
            x: x,
            y: y,
            width: 200,
            height: 120,
            data: blockData || {},
            inputs: this.getInputPorts(nodeType),
            outputs: this.getOutputPorts(nodeType),
            selected: false
        };
        
        this.nodes.push(node);
        this.redraw();
        return node;
    }
    
    getInputPorts(nodeType) {
        // Define input ports based on block type
        const ports = {
            // Tools
            'input_http': [],
            'output_http': [{name: 'data', x: 0, y: 0}],
            'mcp_tool': [{name: 'tool_id', x: 0, y: 0}, {name: 'parameters', x: 0, y: 0}],
            'mcp_chain': [{name: 'tools', x: 0, y: 0}],
            // Prompts
            'prompt_llm': [{name: 'prompt', x: 0, y: 0}, {name: 'context', x: 0, y: 0}],
            'prompt_template': [{name: 'template', x: 0, y: 0}, {name: 'variables', x: 0, y: 0}],
            'prompt_chain': [{name: 'prompts', x: 0, y: 0}],
            // Resources
            'resource_data': [],
            'resource_file': [{name: 'path', x: 0, y: 0}],
            'resource_database': [{name: 'query', x: 0, y: 0}],
            'rag_ingest': [{name: 'document', x: 0, y: 0}, {name: 'metadata', x: 0, y: 0}],
            'rag_search': [{name: 'query', x: 0, y: 0}],
            'rag_subgraph': [{name: 'node_id', x: 0, y: 0}, {name: 'depth', x: 0, y: 0}],
            // Transform
            'transform_json': [{name: 'data', x: 0, y: 0}],
            'transform_text': [{name: 'text', x: 0, y: 0}],
            // Control
            'control_if': [{name: 'condition', x: 0, y: 0}],
            'control_loop': [{name: 'items', x: 0, y: 0}],
            // Restrictions
            'restriction_rate_limit': [{name: 'requests', x: 0, y: 0}, {name: 'window', x: 0, y: 0}],
            'restriction_access_control': [{name: 'user', x: 0, y: 0}, {name: 'resource', x: 0, y: 0}, {name: 'permission', x: 0, y: 0}],
            'restriction_validation': [{name: 'data', x: 0, y: 0}, {name: 'rules', x: 0, y: 0}],
            'restriction_quota': [{name: 'resource', x: 0, y: 0}, {name: 'amount', x: 0, y: 0}],
            'restriction_time_window': [{name: 'start_time', x: 0, y: 0}, {name: 'end_time', x: 0, y: 0}],
            'restriction_condition': [{name: 'condition', x: 0, y: 0}, {name: 'action', x: 0, y: 0}],
            // Output
            'output_console': [{name: 'data', x: 0, y: 0}]
        };
        
        return ports[nodeType] || [];
    }
    
    getOutputPorts(nodeType) {
        // Define output ports based on block type
        const ports = {
            // Tools
            'input_http': [{name: 'response', x: 0, y: 0}],
            'output_http': [],
            'mcp_tool': [{name: 'result', x: 0, y: 0}],
            'mcp_chain': [{name: 'results', x: 0, y: 0}],
            // Prompts
            'prompt_llm': [{name: 'response', x: 0, y: 0}],
            'prompt_template': [{name: 'prompt', x: 0, y: 0}],
            'prompt_chain': [{name: 'responses', x: 0, y: 0}],
            // Resources
            'resource_data': [{name: 'data', x: 0, y: 0}],
            'resource_file': [{name: 'content', x: 0, y: 0}],
            'resource_database': [{name: 'results', x: 0, y: 0}],
            'rag_ingest': [{name: 'node_id', x: 0, y: 0}],
            'rag_search': [{name: 'results', x: 0, y: 0}],
            'rag_subgraph': [{name: 'subgraph', x: 0, y: 0}],
            // Transform
            'transform_json': [{name: 'result', x: 0, y: 0}],
            'transform_text': [{name: 'result', x: 0, y: 0}],
            // Control
            'control_if': [{name: 'result', x: 0, y: 0}],
            'control_loop': [{name: 'result', x: 0, y: 0}],
            // Restrictions
            'restriction_rate_limit': [{name: 'allowed', x: 0, y: 0}, {name: 'remaining', x: 0, y: 0}],
            'restriction_access_control': [{name: 'allowed', x: 0, y: 0}, {name: 'reason', x: 0, y: 0}],
            'restriction_validation': [{name: 'valid', x: 0, y: 0}, {name: 'errors', x: 0, y: 0}],
            'restriction_quota': [{name: 'within_quota', x: 0, y: 0}, {name: 'remaining', x: 0, y: 0}],
            'restriction_time_window': [{name: 'allowed', x: 0, y: 0}, {name: 'current_time', x: 0, y: 0}],
            'restriction_condition': [{name: 'restricted', x: 0, y: 0}, {name: 'message', x: 0, y: 0}],
            // Output
            'output_console': []
        };
        
        return ports[nodeType] || [];
    }
    
    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.panX) / this.scale;
        const y = (e.clientY - rect.top - this.panY) / this.scale;
        
        // Check if clicking on a port
        const port = this.getPortAt(x, y);
        if (port) {
            this.connecting = true;
            this.connectionStart = {node: port.node, port: port.port};
            return;
        }
        
        // Check if clicking on a node
        const node = this.getNodeAt(x, y);
        if (node) {
            this.selectedNode = node;
            node.selected = true;
            this.dragging = true;
            this.dragOffset = {x: x - node.x, y: y - node.y};
            this.redraw();
            this.onNodeSelected(node);
            return;
        }
        
        // Deselect
        this.selectedNode = null;
        this.nodes.forEach(n => n.selected = false);
        this.redraw();
    }
    
    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.panX) / this.scale;
        const y = (e.clientY - rect.top - this.panY) / this.scale;
        
        if (this.connecting && this.connectionStart) {
            this.connectionPreview = {x, y};
            this.redraw();
        } else if (this.dragging && this.selectedNode) {
            this.selectedNode.x = x - this.dragOffset.x;
            this.selectedNode.y = y - this.dragOffset.y;
            this.updatePortPositions(this.selectedNode);
            this.redraw();
        }
    }
    
    onMouseUp(e) {
        if (this.connecting && this.connectionStart) {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.panX) / this.scale;
            const y = (e.clientY - rect.top - this.panY) / this.scale;
            
            const port = this.getPortAt(x, y);
            if (port && port.node !== this.connectionStart.node) {
                // Create connection
                this.addConnection(
                    this.connectionStart.node.id,
                    this.connectionStart.port.name,
                    port.node.id,
                    port.port.name
                );
            }
            
            this.connecting = false;
            this.connectionStart = null;
            this.connectionPreview = null;
            this.redraw();
        }
        
        this.dragging = false;
    }
    
    onWheel(e) {
        e.preventDefault();
        const delta = e.deltaY * -0.001;
        this.scale = Math.min(Math.max(0.5, this.scale + delta), 2.0);
        this.redraw();
    }
    
    getNodeAt(x, y) {
        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const node = this.nodes[i];
            if (x >= node.x && x <= node.x + node.width &&
                y >= node.y && y <= node.y + node.height) {
                return node;
            }
        }
        return null;
    }
    
    getPortAt(x, y) {
        for (const node of this.nodes) {
            // Check input ports
            for (const port of node.inputs) {
                const portX = node.x + port.x;
                const portY = node.y + port.y;
                const distance = Math.sqrt(
                    Math.pow(x - portX, 2) + Math.pow(y - portY, 2)
                );
                if (distance < 8) {
                    return {node, port, type: 'input'};
                }
            }
            
            // Check output ports
            for (const port of node.outputs) {
                const portX = node.x + port.x;
                const portY = node.y + port.y;
                const distance = Math.sqrt(
                    Math.pow(x - portX, 2) + Math.pow(y - portY, 2)
                );
                if (distance < 8) {
                    return {node, port, type: 'output'};
                }
            }
        }
        return null;
    }
    
    updatePortPositions(node) {
        const portSpacing = 30;
        const startY = 40;
        
        // Update input ports
        node.inputs.forEach((port, i) => {
            port.x = 0;
            port.y = startY + (i * portSpacing);
        });
        
        // Update output ports
        node.outputs.forEach((port, i) => {
            port.x = node.width;
            port.y = startY + (i * portSpacing);
        });
    }
    
    addConnection(fromNodeId, fromPort, toNodeId, toPort) {
        // Check if connection already exists
        const exists = this.connections.some(conn =>
            conn.fromNode === fromNodeId && conn.fromPort === fromPort &&
            conn.toNode === toNodeId && conn.toPort === toPort
        );
        
        if (!exists) {
            this.connections.push({
                id: `conn_${Date.now()}`,
                fromNode: fromNodeId,
                fromPort: fromPort,
                toNode: toNodeId,
                toPort: toPort
            });
            this.redraw();
        }
    }
    
    drawNode(node) {
        const blockInfo = getBlockInfo(node.type);
        const color = blockInfo?.color || '#3e3e42';
        
        // Draw node background
        this.ctx.fillStyle = color;
        this.ctx.fillRect(node.x, node.y, node.width, node.height);
        
        // Draw border
        this.ctx.strokeStyle = node.selected ? '#007acc' : '#555555';
        this.ctx.lineWidth = node.selected ? 3 : 2;
        this.ctx.strokeRect(node.x, node.y, node.width, node.height);
        
        // Draw title
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = 'bold 13px sans-serif';
        this.ctx.fillText(blockInfo?.name || node.type, node.x + 10, node.y + 25);
        
        // Draw type
        this.ctx.fillStyle = '#cccccc';
        this.ctx.font = '11px sans-serif';
        this.ctx.fillText(node.type, node.x + 10, node.y + 45);
        
        // Draw ports
        this.updatePortPositions(node);
        
        // Input ports (left side)
        node.inputs.forEach(port => {
            const portX = node.x + port.x;
            const portY = node.y + port.y;
            
            // Port circle
            this.ctx.fillStyle = '#007acc';
            this.ctx.beginPath();
            this.ctx.arc(portX, portY, 6, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Port label
            this.ctx.fillStyle = '#cccccc';
            this.ctx.font = '10px sans-serif';
            this.ctx.fillText(port.name, portX + 10, portY + 4);
        });
        
        // Output ports (right side)
        node.outputs.forEach(port => {
            const portX = node.x + port.x;
            const portY = node.y + port.y;
            
            // Port circle
            this.ctx.fillStyle = '#4caf50';
            this.ctx.beginPath();
            this.ctx.arc(portX, portY, 6, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Port label
            this.ctx.fillStyle = '#cccccc';
            this.ctx.font = '10px sans-serif';
            this.ctx.textAlign = 'right';
            this.ctx.fillText(port.name, portX - 10, portY + 4);
            this.ctx.textAlign = 'left';
        });
    }
    
    drawConnection(conn) {
        const fromNode = this.nodes.find(n => n.id === conn.fromNode);
        const toNode = this.nodes.find(n => n.id === conn.toNode);
        
        if (!fromNode || !toNode) return;
        
        const fromPort = fromNode.outputs.find(p => p.name === conn.fromPort);
        const toPort = toNode.inputs.find(p => p.name === conn.toPort);
        
        if (!fromPort || !toPort) return;
        
        const fromX = fromNode.x + fromPort.x;
        const fromY = fromNode.y + fromPort.y;
        const toX = toNode.x + toPort.x;
        const toY = toNode.y + toPort.y;
        
        // Draw connection line with bezier curve
        this.ctx.strokeStyle = '#007acc';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(fromX, fromY);
        
        const cp1x = fromX + 50;
        const cp1y = fromY;
        const cp2x = toX - 50;
        const cp2y = toY;
        
        this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, toX, toY);
        this.ctx.stroke();
        
        // Draw arrowhead
        const angle = Math.atan2(toY - fromY, toX - fromX);
        const arrowLength = 10;
        const arrowWidth = 5;
        
        this.ctx.fillStyle = '#007acc';
        this.ctx.beginPath();
        this.ctx.moveTo(toX, toY);
        this.ctx.lineTo(
            toX - arrowLength * Math.cos(angle - Math.PI / 6),
            toY - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.lineTo(
            toX - arrowLength * Math.cos(angle + Math.PI / 6),
            toY - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.closePath();
        this.ctx.fill();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#2d2d30';
        this.ctx.lineWidth = 1;
        
        const gridSize = 20;
        const startX = Math.floor((-this.panX % gridSize));
        const startY = Math.floor((-this.panY % gridSize));
        const width = this.canvas.width / this.scale;
        const height = this.canvas.height / this.scale;
        
        for (let x = startX; x < width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, height);
            this.ctx.stroke();
        }
        
        for (let y = startY; y < height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(width, y);
            this.ctx.stroke();
        }
    }
    
    redraw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply transform
        this.ctx.save();
        this.ctx.scale(this.scale, this.scale);
        this.ctx.translate(this.panX, this.panY);
        
        // Draw grid
        this.drawGrid();
        
        // Draw connections
        this.connections.forEach(conn => this.drawConnection(conn));
        
        // Draw connection preview
        if (this.connectionPreview && this.connectionStart) {
            const fromNode = this.connectionStart.node;
            const fromPort = this.connectionStart.port;
            const fromX = fromNode.x + fromPort.x;
            const fromY = fromNode.y + fromPort.y;
            
            this.ctx.strokeStyle = '#4caf50';
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            this.ctx.beginPath();
            this.ctx.moveTo(fromX, fromY);
            this.ctx.lineTo(this.connectionPreview.x, this.connectionPreview.y);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }
        
        // Draw nodes
        this.nodes.forEach(node => this.drawNode(node));
        
        this.ctx.restore();
    }
    
    onNodeSelected(node) {
        // Update properties panel
        updatePropertiesPanel(node);
    }
    
    deleteNode(nodeId) {
        this.nodes = this.nodes.filter(n => n.id !== nodeId);
        this.connections = this.connections.filter(
            c => c.fromNode !== nodeId && c.toNode !== nodeId
        );
        if (this.selectedNode?.id === nodeId) {
            this.selectedNode = null;
        }
        this.redraw();
    }
    
    getWorkflowData() {
        return {
            nodes: this.nodes.map(node => ({
                id: node.id,
                type: node.type,
                position: {x: node.x, y: node.y},
                data: node.data
            })),
            connections: this.connections.map(conn => ({
                from: conn.fromNode,
                fromPort: conn.fromPort,
                to: conn.toNode,
                toPort: conn.toPort
            }))
        };
    }
}

// Global node editor instance
let nodeEditor = null;

function getBlockInfo(blockType) {
    // Use global block info cache
    if (typeof blockInfoCache !== 'undefined' && blockInfoCache[blockType]) {
        return blockInfoCache[blockType];
    }
    // Fallback
    return {
        name: blockType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        color: '#3e3e42',
        icon: '▢'
    };
}

function updatePropertiesPanel(node) {
    const panel = document.getElementById('properties-content');
    if (!node) {
        panel.innerHTML = '<p>Select a node to edit properties</p>';
        return;
    }
    
    panel.innerHTML = `
        <div class="property-group">
            <label class="property-label">Node Type</label>
            <input type="text" class="property-input" value="${node.type}" disabled>
        </div>
        <div class="property-group">
            <label class="property-label">Node ID</label>
            <input type="text" class="property-input" value="${node.id}" disabled>
        </div>
        <div class="property-group">
            <label class="property-label">Position X</label>
            <input type="number" class="property-input" value="${node.x}" 
                   onchange="nodeEditor.nodes.find(n => n.id === '${node.id}').x = parseFloat(this.value); nodeEditor.redraw();">
        </div>
        <div class="property-group">
            <label class="property-label">Position Y</label>
            <input type="number" class="property-input" value="${node.y}" 
                   onchange="nodeEditor.nodes.find(n => n.id === '${node.id}').y = parseFloat(this.value); nodeEditor.redraw();">
        </div>
    `;
}
