import { Component, OnInit } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import { Flowchart } from './flowchart';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-flowchart-list',
  templateUrl: './flowchart-list.component.html',
  styleUrls: ['./flowchart-list.component.css']
})
export class FlowchartListComponent implements OnInit {
  flowcharts: Flowchart[] = [];

  constructor(private flowchartService: FlowchartService) { }

  ngOnInit(): void {
    this.getFlowcharts();
  }

  getFlowcharts(): void {
    this.flowchartService.getFlowcharts().pipe(take(1)).subscribe(flowcharts => this.flowcharts = flowcharts);
  }

  deleteFlowchart(id: string): void {
    this.flowchartService.deleteFlowchart(id).pipe(take(1)).subscribe(() => {
      this.flowcharts = this.flowcharts.filter(flowchart => flowchart.id !== id);
    });
  }

}
