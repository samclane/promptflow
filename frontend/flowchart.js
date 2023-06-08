const axios = require('axios');
const fabric = require('fabric').fabric;
const { from, Observable } = require('rxjs');
const { throttleTime } = require('rxjs/operators');

const endpoint = "http://localhost:8000/flowcharts";

const canvas = new fabric.Canvas('flowchartCanvas', {
    width: 800,
    height: 600,
    backgroundColor: '#3B4048',
    selectionColor: 'blue',
    selectionLineWidth: 2,
    preserveObjectStacking: true
});

const flowchartId = window.localStorage.getItem('flowchartId');
const flowchart$ = from(axios.get(`${endpoint}/${flowchartId}`));

flowchart$.subscribe((response) => {
    const flowchart = response.data.flowchart;

    flowchart.nodes.forEach((node) => {
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
            type: 'node'
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
            selectable: true,
            hoverCursor: 'pointer',
            id: node.id,
            type: 'node'
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
        group.id = node.id;
        canvas.add(group);
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
    if (target.type === 'node') {
        // darken and make node border visible, increase size
        target.item(0).set({ 'fill': '#a3c162', 'stroke': '#000000', 'width': 110, 'height': 110 });
        canvas.renderAll();
    }
    else if (target.type === 'connector') {
        // make connector thicker
        target.set({ 'strokeWidth': 4 });
        canvas.renderAll();
    }
});

const mouseOut$ = fromFabricEvent(canvas, 'mouse:out');
mouseOut$.subscribe((event) => {
    const target = event.target;
    if (!target) return;
    if (target.type === 'node') {
        // lighten and make node border invisible, decrease size
        target.item(0).set({ 'fill': '#b4d273', 'stroke': '#2e2e2e', 'width': 100, 'height': 100 });
        canvas.renderAll();
    }
    else if (target.type === 'connector') {
        // make connector thinner
        target.set({ 'strokeWidth': 2 });
        canvas.renderAll();
    }
});
