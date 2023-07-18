import { Component, OnInit, Input, AfterViewInit } from '@angular/core';
import { Flowchart } from './flowchart';
import mermaid from 'mermaid';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent implements AfterViewInit {
  @Input() flowchart!: Flowchart;

  constructor() { }

  ngAfterViewInit() {
    if (!this.flowchart) {
      return;
    }
    mermaid.initialize({ startOnLoad: true });
    mermaid.render('graphDiv', this.generateMermaidDiagram(this.flowchart));
  }

  generateMermaidDiagram(flowchart: Flowchart): string {
    let diagram = 'graph TB\n';
    flowchart.nodes.forEach(node => {
      diagram += `${node.id}("${node.label}")\n`;
    });
    flowchart.branches.forEach(branch => {
      diagram += `${branch.prev} --> ${branch.next}\n`;
    });
    return diagram;
  }
}
