const flowchartId = window.localStorage.getItem('flowchartId');
const endpoint = "http://localhost:8000/flowcharts";  // Change the URL to match your API server
let canvas = document.getElementById("flowchartCanvas");
let ctx = canvas.getContext("2d");
let flowchart = null;

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
let hoveredNode = null;


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
    const radius = node == hoveredNode ? 55 : 50;  // Set a fixed radius value

    // Create gradient
    let grd = ctx.createLinearGradient(node.center_x, node.center_y - radius, node.center_x, node.center_y + radius);
    grd.addColorStop(0, node == hoveredNode ? '#b4d273' : '#8BC34A');
    grd.addColorStop(1, '#6C9A1F');
    
    // Draw the circular node
    ctx.arc(node.center_x, node.center_y, radius, 0, 2 * Math.PI, false);

    // Set gradient as fill style
    ctx.fillStyle = grd;
    ctx.fill();
    
    // Add shadow for 3D effect
    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = 15;
    ctx.shadowOffsetX = 5;
    ctx.shadowOffsetY = 5;
    
    // Stroke
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#1C1E26';
    ctx.stroke();

    // Reset shadow for text drawing
    ctx.shadowColor = 'transparent';

    // Text
    ctx.font = "20px 'Segoe UI', Arial, sans-serif"; // Using a more modern font
    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.textBaseline = 'middle'; // To align the text in the middle vertically
    ctx.fillText(node.label, node.center_x, node.center_y);
}



function drawNodes() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate( window.innerWidth / 2, window.innerHeight / 2 )
    ctx.scale(cameraZoom, cameraZoom)
    ctx.translate( -window.innerWidth / 2 + cameraOffset.x, -window.innerHeight / 2 + cameraOffset.y )
    if (flowchart === null) return;
    if (flowchart.nodes === null) return;
    // Draw all the nodes
    flowchart.nodes.forEach((node) => {
        drawNode(node);
    });
    // Reset the transform to the identity matrix
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    requestAnimationFrame(drawNodes);
}

function drawArrowhead(ctx, from, to, radius, fill, stroke) {
    let x_center = to.center_x;
    let y_center = to.center_y;

    let angle;
    let x;
    let y;

    ctx.beginPath();

    angle = Math.atan2(to.center_y - from.center_y, to.center_x - from.center_x)
    x = radius * Math.cos(angle) + x_center;
    y = radius * Math.sin(angle) + y_center;

    ctx.moveTo(x, y);

    angle += (1/3)*(2*Math.PI);
    x = radius * Math.cos(angle) + x_center;
    y = radius * Math.sin(angle) + y_center;

    ctx.lineTo(x, y);

    angle += (1/3)*(2*Math.PI);
    x = radius * Math.cos(angle) + x_center;
    y = radius * Math.sin(angle) + y_center;

    ctx.lineTo(x, y);
    ctx.closePath();

    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = stroke;
    ctx.stroke();
}

function drawConnectors() {
    ctx.translate( window.innerWidth / 2, window.innerHeight / 2 )
    ctx.scale(cameraZoom, cameraZoom)
    ctx.translate( -window.innerWidth / 2 + cameraOffset.x, -window.innerHeight / 2 + cameraOffset.y )
    if (flowchart === null) return;
    if (flowchart.connectors === null) return;
    flowchart.connectors.forEach((connector) => {
        const startNode = flowchart.nodes.find((node) => node.id === connector.node1);
        const endNode = flowchart.nodes.find((node) => node.id === connector.node2);
        ctx.beginPath();
        ctx.moveTo(startNode.center_x, startNode.center_y);
        ctx.lineTo(endNode.center_x, endNode.center_y);
        ctx.lineWidth = 5;
        ctx.strokeStyle = '#f5f5f5';
        ctx.stroke();
        drawArrowhead(ctx, startNode, endNode, 20, '#f5f5f5', '#f5f5f5');
    });
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    requestAnimationFrame(drawConnectors);
}

function drawAll() {
    drawNodes();
    drawConnectors();
}

axios.get(`${endpoint}/${flowchartId}`)
.then((response) => {
    flowchart = response.data.flowchart;

    drawAll();
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
    const mousePos = getMousePos(canvas, e);
    hoveredNode = null;
    if (flowchart === null) return;
    for (let i = 0; i < flowchart.nodes.length; i++) {

        if (isHovering(mousePos, flowchart.nodes[i])) {

            hoveredNode = flowchart.nodes[i];
            break;
        }
    }
    drawAll();
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
            cameraZoom = zoomFactor*lastZoom
        }
        
        cameraZoom = Math.min( cameraZoom, MAX_ZOOM )
        cameraZoom = Math.max( cameraZoom, MIN_ZOOM )
        
    }
    drawAll();
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



function getMousePos(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

function isHovering(mousePos, node) {
    // adjust mouse position to account for camera offset and zoom
    const distX = mousePos.x - node.center_x - cameraOffset.x; 
    const distY = mousePos.y - node.center_y - cameraOffset.y;
    return Math.sqrt(distX * distX + distY * distY) < 50; // 50 is the radius of the node
}
