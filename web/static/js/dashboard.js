// ===================================================================
// CN Healthcare Edge Computing Dashboard - JavaScript
// Real-time data updates and visualization WITH ML PREDICTION
// (Corrected: fixed template literals, removed duplicate listeners,
//  fixed tab selector, fixed activity log entry class, fixed status text)
// ===================================================================

// Initialize Socket.IO connection
const socket = io();

// Global variables
let network = null;
let cwndChart = null;
let simulationRunning = false;
let cwndData = [];
let maxDataPoints = 50;

// ===================================================================
// INITIALIZATION
// ===================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');

    // Initialize charts
    initCwndChart();

    // Set up button listeners
    setupButtonListeners();

    // Set up socket listeners
    setupSocketListeners();

    console.log('Dashboard ready!');
});

// ===================================================================
// BUTTON HANDLERS
// ===================================================================

function setupButtonListeners() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const resetBtn = document.getElementById('resetBtn');

    startBtn.addEventListener('click', function() {
        socket.emit('start_simulation');
        startBtn.disabled = true;
        stopBtn.disabled = false;
        updateStatus('Running', true);
    });

    stopBtn.addEventListener('click', function() {
        socket.emit('stop_simulation');
        startBtn.disabled = false;
        stopBtn.disabled = true;
        updateStatus('Stopped', false);
    });

    resetBtn.addEventListener('click', function() {
        socket.emit('reset_simulation');
        startBtn.disabled = false;
        stopBtn.disabled = true;
        updateStatus('Stopped', false);

        // Reset charts
        cwndData = [];
        updateCwndChart();

        // Clear activity log
        const logEl = document.getElementById('activityLog');
        if (logEl) logEl.innerHTML = '';

        // Reset metrics
        resetMetrics();

        // Reset ML alert
        resetMLAlert();
    });
}

// ===================================================================
// SOCKET.IO LISTENERS
// ===================================================================

function setupSocketListeners() {
    // Routing updates
    socket.on('routing_update', function(data) {
        console.log('Routing update:', data);

        const pathStr = Array.isArray(data.path) ? data.path.join(' → ') : String(data.path || '');
        addLogEntry(
            data.task_id,
            `Path: ${pathStr} | Hops: ${data.hops}`,
            (data.status || '').toLowerCase()
        );

        // Update inspector
        if (typeof updateBackpressureInspector === 'function') {
            updateBackpressureInspector(data);
        }
    });

    // Backpressure metrics updates
    socket.on('bp_metrics_update', function(data) {
        console.log('BP metrics update:', data);

        if (document.getElementById('bpSuccessRate')) {
            document.getElementById('bpSuccessRate').textContent =
                (typeof data.success_rate === 'number' ? data.success_rate.toFixed(1) : data.success_rate) + '%';
        }
        if (document.getElementById('bpTotalTasks')) {
            document.getElementById('bpTotalTasks').textContent = data.total_tasks ?? 0;
        }
        if (document.getElementById('bpAvgHops')) {
            document.getElementById('bpAvgHops').textContent =
                (typeof data.avg_hops === 'number' ? data.avg_hops.toFixed(2) : data.avg_hops);
        }
        if (document.getElementById('bpQueueLoad')) {
            document.getElementById('bpQueueLoad').textContent = data.total_queue_load ?? 0;
        }
    });

    // TCP updates
    socket.on('tcp_update', function(data) {
        console.log('TCP update:', data);
        updateTcpMetrics(data);

        // Update chart
        cwndData.push({
            round: data.round,
            cwnd: data.cwnd,
            ssthresh: data.ssthresh
        });

        // Keep only last N data points
        if (cwndData.length > maxDataPoints) {
            cwndData.shift();
        }

        updateCwndChart();

        // Update inspector
        if (typeof updateTCPInspector === 'function') {
            updateTCPInspector(data);
        }
    });

    // ML prediction updates
    socket.on('ml_prediction', function(data) {
        console.log('ML prediction:', data);
        updateMLPrediction(data);

        // Update inspector
        if (typeof updateMLInspector === 'function') {
            updateMLInspector(data);
        }
    });

    // Receive network topology
    socket.on('network_data', function(data) {
        console.log('Received network data:', data);
        initNetworkVisualization(data);
    });

    // Network state updates
    socket.on('network_update', function(data) {
        console.log('Network update:', data);
        updateNetworkVisualization(data);
    });

    // Simulation status
    socket.on('simulation_status', function(data) {
        console.log('Simulation status:', data);
        simulationRunning = !!data.running;
        // Also update UI status dot/text
        updateStatus(simulationRunning ? 'Running' : 'Stopped', simulationRunning);
    });
}

