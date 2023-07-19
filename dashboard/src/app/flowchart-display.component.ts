import { Component, OnInit, Input, AfterViewInit } from '@angular/core';
import { Flowchart } from './flowchart';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent implements OnInit {
  flowchart!: Flowchart

  id!: string;

  constructor(private route: ActivatedRoute, private flowchartService: FlowchartService) {
    this.id = this.route.snapshot.paramMap.get('id')!;
  }

  ngOnInit(): void {
    this.flowchartService.getFlowchart(this.id).pipe(take(1)).subscribe(flowchart => {
      this.flowchart = flowchart;
      console.log(this.flowchart)
    });
  }
}
