// Main application JavaScript
let config = {};
let nodes = [];
let members = [];

// Get path prefix from meta tag or default
function getPathPrefix() {
    const metaTag = document.querySelector('meta[name="path-prefix"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// Load configuration and data
async function loadData() {
    const pathPrefix = getPathPrefix();
    try {
        const response = await fetch(`${pathPrefix}/api/data`);
        const data = await response.json();

        config = data.config;
        nodes = data.nodes; // Already filtered by server
        members = data.members; // Already filtered by server

        return { config, nodes, members };
    } catch (error) {
        console.error('Error loading data:', error);
        return { config: {}, nodes: [], members: [] };
    }
}

// Home page data (no longer needed for statistics, kept for potential future use)
function homeData() {
    return {
        async init() {
            // Home page no longer needs to load data for statistics
            // Statistics are now rendered server-side
        }
    }
}

// Simple navigation utilities
const Router = {
    // Navigate to node route
    navigateToNode(area, nodeId) {
        const url = `/nodes/${area}/${nodeId}`;
        window.location.href = url;
    }
};

    // Multiselect component
    function multiselect(propertyName, optionsOrFunction) {
        return {
            open: false,
            selectedValues: [],
            options: [],

            init() {
                // Wait for parent to be fully initialized
                this.$nextTick(() => {
                    this.waitForParent();
                });
            },

            waitForParent() {
                // Check if parent is available and has the required properties
                if (!this.$parent || !this.$parent.nodes) {
                    // Wait a bit longer and try again
                    setTimeout(() => this.waitForParent(), 200);
                    return;
                }

                // Parent is ready, initialize the multiselect
                this.initializeMultiselect();
            },

            initializeMultiselect() {
                // Initialize with empty array for multiselect
                if (!this.$parent[propertyName]) {
                    this.$parent[propertyName] = [];
                }

                this.updateOptions();

                // Set default state to all options selected
                this.selectedValues = [...this.options];

                // Watch for changes in the parent's nodes data
                this.$watch('$parent.nodes', () => {
                    this.updateOptions();
                });

                // Store a reference to the parent for later use
                this.parentComponent = this.$parent;
            },
        
        updateOptions() {
            // Handle both array and function parameters
            if (typeof optionsOrFunction === 'function') {
                try {
                    const result = optionsOrFunction.call(this.$parent);
                    this.options = result || [];
                } catch (error) {
                    console.warn('Error getting options:', error);
                    this.options = [];
                }
            } else {
                this.options = optionsOrFunction || [];
            }
        },
        
        toggle() {
            this.updateOptions(); // Refresh options when opening
            this.open = !this.open;
        },
        
        getDisplayText() {
            if (this.selectedValues.length === 0) {
                return 'All';
            } else if (this.selectedValues.length === 1) {
                return this.selectedValues[0];
            } else {
                return `${this.selectedValues.length} selected`;
            }
        },
        
                    updateSelection() {
                // Try to get parent from stored reference or current context
                let parent = this.parentComponent || this.$parent;
                
                // If still no parent, try to find it by looking up the DOM tree
                if (!parent) {
                    let element = this.$el;
                    while (element && !parent) {
                        if (element._x_dataStack && element._x_dataStack.length > 0) {
                            const data = element._x_dataStack[0];
                            if (data.nodes && data.applyFilters) {
                                parent = data;
                                break;
                            }
                        }
                        element = element.parentElement;
                    }
                }
                
                if (!parent) {
                    return;
                }

                // Update the parent component's property
                parent[propertyName] = [...this.selectedValues];
                
                // Trigger filter update
                parent.applyFilters();
            },
        
                    clearAll() {
                this.selectedValues = [];
                this.updateSelection();
            }
    }
}

// Nodes page data
function nodesData() {
    return {
        nodes: [],
        members: [],
        filteredNodes: [],
        currentNode: null,
        selectedHardware: [],
        selectedRole: [],
        selectedOwner: [],
        showOnlineOnly: false,
        showTesting: false,
        clusteringEnabled: true,
        pinLabelsEnabled: true,
        mapInitialized: false,
        map: null,
        markers: [],
        markerClusterGroup: null,

        async init() {
            const data = await loadData();
            this.nodes = data.nodes;
            this.members = data.members;

            // Get current node ID from data attribute and find it in the nodes data
            const currentNodeId = this.$el.getAttribute('data-current-node-id');
            if (currentNodeId) {
                this.currentNode = this.nodes.find(node => node.id === currentNodeId) || null;
            }

            // Make this component globally accessible for popup buttons
            window.nodesPageInstance = this;

            this.applyFilters();

            // Initialize map after DOM is ready
            this.$nextTick(() => {
                setTimeout(() => {
                    this.initMap();
                }, 100);
            });
            
            // Force refresh multiselect options after data is loaded
            this.$nextTick(() => {
                this.refreshMultiselectOptions();
            });
        },
        
        refreshMultiselectOptions() {
            // Find all multiselect components and refresh their options
            const multiselectContainers = this.$el.querySelectorAll('.multiselect-container');
            multiselectContainers.forEach(container => {
                if (container._x_dataStack && container._x_dataStack[0]) {
                    const multiselectData = container._x_dataStack[0];
                    if (multiselectData.updateOptions) {
                        multiselectData.updateOptions();
                    }
                }
            });
        },

        // Navigate to node details page (simpler server-side approach)
        navigateToNodeDetails(node) {
            const nodeIdParts = node.id.split('.');
            const shortId = nodeIdParts[0]; // e.g. "rep01" from "rep01.ip3.ipnt.uk"
            const area = node.area.toLowerCase(); // e.g. "ip3"

            // Direct navigation to server route
            window.location.href = `/nodes/${area}/${shortId}`;
        },

        get availableHardware() {
            return [...new Set(this.nodes.map(node => node.hardware))];
        },

        get availableOwners() {
            return [...new Set(this.nodes.map(node => node.memberId))].sort();
        },

        get availableRoles() {
            return [...new Set(this.nodes.filter(node => node.isTesting !== true).map(node => node.meshRole))].sort();
        },

        get onlineNodesCount() {
            return this.filteredNodes.filter(node => node.isOnline !== false).length;
        },

        get repeaterNodesCount() {
            return this.filteredNodes.filter(node => node.meshRole === 'repeater').length;
        },

        focusNodeOnMap(node) {
            if (this.map) {
                this.map.setView([node.location.lat, node.location.lng], 15);
            }
            // Also navigate to the node page
            this.navigateToNode(node);

            // Scroll to top after a brief delay to allow DOM updates
            setTimeout(() => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }, 100);
        },

        initMap() {
            if (this.mapInitialized || typeof L === 'undefined') return;

            let center, zoom;

            // If viewing an individual node, center on that node
            if (this.currentNode && this.currentNode.location && this.currentNode.location.lat && this.currentNode.location.lng) {
                center = { lat: this.currentNode.location.lat, lng: this.currentNode.location.lng };
                zoom = 18; // Higher zoom for individual node view
            } else {
                // Calculate bounds from filtered nodes
                const nodesWithLocation = this.filteredNodes.filter(node =>
                    node.showOnMap && node.location && node.location.lat && node.location.lng
                );

                if (nodesWithLocation.length > 0) {
                    const bounds = L.latLngBounds(nodesWithLocation.map(node => [node.location.lat, node.location.lng]));
                    center = bounds.getCenter();
                    // Calculate appropriate zoom level
                    zoom = nodesWithLocation.length === 1 ? 13 : 11;
                } else {
                    // Fallback to config or default
                    center = config.map?.center || { lat: 52.05917, lng: 1.15545 };
                    zoom = config.map?.zoom || 11;
                }
            }

            this.map = L.map('nodesMap').setView([center.lat, center.lng], zoom);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            this.mapInitialized = true;

            // Wait for map to be ready before initializing cluster group
            this.map.whenReady(() => {
                // Add a small delay to ensure everything is fully initialized
                setTimeout(() => {
                    // Initialize marker cluster group after map is ready
                    if (typeof L.markerClusterGroup !== 'undefined') {
                        this.markerClusterGroup = L.markerClusterGroup({
                            chunkedLoading: true,
                            maxClusterRadius: 50,
                            spiderfyOnMaxZoom: false, // Disable spiderfy to avoid map access issues
                            showCoverageOnHover: false,
                            zoomToBoundsOnClick: false, // Disable zoom to bounds to prevent map access issues
                            disableClusteringAtZoom: 16, // Disable clustering at high zoom levels
                            animate: false // Disable animations to prevent timing issues
                        });

                        // Add custom cluster click handler to avoid zoom issues
                        this.markerClusterGroup.on('clusterclick', (e) => {
                            try {
                                // Simple zoom in instead of bounds fitting
                                const currentZoom = this.map.getZoom();
                                if (currentZoom < 15) {
                                    this.map.setView(e.latlng, currentZoom + 2);
                                }
                            } catch (error) {
                                console.warn('Error handling cluster click:', error);
                            }
                        });

                        // Only add cluster group to map if clustering is enabled
                        if (this.clusteringEnabled) {
                            this.map.addLayer(this.markerClusterGroup);
                        }
                    }

                    this.updateMapMarkers();
                    this.fitMapToNodes();
                }, 100);
            });
        },

        fitMapToNodes() {
            if (!this.map) return;

            // Don't auto-fit if we're viewing an individual node
            if (this.currentNode) return;

            const nodesWithLocation = this.filteredNodes.filter(node =>
                node.showOnMap && node.location && node.location.lat && node.location.lng
            );

            if (nodesWithLocation.length > 1) {
                try {
                    const bounds = L.latLngBounds(nodesWithLocation.map(node => [node.location.lat, node.location.lng]));
                    this.map.fitBounds(bounds, { padding: [20, 20], maxZoom: 13 });
                } catch (error) {
                    console.warn('Error fitting map to nodes:', error);
                }
            } else if (nodesWithLocation.length === 1) {
                const node = nodesWithLocation[0];
                this.map.setView([node.location.lat, node.location.lng], 13);
            }
        },

        updateMapMarkers() {
            if (!this.map) return;

            try {
                // Clear existing markers from both cluster group and direct map
                if (this.markerClusterGroup) {
                    this.markerClusterGroup.clearLayers();
                }
                
                // Always clear individual markers from map
                this.markers.forEach(marker => {
                    if (this.map.hasLayer(marker)) {
                        this.map.removeLayer(marker);
                    }
                });
                this.markers = [];
            } catch (error) {
                console.warn('Error clearing markers:', error);
                this.markers = [];
            }

            // Use cluster group if available and clustering is enabled
            const useClusterGroup = this.markerClusterGroup && this.clusteringEnabled;
            
            // Ensure cluster group is added to map if clustering is enabled
            if (this.clusteringEnabled && this.markerClusterGroup && !this.map.hasLayer(this.markerClusterGroup)) {
                this.map.addLayer(this.markerClusterGroup);
            }
            
            // Remove cluster group from map if clustering is disabled
            if (!this.clusteringEnabled && this.markerClusterGroup && this.map.hasLayer(this.markerClusterGroup)) {
                this.map.removeLayer(this.markerClusterGroup);
            }

            // Determine which nodes to show on map
            let nodesToShow = this.filteredNodes;

            // If viewing an individual node, ensure it's included even if filtered out
            if (this.currentNode) {
                const currentNodeInFiltered = this.filteredNodes.find(n => n.id === this.currentNode.id);
                if (!currentNodeInFiltered) {
                    // Add current node to the list if it's not in filtered results
                    nodesToShow = [...this.filteredNodes, this.currentNode];
                }
            }

            // Add markers for nodes
            nodesToShow.forEach(node => {
                if (!node.showOnMap || !node.location || !node.location.lat || !node.location.lng) return;

                try {
                    // Create status indicator icon
                    let statusColor;
                    if (node.isTesting === true) {
                        statusColor = '#6633ff'; // blue for testing nodes
                    } else {
                        statusColor = node.isOnline !== false ? '#10b981' : '#ef4444'; // green for online, red for offline
                    }

                    // Make current node marker larger and more prominent
                    const isCurrentNode = this.currentNode && node.id === this.currentNode.id;
                    const markerSize = isCurrentNode ? 'w-8 h-8' : 'w-6 h-6';
                    const iconSize = isCurrentNode ? [32, 32] : [24, 24];
                    const iconAnchor = isCurrentNode ? [16, 16] : [12, 12];
                    const borderWidth = isCurrentNode ? 'border-4' : 'border-2';

                    const customIcon = L.divIcon({
                        html: `<div style="background-color: ${statusColor};" class="${markerSize} rounded-full ${borderWidth} border-white shadow-lg ${isCurrentNode ? 'animate-pulse' : ''}"></div>`,
                        className: 'custom-marker',
                        iconSize: iconSize,
                        iconAnchor: iconAnchor
                    });

                    const marker = L.marker([node.location.lat, node.location.lng], { icon: customIcon });
                    
                    // Add tooltip only if pin labels are enabled
                    if (this.pinLabelsEnabled) {
                        marker.bindTooltip(node.id, {
                            permanent: true,
                            direction: 'right',
                            offset: [15, 0],
                            className: 'node-tooltip'
                        });
                    }
                    
                    // Add popup
                    marker.bindPopup(`
                        <div class="max-w-xs">
                            <strong class="text-lg">${node.name}</strong><br>
                            <div class="mt-2 space-y-1 text-sm">
                                <div><em>Owner:</em> ${this.getMemberName(node.memberId)}</div>
                                <!--
                                <div class="flex items-center mt-2">
                                    <div class="w-2 h-2 rounded-full mr-2" style="background-color: ${statusColor}"></div>
                                    <span class="font-medium">${node.isOnline !== false ? 'Online' : 'Offline'}</span>
                                </div>
                                -->
                            </div>
                            <div class="mt-3 pt-2 border-t border-gray-200">
                                <button onclick="window.nodesPageInstance.navigateToNodeDetails({id: '${node.id}', area: '${node.area}'})" class="text-primary hover:text-accent text-sm font-medium">
                                    View Node Details
                                </button>
                            </div>
                        </div>
                    `, {
                        closeOnClick: false,
                        autoClose: false,
                        closeButton: true
                    });

                    // Add to cluster group if clustering is enabled, otherwise directly to map
                    if (useClusterGroup) {
                        this.markerClusterGroup.addLayer(marker);
                    } else {
                        marker.addTo(this.map);
                    }

                    this.markers.push(marker);
                } catch (error) {
                    console.warn('Error adding marker for node:', node.id, error);
                }
            });
        },

        applyFilters() {
            this.filteredNodes = this.nodes.filter(node => {
                const hardwareMatch = this.selectedHardware.length === 0 ||
                    this.selectedHardware.some(hw => node.hardware.toLowerCase().includes(hw.toLowerCase()));
                const roleMatch = this.selectedRole.length === 0 ||
                    this.selectedRole.includes(node.meshRole);
                const ownerMatch = this.selectedOwner.length === 0 ||
                    this.selectedOwner.includes(node.memberId);
                const onlineMatch = !this.showOnlineOnly || node.isOnline !== false;
                const testingMatch = this.showTesting || node.isTesting !== true;
                
                const matches = hardwareMatch && roleMatch && ownerMatch && onlineMatch && testingMatch;
                
                return matches;
            }).sort((a, b) => {
                // Sort by area first, then by ID
                const areaComparison = a.area.localeCompare(b.area);
                if (areaComparison !== 0) return areaComparison;

                // If areas are the same, sort by ID
                return a.id.localeCompare(b.id);
            });

            this.updateMapMarkers();
            this.fitMapToNodes();
        },

        getMemberName(memberId) {
            const member = this.members.find(m => m.id === memberId);
            return member ? member.name : 'Unknown';
        },

        getUniqueHardware() {
            return [...new Set(this.nodes.map(node => node.hardware))];
        },

        getUniqueRoles() {
            return [...new Set(this.nodes.map(node => node.meshRole))];
        },

        toggleClustering() {
            if (this.map) {
                this.updateMapMarkers();
            }
        },

        togglePinLabels() {
            if (this.map) {
                this.updateMapMarkers();
            }
        }
    }
}

// Members page data
function membersData() {
    return {
        members: [],
        nodes: [],

        async init() {
            const data = await loadData();
            this.members = data.members;
            this.nodes = data.nodes;
        },

        getNodeCount(memberId) {
            return this.nodes.filter(node => node.memberId === memberId && node.isPublic).length;
        },

        formatDate(dateString) {
            if (!dateString) return '';
            return new Date(dateString).toLocaleDateString('en-GB', {
                year: 'numeric',
                month: 'long'
            });
        },

        getAvatarUrl(avatarPath) {
            if (!avatarPath) return '';
            const pathPrefix = getPathPrefix();
            return pathPrefix + avatarPath;
        }
    }
}

// Global QR Code generation function
window.generateQRCode = function(nodeUri, canvasId) {
    if (!nodeUri || typeof qrcode === 'undefined') {
        console.error('Missing nodeUri or qrcode library not loaded');
        return;
    }

    setTimeout(() => {
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            try {
                const qr = qrcode(0, 'M');
                qr.addData(nodeUri);
                qr.make();

                const ctx = canvas.getContext('2d');
                const borderSize = 20;
                const qrSize = 210;
                const totalSize = qrSize + (borderSize * 2);
                const modules = qr.getModuleCount();
                const cellSize = qrSize / modules;

                canvas.width = totalSize;
                canvas.height = totalSize;

                // Fill entire canvas with white background
                ctx.fillStyle = '#FFFFFF';
                ctx.fillRect(0, 0, totalSize, totalSize);

                // Draw QR code with border offset
                ctx.fillStyle = '#000000';
                for (let row = 0; row < modules; row++) {
                    for (let col = 0; col < modules; col++) {
                        if (qr.isDark(row, col)) {
                            ctx.fillRect(
                                borderSize + (col * cellSize),
                                borderSize + (row * cellSize),
                                cellSize,
                                cellSize
                            );
                        }
                    }
                }
            } catch (error) {
                console.error('QR Code generation error:', error);
            }
        } else {
            console.error('Canvas element not found:', canvasId);
        }
    }, 100);
};

// Contact page data
function contactData() {
    return {
        config: {},

        async init() {
            const data = await loadData();
            this.config = data.config;
        }
    }
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Dark mode persistence
document.addEventListener('alpine:init', () => {
    Alpine.store('darkMode', {
        on: false,

        init() {
            // Initialize from localStorage or OS preference
            const storedValue = localStorage.getItem('darkMode');

            if (storedValue !== null) {
                // User has explicitly set a preference
                this.on = storedValue === 'true';
            } else {
                // Default to OS preference
                this.on = window.matchMedia('(prefers-color-scheme: dark)').matches;
            }

            // Sync with the class that was already applied in head
            if (this.on) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }

            // Listen for OS theme changes if user hasn't explicitly set a preference
            if (storedValue === null) {
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                    // Only update if user hasn't manually set a preference
                    if (localStorage.getItem('darkMode') === null) {
                        this.on = e.matches;
                        if (this.on) {
                            document.documentElement.classList.add('dark');
                        } else {
                            document.documentElement.classList.remove('dark');
                        }
                    }
                });
            }
        },

        toggle() {
            this.on = !this.on;
            localStorage.setItem('darkMode', this.on.toString());

            // Update document class immediately
            if (this.on) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }
    });
});