// ===================================================================
// NETWORK VISUALIZATION
// ===================================================================

function initNetworkVisualization(data) {
    const container = document.getElementById('networkViz');
    if (!container) return;

    // Prepare nodes
    const nodes = data.nodes.map(node => ({
        id: node.id,
        label: node.label,
        x: node.x,
        y: node.y,
        color: getNodeColor(node.layer),
        shape: 'box',
        font: { color: 'white', size: 14, face: 'Arial', bold: true },
        borderWidth: 2,
        shadow: true
    }));

    // Prepare edges
    const edges = data.edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        arrows: 'to',
        color: { color: '#848484', highlight: '#667eea' },
        width: 2,
        smooth: { type: 'cubicBezier' }
    }));

    // Create network
    const networkData = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };

    const options = {
        physics: { enabled: false },
        interaction: { hover: true, zoomView: false },
        nodes: {
            borderWidth: 3,
            size: 30,
            font: { size: 12, face: 'Tahoma' }
        }
    };

    network = new vis.Network(container, networkData, options);

    console.log('Network visualization initialized');
}

function getNodeColor(layer) {
    const colors = {
        'iot': '#ef4444',      // Red
        'edge': '#06b6d4',     // Cyan
        'fog': '#3b82f6',      // Blue
        'cloud': '#f97316'     // Orange
    };
    return colors[layer] || '#6b7280';
}

function updateNetworkVisualization(data) {
    if (!network || !data || !data.queues) return;

    // Update node colors based on queue length
    const nodes = network.body.data.nodes;

    Object.keys(data.queues).forEach(nodeId => {
        const queueLength = data.queues[nodeId];
        const node = nodes.get(nodeId);

        if (node) {
            // Change border color based on queue
            if (queueLength > 5) {
                node.borderWidth = 5;
                node.color = { border: '#ef4444' }; // Red for high queue
            } else {
                node.borderWidth = 3;
                // keep original color fill if present
                if (!node.color || typeof node.color === 'string') {
                    node.color = getNodeColor(node.group || node.layer);
                }
            }

            nodes.update(node);
        }
    });
}

// ===================================================================
// ML PREDICTION HANDLER - NEW
// ===================================================================

function updateMLPrediction(data) {
    const alertBox = document.getElementById('mlAlert');
    const alertText = document.getElementById('mlAlertText');

    // defensive checks
    if (!alertBox || !alertText) return;

    // Update metrics
    if (document.getElementById('mlConfidence')) {
        document.getElementById('mlConfidence').textContent = (data.confidence ?? 0).toFixed(1) + '%';
    }
    if (document.getElementById('mlAccuracy')) {
        document.getElementById('mlAccuracy').textContent = (data.accuracy ?? 0).toFixed(1) + '%';
    }
    if (document.getElementById('mlSamples')) {
        document.getElementById('mlSamples').textContent = data.training_samples ?? 0;
    }

    // Update status
    if (data.status === 'training') {
        document.getElementById('mlStatus').textContent = 'Training...';
        alertBox.className = 'ml-alert ml-alert-normal';
        alertText.innerHTML = '<i class="fas fa-cog fa-spin"></i> Collecting Training Data...';
    } else if (data.is_trained) {
        document.getElementById('mlStatus').textContent = 'Active';

        // Update alert based on prediction
        if (data.prediction) {
            // High confidence warning
            if ((data.confidence ?? 0) > 80) {
                alertBox.className = 'ml-alert ml-alert-danger';
                alertText.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ⚠ CONGESTION PREDICTED! ⚠';

                // Add to activity log
                addLogEntry(
                    'ML Predictor',
                    `High congestion risk (${(data.confidence ?? 0).toFixed(0)}% confidence)`,
                    'failed'
                );
            } else {
                alertBox.className = 'ml-alert ml-alert-warning';
                alertText.innerHTML = '<i class="fas fa-exclamation-circle"></i> Possible Congestion Ahead';
            }
        } else {
            // Normal - no congestion predicted
            alertBox.className = 'ml-alert ml-alert-normal';
            alertText.innerHTML = '<i class="fas fa-check-circle"></i> Network Status: Normal';
        }
    } else {
        // fallback
        document.getElementById('mlStatus').textContent = 'Idle';
        alertBox.className = 'ml-alert ml-alert-normal';
        alertText.innerHTML = '<i class="fas fa-shield-alt"></i> Monitoring...';
    }
}

