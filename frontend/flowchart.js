const axios = require('axios');
const fabric = require('fabric').fabric;
const { from, Observable } = require('rxjs');
const { throttleTime, debounceTime } = require('rxjs/operators');

const endpoint = "http://localhost:8000";

const canvas = new fabric.Canvas('flowchartCanvas', {
    width: 800,
    height: 600,
    backgroundColor: '#3B4048',
    selectionColor: '#2e2e2e',
    selectionLineWidth: 2,
    preserveObjectStacking: true
});

const flowchartId = window.localStorage.getItem('flowchartId');
const flowchart$ = from(axios.get(`${endpoint}/flowcharts/${flowchartId}`));

function createNode(node) {
    const rect = new fabric.Rect({
        left: node.center_x,
        top: node.center_y,
        width: 100,
        height: 100,
        fill: '#b4d273',
        stroke: '#2e2e2e',
        strokeWidth: 2,
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: node.id,
        type: 'node-rect'
    });

    const text = new fabric.Text(node.label, {
        left: node.center_x,
        top: node.center_y,
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#2e2e2e',
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: false,
        hoverCursor: 'pointer',
        id: node.id,
        type: 'node-text'
    });

    const group = new fabric.Group([rect, text], {
        left: node.center_x,
        top: node.center_y,
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: true,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: node.id,
        type: 'node'
    });
    canvas.add(group);
}

function drawButtons(target) {
    const buttonWidth = 20;
    const buttonHeight = 20;
    const buttonOffset = 5;

    const deleteButton = new fabric.Rect({
        left: target.left + target.width / 2 - buttonWidth / 2,
        top: target.top - target.height / 2 - buttonHeight / 2 - buttonOffset,
        width: buttonWidth,
        height: buttonHeight,
        fill: '#2e2e2e',
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: target.id,
        type: 'node-delete-button'
    });

    const deleteButtonText = new fabric.Text('X', {
        left: target.left + target.width / 2 - buttonWidth / 2,
        top: target.top - target.height / 2 - buttonHeight / 2 - buttonOffset,
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#b4d273',
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: target.id,
        type: 'node-delete-button-text'
    });

    const connectorButton = new fabric.Rect({
        left: target.left + target.width / 2 - buttonWidth / 2,
        top: target.top + target.height / 2 + buttonHeight / 2 + buttonOffset,
        width: buttonWidth,
        height: buttonHeight,
        fill: '#2e2e2e',
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: target.id,
        type: 'node-connector-button'
    });

    const connectorButtonText = new fabric.Text('+', {
        left: target.left + target.width / 2 - buttonWidth / 2,
        top: target.top + target.height / 2 + buttonHeight / 2 + buttonOffset,
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#b4d273',
        originX: 'center',
        originY: 'center',
        centeredRotation: true,
        hasControls: false,
        hasBorders: false,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockUniScaling: true,
        selectable: true,
        hoverCursor: 'pointer',
        id: target.id,
        type: 'node-connector-button-text'
    });

    canvas.add(deleteButton);
    canvas.add(deleteButtonText);
    canvas.add(connectorButton);
    canvas.add(connectorButtonText);
}

function hideButtons() {
    canvas.getObjects('node-connector-button').forEach((button) => {
        button.visible = false;
    });
    canvas.getObjects('node-delete-button').forEach((button) => {
        button.visible = false;
    });
    canvas.getObjects('node-connector-button-text').forEach((button) => {
        button.visible = false;
    });
    canvas.getObjects('node-delete-button-text').forEach((button) => {
        button.visible = false;
    });
    canvas.renderAll();
}

flowchart$.subscribe((response) => {
    const flowchart = response.data.flowchart;

    flowchart.nodes.forEach((node) => {
        createNode(node);
    });

    flowchart.connectors.forEach((connector) => {
        start_node = flowchart.nodes.find(node => node.id === connector.node1);
        end_node = flowchart.nodes.find(node => node.id === connector.node2);
        const line = new fabric.Line([start_node.center_x, start_node.center_y, end_node.center_x, end_node.center_y], {
            stroke: '#2e2e2e',
            strokeWidth: 2,
            selectable: true,
            evented: true,
            id: connector.id,
            type: 'connector'
        });
        line.node1 = connector.node1;
        line.node2 = connector.node2;
        canvas.add(line);
        const angle = Math.atan2(connector.node2.top - connector.node1.top, connector.node2.left - connector.node1.left) * 180 / Math.PI + 90;
        arrowhead = createArrowhead(end_node.center_x, end_node.center_y, angle);
        arrowhead.id = connector.node2.id;
        canvas.add(arrowhead);
    });



});



// Fetch node types from the endpoint and populate the dropdown
const nodeTypes$ = from(axios.get(`${endpoint}/nodes/types`));

nodeTypes$.subscribe((response) => {
    const nodeTypes = response.data['node_types'];
    const nodeTypeDropdown = document.getElementById('node-type-dropdown');
    nodeTypes.forEach((nodeType) => {
        const option = document.createElement('option');
        option.value = nodeType;
        option.text = nodeType;
        nodeTypeDropdown.appendChild(option);
    });
});



function resizeCanvas() {
    canvas.setWidth(window.innerWidth);
    canvas.setHeight(window.innerHeight);
    canvas.renderAll();
}

resizeCanvas();

// Handle window resize events
const resize$ = fromEvent(window, 'resize').pipe(throttleTime(200));
resize$.subscribe(() => {
    resizeCanvas();
});

