// Network visualization configuration and functionality
console.log('Network visualization script loaded');

// Debug check for D3.js
if (typeof d3 === 'undefined') {
    console.error('D3.js is not loaded! Please check script inclusions');
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing network visualization');
    // Check if the network graph container exists
    const networkContainer = document.getElementById('networkGraph');
    if (!networkContainer) return;

    // Get collaboration data from the window object (passed from Flask)
    const collaborationData = window.collaborationData;
    if (!collaborationData) {
        console.error('No collaboration data available');
        return;
    }

    console.log('Loaded collaboration data:', collaborationData);

    // Configuration
    const width = networkContainer.clientWidth || 800; // Fallback if clientWidth is 0
    const height = 600;
    const nodeRadius = 24; // Slightly smaller for a more modern look
    const nodePadding = 5;    // Modern color palette - using a muted, sophisticated palette
    const modernPalette = [
        '#264653', // Dark cyan
        '#2a9d8f', // Teal
        '#e9c46a', // Gold
        '#f4a261', // Peach
        '#e76f51', // Terracotta
        '#606c38', // Olive
        '#dda15e', // Camel
        '#bc6c25', // Rust
        '#5f0f40', // Burgundy
        '#0b525b'  // Deep teal
    ];

    // Security score color scale - from red (low security) to green (high security)
    const securityColorScale = d3.scaleLinear()
        .domain([0.33, 0.5, 0.66, 1])
        .range(['#e63946', '#f4a261', '#a8dadc', '#2a9d8f']);

    // Use a more modern color scale for fallback colors when security score isn't available
    const colors = d3.scaleOrdinal(modernPalette);

    console.log('Container dimensions:', { width, height });

    // Initialize the SVG with explicit dimensions
    const svg = d3.select('#networkGraph')
        .append('svg')
        .attr('width', '100%')
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');

    // Create arrow marker for directed edges
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '-5 -5 10 10')
        .attr('refX', nodeRadius)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M -5,-5 L 5,0 L -5,5')
        .attr('class', 'arrowhead');    // Create the force simulation with improved centering after repulsion
    const simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(150)) // Fixed distance for better visibility
        .force('charge', d3.forceManyBody().strength(-800)) // Stronger repulsion
        .force('center', d3.forceCenter(width / 2, height / 2).strength(0.1)) // Stronger centering force
        .force('x', d3.forceX(width / 2).strength(0.1)) // Additional x-centering force
        .force('y', d3.forceY(height / 2).strength(0.1)) // Additional y-centering force
        .force('collision', d3.forceCollide().radius(nodeRadius * 1.8)) // Larger collision radius
        .alphaDecay(0.008) // Even slower decay for more balanced layout
        .alphaTarget(0);

    // Text wrapping function for node labels
    function wrap(text, width) {
        text.each(function() {
            const text = d3.select(this);
            const words = text.text().split(/\s+/).reverse();
            const lineHeight = 1.1;
            const y = text.attr('y');
            const dy = parseFloat(text.attr('dy'));
            let line = [];
            let lineNumber = 0;
            let tspan = text.text(null).append('tspan').attr('x', 0).attr('y', y).attr('dy', dy + 'em');
            
            let word;
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(' '));
                if (line.join(' ').length > 10) {
                    line.pop();
                    tspan.text(line.join(' '));
                    line = [word];
                    tspan = text.append('tspan').attr('x', 0).attr('y', y).attr('dy', ++lineNumber * lineHeight + dy + 'em').text(word);
                }
            }
        });
    }

    // Drag functions
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
    }    function updateNetwork(monthData) {
        if (!monthData || !Array.isArray(monthData) || monthData.length === 0) {
            console.error('No valid month data available:', monthData);
            // If no data, create a simple placeholder node to demonstrate functionality
            monthData = [
                {'from': 'Sample User 1', 'to': 'Sample User 2', 'count': 5},
                {'from': 'Sample User 2', 'to': 'Sample User 3', 'count': 3},
                {'from': 'Sample User 3', 'to': 'Sample User 1', 'count': 7}
            ];
        }
        
        console.log('Month data received:', monthData);
        
        // Process the data
        const nodesSet = new Set();
        const nodeLinkCount = new Map(); // Track number of connections for each node
        
        monthData.forEach(link => {
            nodesSet.add(link.from);
            nodesSet.add(link.to);
            
            // Count connections for sizing nodes
            nodeLinkCount.set(link.from, (nodeLinkCount.get(link.from) || 0) + link.count);
            nodeLinkCount.set(link.to, (nodeLinkCount.get(link.to) || 0) + 1); // Count being targeted with less weight
        });
        
        // Find max connections for scaling
        const maxConnections = Math.max(...nodeLinkCount.values(), 1);
          // Create node scale based on connections - with improved aesthetics and text fit
        const nodeScale = d3.scaleLinear()
            .domain([1, maxConnections])
            .range([24, 42]) // Increased range for better text fit
            .clamp(true);// Create graph data
        function debugObject(obj, label) {
            console.log(`--- DEBUG ${label} ---`);
            console.log(JSON.stringify(obj, null, 2));
            console.log(`--- END ${label} ---`);
            return obj; // Pass through the object for chaining
        }          const nodes = Array.from(nodesSet).map(name => {
            const connections = nodeLinkCount.get(name) || 0;
            
            // More sophisticated name processing for better fit
            let displayName;
            if (name.indexOf(' ') > 0) {
                // If there's a space, use initials or first name
                const nameParts = name.split(' ');
                if (nameParts.length >= 2) {
                    // Use initials for first and last name
                    displayName = nameParts[0][0] + nameParts[nameParts.length-1][0];
                    if (displayName.length < 2) displayName = nameParts[0]; // Fallback
                } else {
                    displayName = nameParts[0];
                }
            } else if (name.indexOf('-') > 0) {
                // For hyphenated names, use first part
                displayName = name.split('-')[0];
            } else if (name.length > 10) {
                // For long names without spaces, truncate
                displayName = name.substring(0, 8) + '..';
            } else {
                displayName = name;
            }
            
            // Look up security score if available
            const securityScore = window.securityScores && window.securityScores[name.toLowerCase()] !== undefined 
                ? window.securityScores[name.toLowerCase()] 
                : null;
            
            return { 
                id: name, 
                name: name,
                displayName: displayName,
                fullName: name, // Keep original full name for tooltips
                securityScore: securityScore, // Add security score
                connections: connections,
                radius: nodeScale(connections) + (displayName.length * 0.8), // Dynamic radius based on name length
                // Explicitly add coordinates
                x: width / 2 + (Math.random() - 0.5) * 100,
                y: height / 2 + (Math.random() - 0.5) * 100
            };
        });
        
        const links = monthData.map(d => ({
            source: d.from,
            target: d.to,
            value: d.count
        }));
        
        console.log('Nodes created:', nodes.length);
        console.log('Links created:', links.length);
        
        const graphData = {
            nodes: nodes,
            links: links
        };
        
        console.log('Graph data processed:', graphData);        // Update the visualization
        const maxLinkValue = d3.max(graphData.links, d => d.value);
        const minLinkValue = d3.min(graphData.links, d => d.value);
        const maxNodeConnections = d3.max(graphData.nodes, n => n.connections);
        
        // Add explanatory text for the log scale to the UI
        console.log(`Link values range from ${minLinkValue} to ${maxLinkValue} (log scaled for visibility)`)
          // Create gradient definitions for node aesthetics - now with security score coloring
        const createGradientDefs = () => {
            graphData.nodes.forEach(node => {
                const colorId = node.id.replace(/[^a-zA-Z0-9]/g, '_');
                const gradientId = `gradient-${colorId}`;
                
                // Get security score for this node
                const nodeIdLower = node.id.toLowerCase();
                const securityScore = window.securityScores && window.securityScores[nodeIdLower] !== undefined 
                    ? window.securityScores[nodeIdLower] 
                    : null;
                
                // Store security score in node object for reference
                node.securityScore = securityScore;
                
                // Determine node color based on security score if available, otherwise use default color scheme
                let nodeColor;
                if (securityScore !== null) {
                    nodeColor = securityColorScale(securityScore);
                    // Add security score class for reference
                    if (securityScore < 0.33) {
                        node.securityClass = 'low-security';
                    } else if (securityScore < 0.66) {
                        node.securityClass = 'medium-security';
                    } else {
                        node.securityClass = 'high-security';
                    }
                } else {
                    nodeColor = colors(node.id);
                    node.securityClass = 'unknown-security';
                }
                
                // Create slightly darker version of the color for gradient
                const darkerColor = d3.color(nodeColor).darker(0.5);
                
                const gradient = defs.append("radialGradient")
                    .attr("id", gradientId)
                    .attr("cx", "30%")
                    .attr("cy", "30%")
                    .attr("r", "70%")
                    .attr("fx", "30%")
                    .attr("fy", "30%");
                
                gradient.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", nodeColor)
                    .attr("stop-opacity", 1);
                
                gradient.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", darkerColor)
                    .attr("stop-opacity", 1);
                    
                node.gradientId = gradientId;
                node.baseColor = nodeColor; // Store the base color for reference
            });
        };// More nuanced scales for visual elements - using enhanced logarithmic scale for link width
        const linkWidthScale = d3.scaleLog()
            .domain([Math.max(minLinkValue, 1), Math.max(maxLinkValue, 2)])  // Log scale requires positive values
            .range([1.5, 8])  // Wider range for more dramatic scaling of line thickness
            .clamp(true);     // Prevent values outside of domain
            
        const linkOpacityScale = d3.scaleLinear()
            .domain([minLinkValue, maxLinkValue])
            .range([0.5, 0.9]); // Increased minimum opacity for better visibility
            
        // Color palette variations for link strength - using more distinct colors
        const linkColorScale = d3.scaleLinear()
            .domain([minLinkValue, maxLinkValue])
            .range(['#2a9d8f', '#264653']); // Using colors from the node palette for better harmony        // Clear previous elements
        svg.selectAll('*').remove();
        
        // Re-append the defs with marker
        const defs = svg.append('defs');
        
        // Create consistent arrowhead marker that doesn't scale with line weight
        defs.append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -3 6 6')
            .attr('refX', nodeRadius + 7) // Increased distance from node
            .attr('refY', 0)
            .attr('markerWidth', 5) // Consistent size
            .attr('markerHeight', 5) 
            .attr('orient', 'auto')
            .attr('markerUnits', 'userSpaceOnUse') // This ensures consistent size regardless of stroke width
            .append('path')
            .attr('d', 'M0,-3L6,0L0,3')
            .attr('class', 'arrowhead');
            
        // Create gradient definitions for more aesthetic nodes
        createGradientDefs();// Create links with weight-based styling - enhanced for clarity
        const linksSelection = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(graphData.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .style('stroke', d => linkColorScale(d.value)) // Use the defined color scale
            .style('stroke-opacity', d => linkOpacityScale(d.value)) // Opacity based on weight
            .style('stroke-width', d => {
                // Enhanced log-scale for line weight with clearer visual distinction
                const width = linkWidthScale(Math.max(d.value, 1));
                console.log(`Link value: ${d.value}, scaled width: ${width}`); // Debug log
                return width;
            }) // Width based on enhanced log scale
            .style('stroke-linecap', 'round') // Round the line ends for a cleaner look
            .attr('marker-end', 'url(#arrowhead)');// Add arrowhead

        // Create nodes group with minimal, modern design
        const nodesSelection = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('.node')
            .data(graphData.nodes)
            .enter()
            .append('g')
            .attr('class', 'node')            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))            .on('mouseover', function(event, d) {
                // Highlight connected links and nodes
                linksSelection
                    .style('stroke-opacity', l => 
                        l.source.id === d.id || l.target.id === d.id 
                            ? 1.0   // Connected links are fully opaque
                            : 0.1)  // Other links fade more to background for better contrast
                    .style('stroke-width', l => {
                        if (l.source.id === d.id || l.target.id === d.id) {
                            // Connected links keep their logarithmic scale but get a boost
                            const baseWidth = linkWidthScale(Math.max(l.value, 1));
                            return baseWidth * 1.3;
                        }
                        return linkWidthScale(Math.max(l.value, 1));
                    });
                
                // Highlight connected nodes
                nodesSelection.style('opacity', n => 
                    n.id === d.id || 
                    graphData.links.some(l => 
                        (l.source.id === d.id && l.target.id === n.id) || 
                        (l.target.id === d.id && l.source.id === n.id)
                    ) ? 1 : 0.4);
                    
                // Create or update tooltip
                let tooltip = d3.select('#node-tooltip');
                if (tooltip.empty()) {
                    tooltip = d3.select('body').append('div')
                        .attr('id', 'node-tooltip')
                        .attr('class', 'node-tooltip');
                }
                
                // Build tooltip content with full name and security score
                let tooltipContent = d.fullName || d.name;
                
                // Add security score info if available
                if (d.securityScore !== null && d.securityScore !== undefined) {
                    const scorePercent = Math.round(d.securityScore * 100);
                    let securityLevel;
                    if (d.securityScore < 0.33) {
                        securityLevel = 'Low';
                    } else if (d.securityScore < 0.66) {
                        securityLevel = 'Medium';
                    } else if (d.securityScore < 0.85) {
                        securityLevel = 'Good';
                    } else {
                        securityLevel = 'Excellent';
                    }
                    
                    tooltipContent += `<br/><span class="security-score ${d.securityClass}">Security: ${securityLevel} (${scorePercent}%)</span>`;
                }
                
                // Position and show tooltip
                tooltip
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 30) + 'px')
                    .style('display', 'block')
                    .html(tooltipContent);
                
                // Apply scale effect to current node
                d3.select(this).select('circle')
                    .transition().duration(200)
                    .attr('r', d.radius * 1.05)
                    .style('stroke-width', 2.5);
            })            .on('mouseout', function() {
                // Restore normal appearance with proper logarithmic scaling
                linksSelection
                    .style('stroke-opacity', d => linkOpacityScale(d.value))
                    .style('stroke-width', d => {
                        // Ensure we maintain the logarithmic scale when restoring
                        return linkWidthScale(Math.max(d.value, 1));
                    });
                nodesSelection.style('opacity', 1);
                
                // Hide tooltip
                d3.select('#node-tooltip')
                    .style('display', 'none');
                    
                // Restore node size
                d3.select(this).select('circle')
                    .transition().duration(200)
                    .attr('r', d => d.radius)
                    .style('stroke-width', 2);
            });        // Add enhanced aesthetic node design with gradients and security-based coloring
        nodesSelection.append('circle')
            .attr('r', d => d.radius || nodeRadius)
            .style('fill', d => d.gradientId ? `url(#${d.gradientId})` : colors(d.id))
            .style('stroke', d => {
                // Add stroke color based on security class for additional visual cue
                if (d.securityClass === 'low-security') {
                    return '#e63946';
                } else if (d.securityClass === 'medium-security') {
                    return '#f4a261';
                } else if (d.securityClass === 'high-security') {
                    return '#2a9d8f';
                }
                return '#ffffff';
            })
            .style('stroke-width', 2)
            .style('opacity', 0.95)
            .style('filter', 'drop-shadow(0px 2px 3px rgba(0,0,0,0.15))');// Add text labels showing the names with enhanced styling for better fit
        nodesSelection.append('text')
            .attr('dy', '.35em') // Slightly adjust vertical centering
            .attr('text-anchor', 'middle')
            .text(d => d.displayName || d.name)
            .style('fill', '#ffffff')
            .style('font-weight', '600') // Bolder text for better readability
            .style('font-size', d => {
                // Dynamic font sizing based on display name length and node radius
                const nameLength = (d.displayName || d.name).length;
                if (nameLength > 4) {
                    return Math.min(16, Math.max(11, d.radius / (nameLength * 0.4))) + 'px';
                }
                return '14px'; // Default size for short names
            })
            .style('letter-spacing', '0.02em') // Slightly improve letter spacing
            .style('font-family', "'Inter', 'Segoe UI', sans-serif")
            .style('pointer-events', 'none')
            .style('text-shadow', '0 1px 2px rgba(0,0,0,0.2)'); // Add subtle text shadow for legibility// Define the tick function - with improved centering
        function ticked() {
            try {
                // Keep nodes within bounds with better centering
                graphData.nodes.forEach(node => {
                    // Use node's actual radius for boundary calculation
                    const r = node.radius || nodeRadius;
                    
                    // Ensure x and y are initialized
                    if (typeof node.x !== 'number') node.x = width/2;
                    if (typeof node.y !== 'number') node.y = height/2;
                    
                    // Keep nodes within bounds
                    node.x = Math.max(r, Math.min(width - r, node.x));
                    node.y = Math.max(r, Math.min(height - r, node.y));
                });
                
                // Update link positions
                linksSelection
                    .attr('x1', d => d.source.x || 0)
                    .attr('y1', d => d.source.y || 0)
                    .attr('x2', d => d.target.x || width)
                    .attr('y2', d => d.target.y || height);

                // Update node positions
                nodesSelection
                    .attr('transform', d => `translate(${d.x || width/2},${d.y || height/2})`);
                    
                console.log("Tick function executed, nodes positioned");
            } catch (e) {
                console.error("Error in tick function:", e);
            }
        }// Set up a force simulation that better centers the graph
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Position nodes initially in a circle
        graphData.nodes.forEach((node, i) => {
            const angle = (i / Math.max(1, graphData.nodes.length - 1)) * 2 * Math.PI;
            const radius = Math.min(width, height) / 3;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });
        
        // Create a centering force based on node importance
        const centeringForce = () => {
            // Apply gentle centering force
            graphData.nodes.forEach(node => {
                // More important nodes (more connections) should be more central
                const centerStrength = 0.03 * (1 - (node.connections / (maxNodeConnections || 1) * 0.7));
                node.vx = (node.vx || 0) + (centerX - (node.x || 0)) * centerStrength;
                node.vy = (node.vy || 0) + (centerY - (node.y || 0)) * centerStrength;
            });
        };

        // Stop any ongoing simulation
        simulation.stop();
          // Update simulation with new data and forces - better reflecting the logarithmic scaling
        simulation
            .nodes(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id)
                // Use logarithmic scale for link distances too - stronger links = closer nodes
                .distance(d => {
                    // Create a log scale for distance: stronger links = closer nodes
                    const distanceScale = d3.scaleLog()
                        .domain([Math.max(1, minLinkValue), Math.max(2, maxLinkValue)])
                        .range([80, 160]) // Closer together for stronger links
                        .clamp(true);
                    return distanceScale(Math.max(1, maxLinkValue - d.value + 1));
                })
                .strength(d => 0.3 + (Math.log(d.value + 1) / Math.log(maxLinkValue + 1) * 0.7))) // Log-scaled strength
            .force('charge', d3.forceManyBody()
                .strength(d => -4000 - d.connections * 15)) // More connections = stronger repulsion
            .force('center', d3.forceCenter(centerX, centerY).strength(0.1))
            .force('collision', d3.forceCollide().radius(d => d.radius * 1.2))
            .on('tick', ticked);
        
        // Call tick once to position elements immediately
        ticked();
        
        // Restart the simulation with high energy but quicker cooldown
        simulation.alpha(1).alphaDecay(0.02).restart();
        
        // Log to confirm nodes are there
        console.log('Nodes count:', graphData.nodes.length);
        
        console.log('Simulation restarted with nodes:', graphData.nodes.length);
        
        // Update the table
        updateCollaborationTable(monthData);
    }

    function updateCollaborationTable(data) {
        const tableBody = document.getElementById('collaborationTableBody');
        tableBody.innerHTML = ''; // Clear previous content
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            const fromCell = document.createElement('td');
            fromCell.textContent = item.from;
            row.appendChild(fromCell);
            
            const toCell = document.createElement('td');
            toCell.textContent = item.to;
            row.appendChild(toCell);
            
            const countCell = document.createElement('td');
            countCell.textContent = item.count;
            row.appendChild(countCell);
            
            const statusCell = document.createElement('td');
            let badgeClass, statusText;
            if (item.count >= 12) {
                badgeClass = 'bg-success';
                statusText = 'High';
            } else if (item.count >= 8) {
                badgeClass = 'bg-info';
                statusText = 'Medium';
            } else {
                badgeClass = 'bg-warning';
                statusText = 'Low';
            }
            
            const badge = document.createElement('span');
            badge.className = `badge ${badgeClass}`;
            badge.textContent = statusText;
            statusCell.appendChild(badge);
            
            tableBody.appendChild(row);
        });
    }    // Initialize with sorted months and create slider markers
    function initializeTimeline() {
        if (!collaborationData || typeof collaborationData !== 'object') {
            console.error('Invalid collaboration data:', collaborationData);
            // Create default data if none is available
            collaborationData = {
                "2025-05": [
                    {'from': 'Sample User 1', 'to': 'Sample User 2', 'count': 5},
                    {'from': 'Sample User 2', 'to': 'Sample User 3', 'count': 3},
                    {'from': 'Sample User 3', 'to': 'Sample User 1', 'count': 7}
                ]
            };
        }
        
        const months = Object.keys(collaborationData).sort();
        console.log('Available months:', months);
        const mostRecentMonth = months.length > 0 ? months[months.length - 1] : null;
        console.log('Most recent month:', mostRecentMonth);

        // Set up the date slider
        const slider = document.getElementById('dateSlider');
        const sliderTrack = document.getElementById('dateSliderTrack');
        const currentPeriodEl = document.getElementById('currentPeriod');

        if (!slider || !sliderTrack || !currentPeriodEl) {
            console.error('Required elements not found');
            return;
        }

        // Configure the slider
        slider.min = 0;
        slider.max = months.length - 1;
        slider.value = months.length - 1; // Start with most recent month

        // Create date markers
        months.forEach((month, index) => {
            const marker = document.createElement('div');
            marker.className = 'date-marker';
            marker.style.left = `${(index / (months.length - 1)) * 100}%`;
            
            const label = document.createElement('div');
            label.className = 'date-label';
            label.textContent = month;
            
            marker.appendChild(label);
            sliderTrack.appendChild(marker);
        });

        // Update network when slider changes
        slider.addEventListener('input', function() {
            const index = parseInt(this.value);
            const selectedMonth = months[index];
            currentPeriodEl.textContent = selectedMonth;
            updateNetwork(collaborationData[selectedMonth]);
            
            // Update active marker
            document.querySelectorAll('.date-marker').forEach((marker, i) => {
                if (i === index) {
                    marker.classList.add('active');
                } else {
                    marker.classList.remove('active');
                }
            });
        });

        // Initialize with selected month
        if (mostRecentMonth) {
            currentPeriodEl.textContent = mostRecentMonth;
            updateNetwork(collaborationData[mostRecentMonth]);
            
            // Highlight the most recent marker
            const lastIndex = months.length - 1;
            const markers = document.querySelectorAll('.date-marker');
            if (markers.length > lastIndex) {
                markers[lastIndex].classList.add('active');
            }
        } else {
            console.error('No months available in the data');
        }
    }

    // Start the initialization
    initializeTimeline();
});