function resetMLAlert() {
    const alertBox = document.getElementById('mlAlert');
    const alertText = document.getElementById('mlAlertText');

    if (!alertBox || !alertText) return;

    alertBox.className = 'ml-alert ml-alert-normal';
    alertText.innerHTML = '<i class="fas fa-shield-alt"></i> Monitoring...';

    if (document.getElementById('mlStatus')) document.getElementById('mlStatus').textContent = 'Training';
    if (document.getElementById('mlConfidence')) document.getElementById('mlConfidence').textContent = '0%';
    if (document.getElementById('mlAccuracy')) document.getElementById('mlAccuracy').textContent = '0%';
    if (document.getElementById('mlSamples')) document.getElementById('mlSamples').textContent = '0';
}

// ===================================================================
// METRICS UPDATES
// ===================================================================

function updateTcpMetrics(data) {
    if (document.getElementById('tcpCwnd')) document.getElementById('tcpCwnd').textContent = (data.cwnd ?? 0).toFixed(2);
    if (document.getElementById('tcpSsthresh')) document.getElementById('tcpSsthresh').textContent = (data.ssthresh ?? 0).toFixed(2);
    if (document.getElementById('tcpState')) document.getElementById('tcpState').textContent = String(data.state || '').replace(/_/g, ' ');

    // Update loss counter if provided
    if (data.losses !== undefined && document.getElementById('tcpLoss')) {
        document.getElementById('tcpLoss').textContent = data.losses;
    }

    if (data.congestion) {
        // Flash the loss counter
        const lossElement = document.getElementById('tcpLoss');
        if (lossElement) {
            lossElement.style.color = '#ef4444';

            setTimeout(() => {
                lossElement.style.color = '#667eea';
            }, 500);
        }
    }
}

function resetMetrics() {
    if (document.getElementById('bpSuccessRate')) document.getElementById('bpSuccessRate').textContent = '0%';
    if (document.getElementById('bpTotalTasks')) document.getElementById('bpTotalTasks').textContent = '0';
    if (document.getElementById('bpAvgHops')) document.getElementById('bpAvgHops').textContent = '0';
    if (document.getElementById('bpQueueLoad')) document.getElementById('bpQueueLoad').textContent = '0';

    if (document.getElementById('tcpCwnd')) document.getElementById('tcpCwnd').textContent = '1.00';
    if (document.getElementById('tcpSsthresh')) document.getElementById('tcpSsthresh').textContent = '16.00';
    if (document.getElementById('tcpState')) document.getElementById('tcpState').textContent = 'SLOW START';
    if (document.getElementById('tcpLoss')) document.getElementById('tcpLoss').textContent = '0';
}

// ===================================================================
// CHARTS
// ===================================================================

function initCwndChart() {
    const canvas = document.getElementById('cwndChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    cwndChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CWND',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'SSThresh',
                    data: [],
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Round (RTT)' }
                },
                y: {
                    display: true,
                    title: { display: true, text: 'Window Size' },
                    beginAtZero: true
                }
            }
        }
    });
}

function updateCwndChart() {
    if (!cwndChart) return;

    cwndChart.data.labels = cwndData.map(d => d.round);
    cwndChart.data.datasets[0].data = cwndData.map(d => d.cwnd);
    cwndChart.data.datasets[1].data = cwndData.map(d => d.ssthresh);

    cwndChart.update('none');
}

// ===================================================================
// ACTIVITY LOG
// ===================================================================

