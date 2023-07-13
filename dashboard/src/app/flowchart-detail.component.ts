import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NodeService } from './node.service';
import { FlowchartService } from './flowchart.service';

@Component({
  selector: 'app-flowchart-detail',
  templateUrl: './flowchart-detail.component.html',
  styleUrls: ['./flowchart-detail.component.css']
})
export class FlowchartDetailComponent implements OnInit {
  flowchartId?: string;

  constructor(
    private route: ActivatedRoute,
    private nodeService: NodeService,
    private flowchartService: FlowchartService
  ) { }

  ngOnInit(): void {
    this.flowchartId = this.route.snapshot.paramMap.get('id') as string;
    // Load the flowchart...
  }

  addNode(nodeType: string): void {
    if (this.flowchartId) {
        this.nodeService.addNode(this.flowchartId, nodeType).subscribe(node => {
        // Add the node to the flowchart...
        });
    }
  }

  removeNode(nodeId: string): void {
    if (this.flowchartId) {
        this.nodeService.removeNode(this.flowchartId, nodeId).subscribe(() => {
          // Remove the node from the flowchart...
        });
    }
  }

  runFlowchart(): void {
    if (this.flowchartId) {
        this.flowchartService.runFlowchart(this.flowchartId).subscribe(() => {
        // Handle successful execution...
        });
    }
  }}
