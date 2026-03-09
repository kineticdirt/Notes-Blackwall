/**
 * Block definitions and utilities.
 */

// Block registry (populated from API)
const blockRegistry = {};

async function loadBlocks() {
    try {
        const response = await fetch('http://localhost:8000/api/blocks');
        const data = await response.json();
        
        data.blocks.forEach(block => {
            blockRegistry[block.type] = block;
        });
        
        return blockRegistry;
    } catch (error) {
        console.error('Failed to load blocks:', error);
        return {};
    }
}

function getBlockInfo(blockType) {
    return blockRegistry[blockType] || null;
}
