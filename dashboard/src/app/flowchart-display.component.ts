import { Component, ElementRef, OnInit } from '@angular/core';
import * as flowchart from 'flowchart.js';
import { map } from 'rxjs';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private el: ElementRef,
    private flowchartService: FlowchartService
  ) { }

  private readonly flowchartId$ = this.route.params.pipe(
    map((x) => x['id']),
  );

  ngOnInit(): void {
    this.flowchartId$.subscribe( id =>
      this.flowchartService.getFlowchartJsString(id)
      .subscribe(data => {
        const diagram = flowchart.parse(data.toString());
        console.log(data.toString());
        diagram.drawSVG(this.el.nativeElement.querySelector('#diagram'));
      })
    )

  }
}
