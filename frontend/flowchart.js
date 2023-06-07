// Replace with the ID of the flowchart you want to display
const flowchartId = window.localStorage.getItem('flowchartId');
const endpoint = "http://localhost:8000/flowcharts";  // Change the URL to match your API server
let canvas = document.getElementById("flowchartCanvas");
let ctx = canvas.getContext("2d");
let flowchart = null;
let nodes = [];

const scaleFactor = window.devicePixelRatio;
canvas.width = canvas.clientWidth * scaleFactor;
canvas.height = canvas.clientHeight * scaleFactor;
ctx.scale(scaleFactor, scaleFactor);
// pan and zoom based on https://codepen.io/chengarda/pen/wRxoyB
let initialAspectRatio = canvas.width / canvas.height;
let cameraOffset = { x: window.innerWidth/2, y: window.innerHeight/2 }
let cameraZoom = 1
let MAX_ZOOM = 5
let MIN_ZOOM = 0.1
let SCROLL_SENSITIVITY = 0.0005
let isDragging = false
let dragStart = { x: 0, y: 0 }

function getEventLocation(e)
{
    if (e.touches && e.touches.length == 1)
    {
        return { x:e.touches[0].clientX, y: e.touches[0].clientY }
    }
    else if (e.clientX && e.clientY)
    {
        return { x: e.clientX, y: e.clientY }        
    }
}


function drawNode(node) {
    ctx.beginPath();
    const radius = 50;  // Set a fixed radius value
    ctx.arc(node.center_x, node.center_y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = '#00cc00';
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#003300';
    ctx.stroke();
    ctx.font = "20px Arial";
    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.fillText(node.label, node.center_x, node.center_y);
}


function drawNodes() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate( window.innerWidth / 2, window.innerHeight / 2 )
    ctx.scale(cameraZoom, cameraZoom)
    ctx.translate( -window.innerWidth / 2 + cameraOffset.x, -window.innerHeight / 2 + cameraOffset.y )
    // Draw all the nodes
    flowchart.nodes.forEach((node) => {
        drawNode(node);
    });
    // Reset the transform to the identity matrix
    ctx.setTransform(1, 0, 0, 1, 0, 0);
}


axios.get(`${endpoint}/${flowchartId}`)
.then((response) => {
    flowchart = response.data.flowchart;

    drawNodes();

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

let originalCanvasWidth = window.innerWidth;
let originalCanvasHeight = window.innerHeight;

function resizeCanvas() {
    // Resize the canvas
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Redraw nodes, without altering their sizes or aspect ratios
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    nodes.forEach(drawNode);
}

function onPointerDown(e)
{
    isDragging = true
    dragStart.x = getEventLocation(e).x/cameraZoom - cameraOffset.x
    dragStart.y = getEventLocation(e).y/cameraZoom - cameraOffset.y
}

function onPointerUp(e)
{
    isDragging = false
    initialPinchDistance = null
    lastZoom = cameraZoom
}

function onPointerMove(e)
{
    if (isDragging)
    {
        cameraOffset.x = getEventLocation(e).x/cameraZoom - dragStart.x
        cameraOffset.y = getEventLocation(e).y/cameraZoom - dragStart.y
    }
}

function handleTouch(e, singleTouchHandler)
{
    if ( e.touches.length == 1 )
    {
        singleTouchHandler(e)
    }
    else if (e.type == "touchmove" && e.touches.length == 2)
    {
        isDragging = false
        handlePinch(e)
    }
}

let initialPinchDistance = null
let lastZoom = cameraZoom

function handlePinch(e)
{
    e.preventDefault()
    
    let touch1 = { x: e.touches[0].clientX, y: e.touches[0].clientY }
    let touch2 = { x: e.touches[1].clientX, y: e.touches[1].clientY }
    
    // This is distance squared, but no need for an expensive sqrt as it's only used in ratio
    let currentDistance = (touch1.x - touch2.x)**2 + (touch1.y - touch2.y)**2
    
    if (initialPinchDistance == null)
    {
        initialPinchDistance = currentDistance
    }
    else
    {
        adjustZoom( null, currentDistance/initialPinchDistance )
    }
}

function adjustZoom(zoomAmount, zoomFactor)
{
    if (!isDragging)
    {
        if (zoomAmount)
        {
            cameraZoom += zoomAmount
        }
        else if (zoomFactor)
        {
            console.log(zoomFactor)
            cameraZoom = zoomFactor*lastZoom
        }
        
        cameraZoom = Math.min( cameraZoom, MAX_ZOOM )
        cameraZoom = Math.max( cameraZoom, MIN_ZOOM )
        
        console.log(zoomAmount)
    }
    drawNodes();
}


window.addEventListener('resize', resizeCanvas, false);
canvas.addEventListener('mousedown', onPointerDown)
canvas.addEventListener('touchstart', (e) => handleTouch(e, onPointerDown))
canvas.addEventListener('mouseup', onPointerUp)
canvas.addEventListener('touchend',  (e) => handleTouch(e, onPointerUp))
canvas.addEventListener('mousemove', onPointerMove)
canvas.addEventListener('touchmove', (e) => handleTouch(e, onPointerMove))
canvas.addEventListener( 'wheel', (e) => adjustZoom(e.deltaY*SCROLL_SENSITIVITY))

resizeCanvas();