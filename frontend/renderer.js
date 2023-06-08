const { switchMap, tap } = require('rxjs/operators');
const axios = require('axios');

const endpoint = "http://localhost:8000/flowcharts";  // Change the URL to match your API server

const flowchartListElement = document.getElementById('flowchart-list');

function createFlowchartHtml(flowchart) {
    return `
        <div class="flowchart">
            <h2>${flowchart.name}</h2>
            <p>ID: ${flowchart.id}</p>
            <p>Nodes: ${flowchart.nodes.length}</p>
            <p>Connectors: ${flowchart.connectors.length}</p>
            <button class="open-button" data-id="${flowchart.id}">Open</button>
            <button class="delete-button" data-id="${flowchart.id}">Delete</button>
        </div>
    `;
}

function refreshFlowchartList() {
    axios.get(endpoint)
        .then(response => {
            const flowcharts = response.data;
            const flowchartListHTML = flowcharts.map(createFlowchartHtml).join('');
            flowchartListElement.innerHTML = flowchartListHTML;
        })
        .catch(error => console.error('Error:', error));
}

refreshFlowchartList();

const deleteButtonClick$ = fromEvent(flowchartListElement, 'click')
    .pipe(
        tap((event) => {
            if (event.target.classList.contains('delete-button')) {
                const flowchartId = event.target.getAttribute('data-id');
                axios.post(`${endpoint}/${flowchartId}/delete`)
                    .then(refreshFlowchartList)
                    .catch(error => console.error('Error:', error));
            }
        })
    );

deleteButtonClick$.subscribe();

const openButtonClick$ = fromEvent(flowchartListElement, 'click')
    .pipe(
        tap((event) => {
            if (event.target.classList.contains('open-button')) {
                const flowchartId = event.target.getAttribute('data-id');
                data = axios.get(`${endpoint}/${flowchartId}`)
                    .then(response => {
                        const flowchart = response.data;
                        const flowchartData = JSON.stringify(flowchart);
                        window.localStorage.setItem('flowchartId', flowchartId);
                        window.location.href = 'flowchart.html';
                    }
                    )
                    .catch(error => console.error('Error:', error));
            }
        })
    );

openButtonClick$.subscribe();

const createFlowchartButton = document.getElementById('create-flowchart-button');

const createFlowchartClick$ = fromEvent(createFlowchartButton, 'click')
    .pipe(
        switchMap(() => {
            return axios.post(endpoint + '/create');
        }
        ),
        tap(() => {
            refreshFlowchartList();
        }
        )
    );

createFlowchartClick$.subscribe();