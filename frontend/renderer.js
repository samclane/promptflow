const axios = require('axios');

const endpoint = 'http://localhost:8000';

function refreshFlowchartList() {
    // Make a GET request to the endpoint
    axios.get(endpoint + '/flowcharts')
      .then(response => {
        // Handle the response
        const flowcharts = response.data;
  
        // Generate HTML for the flowcharts
        let flowchartListHTML = flowcharts.map(flowchart => `
          <div class="flowchart">
            <h2>${flowchart.name}</h2>
            <p>ID: ${flowchart.id}</p>
            <p>Nodes: ${flowchart.nodes.length}</p>
            <p>Connectors: ${flowchart.connectors.length}</p>
            <button class="openFlowchartButton" data-flowchart-id="${flowchart.id}">Open</button>
            <button class="deleteFlowchartButton" data-flowchart-id="${flowchart.id}">Delete</button>
          </div>
        `).join('');

        document.getElementById('flowchart-list').innerHTML = flowchartListHTML;
        // Add event listeners to the buttons
        const flowchartButtons = document.getElementsByClassName('openFlowchartButton');
        for (let i = 0; i < flowchartButtons.length; i++) {
            const button = flowchartButtons[i];
            button.addEventListener('click', () => {
                const flowchartId = button.getAttribute('data-flowchart-id');
                openFlowchart(flowchartId);
            });
        }
        const deleteButtons = document.getElementsByClassName('deleteFlowchartButton');
        for (let i = 0; i < deleteButtons.length; i++) {
            const button = deleteButtons[i];
            button.addEventListener('click', () => {
                const flowchartId = button.getAttribute('data-flowchart-id');
                deleteFlowchart(flowchartId);
            });
        }
        // Insert the HTML into the DOM
      })
      .catch(error => {
        // Handle the error
        console.error('Error:', error);
      });
  }
  
refreshFlowchartList();  // Fetch the flowcharts when the application first loads
  
  
document.getElementById('createFlowchartButton').addEventListener('click', async () => {
    const response = await axios.post(endpoint + '/flowcharts/create');
    const flowchart = response.data;
    
    refreshFlowchartList();
    // do something with the new flowchart...
  });

async function openFlowchart(flowchartId) {
    const response = await axios.get(endpoint + '/flowcharts/' + flowchartId);
    const flowchart = response.data;
    // do something with the flowchart...
    refreshFlowchartList();
}

async function deleteFlowchart(flowchartId) {
    const response = await axios.post(endpoint + '/flowcharts/' + flowchartId + '/delete');
    console.log(response.data);
    const flowchart = response.data;
    // do something with the flowchart...
    refreshFlowchartList();
  }