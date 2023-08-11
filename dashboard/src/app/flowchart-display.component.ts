import { Component, ElementRef, AfterViewInit } from '@angular/core';
import * as flowchart from 'flowchart.js';
import { switchMap, map, take } from 'rxjs/operators';
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
      map((x) => {
        console.log(x);
        const parsedFlowchart = flowchart.parse(x.flowchart_js);
        const transformedColorMap = Object.keys(x.color_map).reduce((acc: Record<string, Record<string, string>>, key) => {
          acc[key] = {
            'fill': x.color_map[key]
          };
          return acc;
        }, {});
        return { parsedFlowchart, colorMap: transformedColorMap }; // Return both values as an object
      }),
    ).subscribe(
      (result) => {
        result.parsedFlowchart.drawSVG(
          this.el.nativeElement.querySelector("#diagram"),
          {
            "flowstate": result.colorMap 
          }
        )
      }
    )
  }
  
}
