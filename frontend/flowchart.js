// Replace with the ID of the flowchart you want to display
const flowchartId = window.localStorage.getItem('flowchartId');
const endpoint = "http://localhost:8000/flowcharts";  // Change the URL to match your API server
let canvas = document.getElementById("flowchartCanvas");
let ctx = canvas.getContext("2d");
let flowchart = null;

const scaleFactor = window.devicePixelRatio;
canvas.width = canvas.clientWidth * scaleFactor;
canvas.height = canvas.clientHeight * scaleFactor;
ctx.scale(scaleFactor, scaleFactor);


function drawNode(nodeData) {
    let canvas = document.getElementById("flowchartCanvas");
    let ctx = canvas.getContext("2d");

    // Set styles for the node
    ctx.fillStyle = "#6c757d";  // or any color you want for the node
    ctx.font = '20px Arial';  // adjust size and font as you prefer

    // Calculate position and dimensions of the node
    // get the scale of the canvas
    let nodeWidth = ctx.measureText(nodeData.label).width;
    let nodeHeight = parseInt(ctx.font);  // you might want to adjust this
    let nodeX = nodeData.center_x;
    let nodeY = nodeData.center_y - nodeHeight;
        // Draw the node rectangle
    ctx.fillRect(nodeX, nodeY, nodeWidth, nodeHeight);

    // Set styles for the text
    ctx.fillStyle = "#f8f9fa";  // or any color you want for the text

    // Draw the text
    ctx.fillText(nodeData.label, nodeData.center_x, nodeData.center_y);
}

function drawNodes() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Draw all the nodes
    flowchart.nodes.forEach((node) => {
        drawNode(node);
    });
}


axios.get(`${endpoint}/${flowchartId}`)
.then((response) => {
    flowchart = response.data.flowchart;

    flowchart.nodes.forEach((node) => {
        drawNode(node);
    });

    const connectorsDiv = document.getElementById('connectors');
    flowchart.connectors.forEach((connector) => {
        const connectorDiv = document.createElement('div');
        connectorDiv.className = 'connector';
        connectorDiv.textContent = JSON.stringify(connector, null, 2);
        connectorsDiv.appendChild(connectorDiv);
    });
})
.catch((error) => {
    console.log(error);
});

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drawNodes();
}

window.addEventListener('resize', resizeCanvas);

resizeCanvas();

