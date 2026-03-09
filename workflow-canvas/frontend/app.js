/**
 * Main application entry point for Workflow Canvas.
 */

const API_BASE = 'http://localhost:8000';

// Global state
let currentWorkflow = {
    id: null,
    name: 'Untitled Workflow',
    blocks: [],
    connections: []
};

let selectedBlock = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    // Load blocks from API
    try {
        const response = await fetch(`${API_BASE}/api/blocks`);
        const data = await response.json();
        renderBlockPalette(data.blocks, data.categories);
        await loadBlockInfo(); // Load block info cache
    } catch (error) {
        console.error('Failed to load blocks:', error);
    }
    
    // Load MCP tools
    try {
        const mcpResponse = await fetch(`${API_BASE}/api/mcp/tools`);
        const mcpData = await mcpResponse.json();
        console.log('MCP tools loaded:', mcpData.tools.length);
    } catch (error) {
        console.error('Failed to load MCP tools:', error);
    }
    
    // Initialize canvas
    initializeCanvas();
}

function setupEventListeners() {
    // Toolbar buttons
    document.getElementById('btn-save').addEventListener('click', saveWorkflow);
    document.getElementById('btn-load').addEventListener('click', loadWorkflow);
    document.getElementById('btn-execute').addEventListener('click', executeWorkflow);
    document.getElementById('btn-clear').addEventListener('click', clearCanvas);
    document.getElementById('btn-close-execution').addEventListener('click', () => {
        document.getElementById('execution-panel').classList.add('hidden');
    });
    
    // Workflow name
    document.getElementById('workflow-name').addEventListener('change', (e) => {
        currentWorkflow.name = e.target.value;
    });
    
    // Chat interface
    setupChatInterface();
}

function setupChatInterface() {
    const chatInterface = document.getElementById('chat-interface');
    const chatToggle = document.getElementById('chat-toggle');
    const chatHeader = document.getElementById('chat-header');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');
    
    // Toggle chat
    chatToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        chatInterface.classList.toggle('chat-collapsed');
    });
    
    chatHeader.addEventListener('click', () => {
        if (chatInterface.classList.contains('chat-collapsed')) {
            chatInterface.classList.remove('chat-collapsed');
        }
    });
    
    // Send message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        addChatMessage(message, 'user');
        chatInput.value = '';
        
        // Process command
        processChatCommand(message);
    }
    
    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-focus input when chat opens
    chatHeader.addEventListener('click', () => {
        setTimeout(() => {
            if (!chatInterface.classList.contains('chat-collapsed')) {
                chatInput.focus();
            }
        }, 100);
    });
}