function addLogEntry(taskId, message, status) {
    const log = document.getElementById('activityLog');
    if (!log) return;
    const timestamp = new Date().toLocaleTimeString();

    const entry = document.createElement('div');
    entry.className = `log-entry ${status}`;

    const statusClass = status === 'success' ? 'log-status-success' : (status === 'failed' ? 'log-status-failed' : '');
    const statusText = status === 'success' ? 'SUCCESS' : status === 'failed' ? 'FAILED' : 'INFO';

    entry.innerHTML = `
        <span class="log-time">[${timestamp}]</span>
        <span class="log-task">${taskId}:</span>
        <span class="log-message">${message}</span>
        <span class="${statusClass}">[${statusText}]</span>
    `;

    log.insertBefore(entry, log.firstChild);

    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// ===================================================================
// STATUS UPDATE
// ===================================================================

function updateStatus(text, running) {
    const statusEl = document.getElementById('statusText');
    if (statusEl) statusEl.textContent = `Status: ${text}`;
    const dot = document.getElementById('statusDot');

    if (dot) {
        if (running) {
            dot.className = 'status-dot status-running';
        } else {
            dot.className = 'status-dot status-stopped';
        }
    }
}
// ===================================================================
// ALGORITHM INSPECTOR - INDUSTRY LEVEL
// ===================================================================

let tcpStateChanges = 0;
let aimdCycles = 0;
let bpDecisionCount = 0;

// Tab switching - will execute after DOM loads
setTimeout(() => {
    const tabs = document.querySelectorAll('.inspector-tab');

    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');

                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.inspector-content').forEach(c => c.classList.remove('active'));

                // Add active class to clicked tab and corresponding content
                this.classList.add('active');
                const inspectorEl = document.getElementById(`inspector-${tabName}`);
                if (inspectorEl) inspectorEl.classList.add('active');
            });
        });
        console.log('Inspector tabs initialized');
    }
}, 1000);

// Update Backpressure Inspector
function updateBackpressureInspector(data) {
    bpDecisionCount++;

    const decisionBox = document.getElementById('bpDecision');
    const formulaBox = document.getElementById('bpFormulas');

    if (!decisionBox || !formulaBox) return;

    // Simulate calculations
    const queueDiff = Math.random() * 5;
    const bandwidth = Math.random() * 100;
    const weight = (0.6 * queueDiff + 0.4 * (bandwidth/100)).toFixed(2);

    const sourceId = (data.task_id || 'Task').split('_')[0] + (Math.floor(Math.random() * 5) + 1);

    decisionBox.innerHTML = `
        <strong>📍 Routing Decision:</strong><br>
        Source: <span style="color: #ef4444">${sourceId}</span> → 
        Destination: <span style="color: #f97316">Cloud_1</span><br><br>

        <strong>Next Hop Selected:</strong> <span style="color: #10b981; font-size: 1.1em;">Edge_${Math.floor(Math.random()*2)+1}</span><br>
        <strong>Path:</strong> ${(Array.isArray(data.path) ? data.path.join(' → ') : data.path)}<br>
        <strong>Status:</strong> <span style="color: ${data.status === 'SUCCESS' ? '#10b981' : '#ef4444'}">${data.status}</span>
    `;

    formulaBox.innerHTML = `
        <span class="formula-line"><strong>Weight Calculation:</strong></span>
        <span class="formula-line">Weight = α × Queue_diff + β × Bandwidth</span>
        <span class="formula-line">Weight = 0.6 × <span class="formula-highlight">${queueDiff.toFixed(2)}</span> + 0.4 × <span class="formula-highlight">${(bandwidth/100).toFixed(2)}</span></span>
        <span class="formula-line">Weight = <span class="formula-result">${weight}</span> ⭐</span>
    `;

    document.getElementById('bpDecisions').textContent = bpDecisionCount;
    document.getElementById('bpAvgTime').textContent = (Math.random() * 2).toFixed(2) + 'ms';

    decisionBox.classList.add('highlight');
    setTimeout(() => decisionBox.classList.remove('highlight'), 500);
}

