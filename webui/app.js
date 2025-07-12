class KnowledgeGraphViewer {
    constructor() {
        this.data = { entities: [], relations: [] };
        this.network = null;
        this.selectedNode = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadData();
    }

    setupEventListeners() {
        document.getElementById('loadData').addEventListener('click', () => this.loadData());
        document.getElementById('refreshGraph').addEventListener('click', () => this.renderGraph());
        document.getElementById('searchBtn').addEventListener('click', () => this.searchEntities());
        
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchEntities();
            }
        });
    }

    async loadData() {
        try {
            this.showLoading('Loading memory data...');
            
            // Simulated data loading from memory.json
            // In a real implementation, this would fetch from the actual file
            const response = await this.fetchMemoryData();
            this.data = this.parseMemoryData(response);
            
            this.updateStatistics();
            this.renderEntityList();
            this.renderGraph();
            
            this.showSuccess('Data loaded successfully!');
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load memory data');
        }
    }

    async fetchMemoryData() {
        try {
            const response = await fetch('/api/memory');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Failed to fetch from API, using fallback data:', error);
            // Fallback data if API is not available
            return [
                {"type": "entity", "name": "Python", "entityType": "programming_language", "observations": ["High-level programming language", "Popular for AI and data science", "Dynamic typing system", "Extensive library ecosystem", "Used in MCP server development", "Supports async/await pattern", "Great for JSON processing"]},
                {"type": "entity", "name": "FastAPI", "entityType": "web_framework", "observations": ["Modern Python web framework", "Built-in async support", "Automatic API documentation", "Type hints integration", "Production-ready framework"]},
                {"type": "entity", "name": "JSON-RPC", "entityType": "protocol", "observations": ["Remote procedure call protocol", "Uses JSON for encoding", "Version 2.0 specification", "Stateless communication"]},
                {"type": "relation", "from": "FastAPI", "to": "Python", "relationType": "built_with"},
                {"type": "relation", "from": "FastAPI", "to": "JSON-RPC", "relationType": "supports"}
            ];
        }
    }

    parseMemoryData(rawData) {
        const entities = [];
        const relations = [];

        rawData.forEach(item => {
            if (item.type === 'entity') {
                entities.push({
                    name: item.name,
                    entityType: item.entityType,
                    observations: item.observations || []
                });
            } else if (item.type === 'relation') {
                relations.push({
                    from: item.from,
                    to: item.to,
                    relationType: item.relationType
                });
            }
        });

        return { entities, relations };
    }

    updateStatistics() {
        const entityTypes = new Set(this.data.entities.map(e => e.entityType));
        
        document.getElementById('entityCount').textContent = this.data.entities.length;
        document.getElementById('relationCount').textContent = this.data.relations.length;
        document.getElementById('typeCount').textContent = entityTypes.size;
    }

    renderEntityList() {
        const entityList = document.getElementById('entityList');
        entityList.innerHTML = '';

        this.data.entities.forEach(entity => {
            const entityItem = document.createElement('div');
            entityItem.className = 'entity-item';
            entityItem.innerHTML = `
                <div class="entity-name">${entity.name}</div>
                <div class="entity-type">${entity.entityType.replace('_', ' ')}</div>
            `;
            
            entityItem.addEventListener('click', () => {
                this.selectEntity(entity);
                this.highlightEntityInList(entityItem);
            });
            
            entityList.appendChild(entityItem);
        });
    }

    highlightEntityInList(selectedItem) {
        document.querySelectorAll('.entity-item').forEach(item => {
            item.classList.remove('selected');
        });
        selectedItem.classList.add('selected');
    }

    selectEntity(entity) {
        this.selectedNode = entity;
        this.displayEntityDetails(entity);
        
        // Highlight node in graph
        if (this.network) {
            this.network.selectNodes([entity.name]);
        }
    }

    displayEntityDetails(entity) {
        const entityInfo = document.getElementById('entityInfo');
        
        const observationsList = entity.observations.map(obs => 
            `<li>${obs}</li>`
        ).join('');

        entityInfo.innerHTML = `
            <div class="entity-info-item">
                <strong>Name:</strong> ${entity.name}
            </div>
            <div class="entity-info-item">
                <strong>Type:</strong> ${entity.entityType.replace('_', ' ')}
            </div>
            <div class="entity-info-item">
                <strong>Observations:</strong>
                <ul class="observations-list">
                    ${observationsList}
                </ul>
            </div>
        `;
    }

    renderGraph() {
        const container = document.getElementById('knowledge-graph');
        
        // Prepare nodes
        const nodes = this.data.entities.map(entity => ({
            id: entity.name,
            label: entity.name,
            color: this.getNodeColor(entity.entityType),
            font: { size: 14, color: '#333' },
            borderWidth: 2,
            borderColor: '#333',
            shape: 'box',
            margin: 10
        }));

        // Prepare edges
        const edges = this.data.relations.map(relation => ({
            from: relation.from,
            to: relation.to,
            label: relation.relationType.replace('_', ' '),
            arrows: 'to',
            color: { color: '#666', highlight: '#333' },
            font: { size: 12, color: '#666' },
            smooth: { type: 'curvedCW', roundness: 0.2 }
        }));

        const data = { nodes, edges };
        
        const options = {
            layout: {
                improvedLayout: true,
                hierarchical: {
                    enabled: false
                }
            },
            physics: {
                enabled: true,
                stabilization: { iterations: 100 },
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 120,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            nodes: {
                shadow: true,
                borderWidth: 2,
                borderWidthSelected: 4
            },
            edges: {
                shadow: true,
                smooth: true
            },
            interaction: {
                hover: true,
                selectConnectedEdges: true
            }
        };

        this.network = new vis.Network(container, data, options);
        
        // Add event listeners
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const entity = this.data.entities.find(e => e.name === nodeId);
                if (entity) {
                    this.selectEntity(entity);
                    this.highlightEntityInList(
                        Array.from(document.querySelectorAll('.entity-item'))
                            .find(item => item.querySelector('.entity-name').textContent === entity.name)
                    );
                }
            }
        });

        this.network.on('hoverNode', (params) => {
            container.style.cursor = 'pointer';
        });

        this.network.on('blurNode', (params) => {
            container.style.cursor = 'default';
        });
    }

    getNodeColor(entityType) {
        const colors = {
            'programming_language': '#4CAF50',
            'web_framework': '#2196F3',
            'protocol': '#FF9800',
            'database': '#9C27B0',
            'tool': '#F44336',
            'concept': '#795548'
        };
        return colors[entityType] || '#607D8B';
    }

    searchEntities() {
        const query = document.getElementById('searchInput').value.toLowerCase().trim();
        if (!query) return;

        const matchingEntities = this.data.entities.filter(entity => 
            entity.name.toLowerCase().includes(query) ||
            entity.entityType.toLowerCase().includes(query) ||
            entity.observations.some(obs => obs.toLowerCase().includes(query))
        );

        if (matchingEntities.length > 0) {
            const firstMatch = matchingEntities[0];
            this.selectEntity(firstMatch);
            
            // Highlight in list
            const listItem = Array.from(document.querySelectorAll('.entity-item'))
                .find(item => item.querySelector('.entity-name').textContent === firstMatch.name);
            if (listItem) {
                this.highlightEntityInList(listItem);
                listItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            this.showSuccess(`Found ${matchingEntities.length} matching entities`);
        } else {
            this.showError('No entities found matching your search');
        }
    }

    showLoading(message) {
        const graphContainer = document.getElementById('knowledge-graph');
        graphContainer.innerHTML = `<div class="loading">${message}</div>`;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            background: ${type === 'success' ? '#4CAF50' : '#F44336'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new KnowledgeGraphViewer();
});