function addChatMessage(text, type = 'assistant') {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format text (simple markdown-like formatting)
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    contentDiv.innerHTML = formattedText;
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function processChatCommand(command) {
    const lowerCommand = command.toLowerCase();
    
    // Show typing indicator
    addChatMessage('Processing...', 'assistant');
    
    try {
        // Get workflow context
        const context = {
            nodes: nodeEditor ? nodeEditor.nodes.map(n => ({
                id: n.id,
                type: n.type,
                position: {x: n.x, y: n.y}
            })) : [],
            connections: nodeEditor ? nodeEditor.connections.map(c => ({
                from: c.fromNode,
                to: c.toNode
            })) : []
        };
        
        // Call AI Gateway
        const response = await fetch(`${API_BASE}/api/ai/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                command: command,
                context: context
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        const messages = document.getElementById('chat-messages');
        const lastMessage = messages.lastElementChild;
        if (lastMessage && lastMessage.textContent === 'Processing...') {
            lastMessage.remove();
        }
        
        // Process action
        if (data.action) {
            await executeAction(data.action, data.message);
        } else {
            addChatMessage(data.message || 'I processed your command.', 'assistant');
        }
    } catch (error) {
        console.error('AI Gateway error:', error);
        
        // Fallback to local processing
        const messages = document.getElementById('chat-messages');
        const lastMessage = messages.lastElementChild;
        if (lastMessage && lastMessage.textContent === 'Processing...') {
            lastMessage.remove();
        }
        
        // Local fallback processing
        processLocalCommand(command);
    }
}

async function executeAction(action, message) {
    if (!action) {
        addChatMessage(message, 'assistant');
        return;
    }
    
    switch (action.type) {
        case 'add_node':
            if (nodeEditor && action.block_type) {
                const x = action.position?.x || Math.random() * 400 + 100;
                const y = action.position?.y || Math.random() * 300 + 100;
                nodeEditor.addNode(action.block_type, x, y, {});
                addChatMessage(`✅ ${message || `Added ${action.block_type} node!`}`, 'assistant');
            }
            break;
            
        case 'clear_canvas':
            if (nodeEditor) {
                nodeEditor.nodes = [];
                nodeEditor.connections = [];
                nodeEditor.redraw();
                addChatMessage('✅ Canvas cleared!', 'assistant');
            }
            break;
            
        case 'list_nodes':
            const blocks = nodeEditor ? nodeEditor.nodes.map(n => n.type).join(', ') : 'none';
            addChatMessage(`📦 Current blocks: ${blocks || 'none'}`, 'assistant');
            break;
            
        case 'save_workflow':
            await saveWorkflow();
            addChatMessage('💾 Workflow saved!', 'assistant');
            break;
            
        case 'execute_workflow':
            await executeWorkflow();
            addChatMessage('🚀 Executing workflow...', 'assistant');
            break;
            
        default:
            addChatMessage(message || 'Action processed.', 'assistant');
    }
}

function processLocalCommand(command) {
    const lowerCommand = command.toLowerCase();
    let response = '';
    
    // Local fallback command processing
    if (lowerCommand.includes('add') && lowerCommand.includes('node')) {
        const blockTypes = {
            'http': 'input_http', 'http request': 'input_http',
            'mcp': 'mcp_tool', 'mcp tool': 'mcp_tool',
            'rag': 'rag_ingest', 'rag ingest': 'rag_ingest',
            'prompt': 'prompt_llm', 'llm': 'prompt_llm',
            'data': 'resource_data', 'resource': 'resource_data'
        };
        
        let blockType = null;
        for (const [key, type] of Object.entries(blockTypes)) {
            if (lowerCommand.includes(key)) {
                blockType = type;
                break;
            }
        }
        
        if (blockType && nodeEditor) {
            const x = Math.random() * 400 + 100;
            const y = Math.random() * 300 + 100;
            nodeEditor.addNode(blockType, x, y, {});
            response = `✅ Added ${blockType} node!`;
        } else {
            response = `❌ Couldn't determine block type. Try: "add HTTP request node"`;
        }
    } else if (lowerCommand.includes('clear') || lowerCommand.includes('reset')) {
        if (nodeEditor) {
            nodeEditor.nodes = [];
            nodeEditor.connections = [];
            nodeEditor.redraw();
            response = '✅ Canvas cleared!';
        }
    } else if (lowerCommand.includes('show') && lowerCommand.includes('block')) {
        const blocks = nodeEditor ? nodeEditor.nodes.map(n => n.type).join(', ') : 'none';
        response = `📦 Current blocks: ${blocks || 'none'}`;
        } else if (lowerCommand.includes('export') && lowerCommand.includes('n8n')) {
            if (currentWorkflow.id) {
                try {
                    const response = await fetch(`${API_BASE}/api/workflows/${currentWorkflow.id}/export/n8n`);
                    const n8nData = await response.json();
                    const blob = new Blob([JSON.stringify(n8nData, null, 2)], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${currentWorkflow.name || 'workflow'}.json`;
                    a.click();
                    response = '✅ Workflow exported to N8N format!';
                } catch (error) {
                    response = `❌ Export failed: ${error.message}`;
                }
            } else {
                response = '💾 Please save the workflow first before exporting.';
            }
        } else if (lowerCommand.includes('import') && lowerCommand.includes('n8n')) {
            response = '💡 To import N8N workflow, use the API endpoint: POST /api/workflows/import/n8n with N8N JSON';
        } else if (lowerCommand.includes('help')) {
            response = `📋 Available commands:
• "Add [block type] node" - Add a node
• "Clear canvas" - Remove all nodes
• "Show blocks" - List all blocks
• "Save workflow" - Save workflow
• "Execute workflow" - Run workflow
• "Export to N8N" - Export in N8N format
• "Import N8N" - Import N8N workflow`;
        } else {
            response = `🤔 I didn't understand. Try "help" for commands.`;
        }
    
    addChatMessage(response, 'assistant');
}

function renderBlockPalette(blocks, categories) {
    const container = document.getElementById('block-categories');
    container.innerHTML = '';
    
    // Group blocks by category
    const blocksByCategory = {};
    categories.forEach(cat => {
        blocksByCategory[cat] = blocks.filter(b => b.category === cat);
    });
    
    // Category display names and icons
    const categoryInfo = {
        'tools': { name: 'Tools', icon: '🔧', description: 'MCP tools and utilities' },
        'prompts': { name: 'Prompts', icon: '💬', description: 'LLM prompts and templates' },
        'resources': { name: 'Resources', icon: '📦', description: 'Data sources and RAG' },
        'transform': { name: 'Transform', icon: '🔄', description: 'Data transformation' },
        'control': { name: 'Control', icon: '🔀', description: 'Flow control' },
        'restrictions': { name: 'Restrictions', icon: '🚫', description: 'Access control and restrictions' },
        'output': { name: 'Output', icon: '📤', description: 'Output destinations' }
    };
    
    // Render each category
    categories.forEach(category => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'category';
        
        const title = document.createElement('div');
        title.className = 'category-title';
        const info = categoryInfo[category] || { name: category, icon: '▢' };
        title.innerHTML = `<span>${info.icon}</span> ${info.name}`;
        if (info.description) {
            title.title = info.description;
        }
        categoryDiv.appendChild(title);
        
        const blocksList = blocksByCategory[category];
        if (blocksList.length === 0) {
            const emptyMsg = document.createElement('div');
            emptyMsg.className = 'category-empty';
            emptyMsg.textContent = 'No blocks in this category';
            emptyMsg.style.cssText = 'font-size: 11px; color: #666; padding: 5px; font-style: italic;';
            categoryDiv.appendChild(emptyMsg);
        } else {
            blocksList.forEach(block => {
                const blockItem = document.createElement('div');
                blockItem.className = 'block-item';
                blockItem.draggable = true;
                blockItem.dataset.blockType = block.type;
                
                blockItem.innerHTML = `
                    <span class="block-icon">${block.icon || '▢'}</span>
                    <span class="block-name">${block.name}</span>
                `;
                
                // Make draggable
                blockItem.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('blockType', block.type);
                    e.dataTransfer.setData('blockData', JSON.stringify(block));
                });
                
                categoryDiv.appendChild(blockItem);
            });
        }
        
        container.appendChild(categoryDiv);
    });
}

function initializeCanvas() {
    // Wait for canvas to be ready
    const canvas = document.getElementById('workflow-canvas');
    if (!canvas) {
        console.error('Canvas not found!');
        return;
    }
    
    // Initialize enhanced node editor
    nodeEditor = new NodeEditor('workflow-canvas');
    
    // Make canvas droppable
    canvas.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    });
    
    canvas.addEventListener('drop', (e) => {
        e.preventDefault();
        const blockType = e.dataTransfer.getData('blockType');
        let blockData = {};
        try {
            blockData = JSON.parse(e.dataTransfer.getData('blockData') || '{}');
        } catch (err) {
            console.warn('Failed to parse block data:', err);
        }
        
        if (blockType) {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - nodeEditor.panX) / nodeEditor.scale;
            const y = (e.clientY - rect.top - nodeEditor.panY) / nodeEditor.scale;
            
            nodeEditor.addNode(blockType, x, y, blockData);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.key === 'Delete' || e.key === 'Backspace') && nodeEditor && nodeEditor.selectedNode) {
            nodeEditor.deleteNode(nodeEditor.selectedNode.id);
        }
    });
    
    // Initial redraw
    setTimeout(() => {
        if (nodeEditor) {
            nodeEditor.redraw();
        }
    }, 200);
}