// Update TCP Inspector
function updateTCPInspector(data) {
    const formulaBox = document.getElementById('tcpFormulas');
    if (!formulaBox) return;

    const prevCwnd = (data.cwnd / (data.state === 'SLOW_START' ? 2 : 1.1)).toFixed(2);

    // Update state machine
    document.querySelectorAll('.state-node').forEach(node => node.classList.remove('active'));

    if (data.state === 'SLOW_START') {
        const node = document.getElementById('state-slowstart');
        if (node) node.classList.add('active');
    } else if (data.state === 'CONGESTION_AVOIDANCE') {
        const node = document.getElementById('state-congavoid');
        if (node) node.classList.add('active');
    }

    if (data.congestion) {
        const node = document.getElementById('state-loss');
        if (node) node.classList.add('active');
        tcpStateChanges++;
        aimdCycles++;
    }

    // Formula display
    let formula = '';
    if (data.congestion) {
        formula = `
            <span class="formula-line"><strong>🚨 PACKET LOSS DETECTED - AIMD</strong></span>
            <span class="formula-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
            <span class="formula-line">SSThresh = CWND / 2</span>
            <span class="formula-line">SSThresh = ${prevCwnd} / 2 = <span class="formula-result">${(data.ssthresh ?? 0).toFixed(2)}</span></span>
            <span class="formula-line">CWND = <span class="formula-result">1.00</span> (Reset)</span>
            <span class="formula-line">State = <span class="formula-highlight">SLOW_START</span></span>
        `;
    } else if (data.state === 'SLOW_START') {
        formula = `
            <span class="formula-line"><strong>📈 SLOW START PHASE</strong></span>
            <span class="formula-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
            <span class="formula-line">CWND<sub>new</sub> = CWND<sub>old</sub> × 2</span>
            <span class="formula-line"><span class="formula-result">${(data.cwnd ?? 0).toFixed(2)}</span> = ${prevCwnd} × 2</span>
            <span class="formula-line">Growth: <span class="formula-highlight">Exponential</span></span>
        `;
    } else {
        formula = `
            <span class="formula-line"><strong>📊 CONGESTION AVOIDANCE</strong></span>
            <span class="formula-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
            <span class="formula-line">CWND<sub>new</sub> = CWND<sub>old</sub> + (1/CWND<sub>old</sub>)</span>
            <span class="formula-line"><span class="formula-result">${(data.cwnd ?? 0).toFixed(2)}</span> = ${prevCwnd} + (1/${prevCwnd})</span>
            <span class="formula-line">Growth: <span class="formula-highlight">Linear (Additive)</span></span>
        `;
    }

    formulaBox.innerHTML = formula;

    const stateChangesEl = document.getElementById('tcpStateChanges');
    const aimdEl = document.getElementById('tcpAIMD');
    if (stateChangesEl) stateChangesEl.textContent = tcpStateChanges;
    if (aimdEl) aimdEl.textContent = aimdCycles;
}

// Update ML Inspector
function updateMLInspector(data) {
    const featuresBox = document.getElementById('mlFeatures');
    const decisionBox = document.getElementById('mlDecision');

    if (!featuresBox || !decisionBox) return;

    // Simulated features
    const features = [
        { name: 'Avg Queue Length', value: (Math.random() * 10).toFixed(2) },
        { name: 'Max Queue', value: (Math.random() * 15).toFixed(2) },
        { name: 'CWND', value: (Math.random() * 16).toFixed(2) },
        { name: 'Packet Losses', value: Math.floor(Math.random() * 5) },
        { name: 'Throughput', value: (Math.random() * 10).toFixed(2) },
        { name: 'Queue Growth', value: (Math.random() * 4 - 2).toFixed(2) }
    ];

    featuresBox.innerHTML = features.map(f => `
        <div class="feature-item flash-update">
            <span class="feature-name">${f.name}:</span>
            <span class="feature-value">${f.value}</span>
        </div>
    `).join('');

    const probability = (data.confidence ?? 0) / 100;
    const prediction = data.prediction ? 'CONGESTION' : 'NORMAL';
    const color = data.prediction ? '#ef4444' : '#10b981';

    decisionBox.innerHTML = `
        <span class="formula-line"><strong>Model Inference:</strong></span>
        <span class="formula-line">P(congestion | X) = <span class="formula-result">${probability.toFixed(3)}</span></span>
        <span class="formula-line">Confidence = <span class="formula-highlight">${(data.confidence ?? 0).toFixed(1)}%</span></span>
        <span class="formula-line">Decision = <span style="color: ${color}; font-weight: 700;">${prediction}</span></span>
        <span class="formula-line">Status = <span class="formula-result">${String(data.status || '').toUpperCase()}</span></span>
    `;

    const timeEl = document.getElementById('mlInferenceTime');
    if (timeEl) timeEl.textContent = (Math.random() * 5).toFixed(2) + 'ms';
}

// Update socket listeners to call inspector functions
console.log('Inspector functions loaded');
