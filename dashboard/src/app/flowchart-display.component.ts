import { Component, ElementRef, AfterViewInit } from '@angular/core';
import * as flowchart from 'flowchart.js';
import { switchMap, map, take, tap } from 'rxjs/operators';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.scss']
})
export class FlowchartDisplayComponent implements AfterViewInit {

  constructor(
    private route: ActivatedRoute,
    private el: ElementRef,
    private flowchartService: FlowchartService
  ) { }

  private readonly flowchartId$ = this.route.params.pipe(
    map((x) => x['id'])
  );

  ngAfterViewInit(): void {
    this.flowchartId$.pipe(
      take(1),
      switchMap((id) => this.flowchartService.getFlowchartJsString(id)),
      map((x) => flowchart.parse(x.flowchart_js)),
      tap((parsedFlowchart) => {
        parsedFlowchart.drawSVG(
          this.el.nativeElement.querySelector("#diagram"),
          {
            "symbols": {
              "condition": {fill: "#4CAF50"},  
              "end": {fill: "#F44336"},       
              "operation": {fill: "#2196F3"},  
              "start": {fill: "#FFC107"},     
              "inputoutput": {fill: "#9C27B0"}, 
              "parallel": {fill: "#00BCD4"},   
              "subroutine": {fill: "#9E9E9E"}, 
            }
          }
        )
      })
    ).subscribe();
  }
}