function addBlockToCanvas(blockType, blockData, x, y) {
    if (nodeEditor) {
        const node = nodeEditor.addNode(blockType, x, y, blockData);
        currentWorkflow.blocks.push({
            id: node.id,
            type: blockType,
            position: { x: node.x, y: node.y },
            data: node.data,
            connections: []
        });
    }
}

function redrawCanvas() {
    if (nodeEditor) {
        nodeEditor.redraw();
    }
}

function drawGrid(ctx, width, height) {
    ctx.strokeStyle = '#2d2d30';
    ctx.lineWidth = 1;
    
    const gridSize = 20;
    
    for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
    
    for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
}

function drawBlock(ctx, block, isSelected) {
    const blockInfo = getBlockInfo(block.type);
    const color = blockInfo?.color || '#3e3e42';
    
    const x = block.position.x;
    const y = block.position.y;
    const width = 180;
    const height = 80;
    
    // Draw block background
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
    
    // Draw border
    ctx.strokeStyle = isSelected ? '#007acc' : '#555555';
    ctx.lineWidth = isSelected ? 3 : 2;
    ctx.strokeRect(x, y, width, height);
    
    // Draw block content
    ctx.fillStyle = '#ffffff';
    ctx.font = '13px sans-serif';
    ctx.fillText(blockInfo?.name || block.type, x + 10, y + 25);
    
    ctx.fillStyle = '#cccccc';
    ctx.font = '11px sans-serif';
    ctx.fillText(block.type, x + 10, y + 45);
}

