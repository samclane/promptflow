import { Component, OnInit } from '@angular/core';
import { FlowchartService } from './flowchart.service';

@Component({
  selector: 'app-flowchart-list',
  templateUrl: './flowchart-list.component.html',
  styleUrls: ['./flowchart-list.component.css']
})
export class FlowchartListComponent implements OnInit {
  flowcharts: any[] = [];

  constructor(private flowchartService: FlowchartService) { }

  ngOnInit(): void {
    this.getFlowcharts();
  }

  getFlowcharts(): void {
    this.flowchartService.getFlowcharts().subscribe(flowcharts => this.flowcharts = flowcharts);
  }

  deleteFlowchart(id: string): void {
    this.flowchartService.deleteFlowchart(id).subscribe(() => {
      this.flowcharts = this.flowcharts.filter(flowchart => flowchart.id !== id);
    });
  }

}
