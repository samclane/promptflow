import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NodeService } from './node.service';
import { FlowchartService } from './flowchart.service';
import { Flowchart } from './flowchart';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-flowchart-detail',
  templateUrl: './flowchart-detail.component.html',
  styleUrls: ['./flowchart-detail.component.css']
})
export class FlowchartDetailComponent implements OnInit {
  id!: string;
  flowchart?: Flowchart

  constructor(
    private route: ActivatedRoute,
    private nodeService: NodeService,
    private flowchartService: FlowchartService
  ) {
    this.id = this.route.snapshot.paramMap.get('id')!;
   }

  ngOnInit(): void {
    this.flowchartService.getFlowchart(this.id).pipe(take(1)).subscribe(flowchart => {
      this.flowchart = flowchart;
    });
  }

  addNode(nodeType: string): void {
    if (this.id) {
        this.nodeService.addNode(this.id, nodeType).pipe(take(1)).subscribe(node => {
        // Add the node to the flowchart...
        });
    }
  }

  removeNode(nodeId: string): void {
    if (this.id) {
        this.nodeService.removeNode(this.id, nodeId).pipe(take(1)).subscribe(() => {
          // Remove the node from the flowchart...
        });
    }
  }

  runFlowchart(): void {
    if (this.id) {
        this.flowchartService.runFlowchart(this.id).pipe(take(1)).subscribe(() => {
        // Handle successful execution...
        });
    }
  }
    stopFlowchart(): void {
        if (this.id) {
            this.flowchartService.stopFlowchart(this.id).pipe(take(1)).subscribe(() => {
            // Handle successful stop...
            });
        }
    }
  }