function drawConnections(ctx) {
    // Draw connections between blocks
    currentWorkflow.blocks.forEach(block => {
        block.connections.forEach(conn => {
            const fromBlock = currentWorkflow.blocks.find(b => b.id === conn.from);
            const toBlock = currentWorkflow.blocks.find(b => b.id === conn.to);
            
            if (fromBlock && toBlock) {
                drawConnection(ctx, fromBlock, toBlock);
            }
        });
    });
}

function drawConnection(ctx, fromBlock, toBlock) {
    const fromX = fromBlock.position.x + 180;
    const fromY = fromBlock.position.y + 40;
    const toX = toBlock.position.x;
    const toY = toBlock.position.y + 40;
    
    ctx.strokeStyle = '#007acc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();
}

// Block info cache
const blockInfoCache = {};

async function loadBlockInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/blocks`);
        const data = await response.json();
        data.blocks.forEach(block => {
            blockInfoCache[block.type] = block;
        });
    } catch (error) {
        console.error('Failed to load block info:', error);
    }
}

function getBlockInfo(blockType) {
    if (blockInfoCache[blockType]) {
        return blockInfoCache[blockType];
    }
    // Fallback
    return {
        name: blockType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        color: '#3e3e42',
        icon: '▢'
    };
}

function updatePropertiesPanel() {
    const panel = document.getElementById('properties-content');
    
    if (!selectedBlock) {
        panel.innerHTML = '<p>Select a block to edit properties</p>';
        return;
    }
    
    const blockInfo = getBlockInfo(selectedBlock.type);
    panel.innerHTML = `
        <div class="property-group">
            <label class="property-label">Block Type</label>
            <input type="text" class="property-input" value="${selectedBlock.type}" disabled>
        </div>
        <div class="property-group">
            <label class="property-label">Block ID</label>
            <input type="text" class="property-input" value="${selectedBlock.id}" disabled>
        </div>
        <div class="property-group">
            <label class="property-label">Position X</label>
            <input type="number" class="property-input" value="${selectedBlock.position.x}" 
                   onchange="updateBlockProperty('position.x', this.value)">
        </div>
        <div class="property-group">
            <label class="property-label">Position Y</label>
            <input type="number" class="property-input" value="${selectedBlock.position.y}" 
                   onchange="updateBlockProperty('position.y', this.value)">
        </div>
    `;
}

function updateBlockProperty(property, value) {
    if (!selectedBlock) return;
    
    const parts = property.split('.');
    if (parts.length === 2) {
        selectedBlock[parts[0]][parts[1]] = parseFloat(value);
    } else {
        selectedBlock[property] = value;
    }
    
    redrawCanvas();
}

async function saveWorkflow() {
    try {
        // Get workflow data from node editor
        const workflowData = nodeEditor ? nodeEditor.getWorkflowData() : {nodes: [], connections: []};
        
        const workflowPayload = {
            name: currentWorkflow.name,
            description: '',
            blocks: workflowData.nodes.map(node => ({
                id: node.id,
                type: node.type,
                position: node.position,
                data: node.data,
                connections: workflowData.connections
                    .filter(c => c.from === node.id || c.to === node.id)
                    .map(c => ({
                        from: c.from,
                        to: c.to,
                        fromPort: c.fromPort,
                        toPort: c.toPort
                    }))
            }))
        };
        
        const url = currentWorkflow.id 
            ? `${API_BASE}/api/workflows/${currentWorkflow.id}`
            : `${API_BASE}/api/workflows`;
        
        const method = currentWorkflow.id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(workflowPayload)
        });
        
        const data = await response.json();
        currentWorkflow.id = data.id;
        
        alert('Workflow saved!');
    } catch (error) {
        console.error('Failed to save workflow:', error);
        alert('Failed to save workflow');
    }
}

async function loadWorkflow() {
    // Simplified - would show a dialog to select workflow
    alert('Load workflow feature - to be implemented');
}

async function executeWorkflow() {
    if (currentWorkflow.blocks.length === 0) {
        alert('No blocks to execute');
        return;
    }
    
    // Show execution panel
    document.getElementById('execution-panel').classList.remove('hidden');
    const log = document.getElementById('execution-log');
    log.innerHTML = '';
    
    addLogEntry('Starting workflow execution...', 'info');
    
    try {
        // Use streaming execution
        await streamWorkflowExecution();
    } catch (error) {
        addLogEntry(`Error: ${error.message}`, 'error');
    }
}

async function streamWorkflowExecution() {
    if (!currentWorkflow.id) {
        // Save workflow first
        await saveWorkflow();
    }
    
    const log = document.getElementById('execution-log');
    const eventSource = new EventSource(
        `${API_BASE}/api/workflows/${currentWorkflow.id}/stream`
    );
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'workflow_start') {
            addLogEntry(`Workflow started: ${data.workflow_id}`, 'info');
        } else if (data.type === 'block_complete') {
            addLogEntry(`Block ${data.block_id} completed`, 'success');
        } else if (data.type === 'block_error') {
            addLogEntry(`Block ${data.block_id} error: ${data.error}`, 'error');
        } else if (data.type === 'workflow_complete') {
            addLogEntry('Workflow execution completed!', 'success');
            eventSource.close();
        } else if (data.type === 'error') {
            addLogEntry(`Error: ${data.error}`, 'error');
            eventSource.close();
        }
    };
    
    eventSource.onerror = () => {
        addLogEntry('Stream connection error', 'error');
        eventSource.close();
    };
}

function addLogEntry(message, type = 'info') {
    const log = document.getElementById('execution-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.innerHTML = `
        <span class="log-timestamp">${timestamp}</span>
        <span class="log-message">${message}</span>
    `;
    
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function clearCanvas() {
    if (confirm('Clear all blocks?')) {
        currentWorkflow.blocks = [];
        selectedBlock = null;
        redrawCanvas();
        updatePropertiesPanel();
    }
}

// Make functions available globally
window.updateBlockProperty = updateBlockProperty;
