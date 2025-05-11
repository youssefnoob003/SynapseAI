// Shared chart configuration and utilities
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        }
    }
};

// Color schemes
const colorSchemes = {
    primary: [
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(255, 99, 132)',
        'rgb(255, 205, 86)'
    ],
    severity: {
        high: 'rgb(220, 53, 69)',
        medium: 'rgb(255, 193, 7)',
        low: 'rgb(23, 162, 184)'
    }
};

// Utility function to safely parse JSON from template
function parseTemplateData(jsonString) {
    try {
        return JSON.parse(jsonString.replace(/&quot;/g, '"'));
    } catch (e) {
        console.error('Error parsing data:', e);
        return null;
    }
}

// Create chart with default options
function createChart(ctx, config) {
    return new Chart(ctx, {
        ...config,
        options: {
            ...chartDefaults,
            ...config.options
        }
    });
}