// Handle mouse wheel events
const mouseWheel$ = fromEvent(canvas.upperCanvasEl, 'wheel');
mouseWheel$.subscribe((event) => {
    const delta = event.deltaY;
    let zoom = canvas.getZoom();
    zoom *= 0.999 ** delta;
    if (zoom > 20) zoom = 20;
    if (zoom < 0.01) zoom = 0.01;
    canvas.zoomToPoint({ x: event.offsetX, y: event.offsetY }, zoom);
    event.preventDefault();
    event.stopPropagation();
});

// Handle mouse move events
const mouseMove$ = fromEvent(canvas.upperCanvasEl, 'mousemove');
mouseMove$.subscribe((event) => {
    if (event.buttons === 4) {
        canvas.relativePan({ x: event.movementX, y: event.movementY });
    }
});

// Define a function to create an observable from a FabricJS event
function fromFabricEvent(target, eventName) {
    return new Observable((subscriber) => {
        target.on(eventName, (event) => subscriber.next(event));
        return () => target.off(eventName);
    });
}

const moving$ = fromFabricEvent(canvas, 'object:moving');

moving$.subscribe((event) => {
    const group = event.target;

    const line = canvas.getObjects('connector').find(line => line.node1 === group.id || line.node2 === group.id);
    const arrowhead = canvas.getObjects('triangle').find(arrowhead => arrowhead.id === line.node2.id);
    if (line) {
        const start_node = canvas.getObjects('node').find(group => group.id === line.node1);
        const end_node = canvas.getObjects('node').find(group => group.id === line.node2);
        line.set({ 'x1': start_node.left, 'y1': start_node.top, 'x2': end_node.left, 'y2': end_node.top });
        arrowhead.set({ 'left': end_node.left, 'top': end_node.top, 'angle': Math.atan2(end_node.top - start_node.top, end_node.left - start_node.left) * 180 / Math.PI + 90 });
    }
});

function createArrowhead(left, top, angle) {
    return new fabric.Triangle({
        left: left,
        top: top,
        originX: 'center',
        originY: 'center',
        hasBorders: false,
        hasControls: false,
        lockMovementX: true,
        lockMovementY: true,
        selectable: true,
        angle: angle,
        width: 20,
        height: 20,
        fill: '#2e2e2e',
        type: 'triangle'
    });
}

const mouseOver$ = fromFabricEvent(canvas, 'mouse:over');
mouseOver$.subscribe((event) => {
    const target = event.target;
    if (!target) return;
    console.log(target);
    if (target.type === 'node') {
        drawButtons(target);
    }
    else if (target.type === 'connector') {
        // make connector thicker
        target.set({ 'strokeWidth': 4 });
        canvas.renderAll();
    }
});

const mouseOut$ = fromFabricEvent(canvas, 'mouse:out');

mouseOut$.pipe(
    debounceTime(300)
).subscribe((event) => {
    const target = event.target;
    if (!target) return;
    if (target.type === 'node') {
        hideButtons();
    } else if (target.type === 'connector') {
        // make connector thinner
        target.set({ 'strokeWidth': 2 });
        canvas.renderAll();
    }
});
const doubleClick$ = fromFabricEvent(canvas, 'mouse:dblclick');
doubleClick$.subscribe((event) => {
    const target = event.target;
    if (!target) return;
    if (target.type === 'node') {
        // get node options from backend
        const nodeOptions = axios.get(`${endpoint}/flowcharts/${flowchartId}/nodes/${target.id}/options`)
            .then(response => {
                const nodeOptions = response.data;
                console.log(nodeOptions);
                if (nodeOptions.editor == null) {
                    // open default editor
                    defaultEditor = window.open('defaultEditor.html', '_blank');
                    defaultEditor.onload = () => {
                        defaultEditor.postMessage(nodeOptions, '*');
                    }
                }
                else {
                    // open custom editor
                    customEditor = window.open(nodeOptions.editor, '_blank');
                    customEditor.onload = () => {
                        customEditor.postMessage(nodeOptions, '*');
                    }
                }
            }
            )
            .catch(error => console.error('Error:', error));
    }
});

// listen for buttons
const runButton = document.getElementById('toolbar-button-run');
const runButtonClick$ = fromEvent(runButton, 'click');
runButtonClick$.subscribe(() => {
    const flowchart = canvas.toJSON();
    console.log(flowchart);
    axios.get(`${endpoint}/flowcharts/${flowchartId}/run`, flowchart)
        .then(response => {
            console.log(response.data);
        })
        .catch(error => console.error('Error:', error));
});

const stopButton = document.getElementById('toolbar-button-stop');
const stopButtonClick$ = fromEvent(stopButton, 'click');
stopButtonClick$.subscribe(() => {
    axios.get(`${endpoint}/flowcharts/${flowchartId}/stop`)
        .then(response => {
            console.log(response.data);
        })
        .catch(error => console.error('Error:', error));
});

const addNodebutton = document.getElementById('toolbar-button-add-node');
const addNodeButtonClick$ = fromEvent(addNodebutton, 'click');
addNodeButtonClick$.subscribe(() => {
    console.log(document.getElementById('node-type-dropdown').value);
    axios.post(`${endpoint}/flowcharts/${flowchartId}/nodes/add`, { 'classname': document.getElementById('node-type-dropdown').value })
        .then(response => {
            const node = response.data['node'];
            createNode(node);
        })
        .catch(error => console.error('Error:', error));
});