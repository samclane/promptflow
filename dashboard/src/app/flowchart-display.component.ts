import { Component, OnInit, Input, AfterViewInit } from '@angular/core';
import { Flowchart } from './flowchart';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';
import { take } from 'rxjs/operators';
import mermaid from 'mermaid';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent implements OnInit {
  flowchart!: Flowchart
  config = {
    startOnLoad: false,
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true
    }
  };
  id!: string;

  constructor(private route: ActivatedRoute, private flowchartService: FlowchartService) {
    this.id = this.route.snapshot.paramMap.get('id')!;
  }

  ngOnInit(): void {
    this.flowchartService.getFlowchart(this.id).pipe(take(1)).subscribe(flowchart => {
      this.flowchart = flowchart;
      mermaid.initialize(this.config);
      const graphDefinition = this.generateMermaidDiagram(this.flowchart);
      mermaid.render("graphDiv", graphDefinition);
    });
  }

  generateMermaidDiagram(flowchart: Flowchart): string {
    let diagram = 'graph TB\n';
    flowchart.nodes.forEach(node => {
      diagram += `${node.id}("${node.label}")\n`;
    });
    flowchart.branches.forEach(branch => {
      diagram += `${branch.prev} --> ${branch.next}\n`;
    });
    console.log(diagram);
    return diagram;
  }
}
