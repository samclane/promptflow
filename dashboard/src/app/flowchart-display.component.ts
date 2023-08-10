import { Component, ElementRef, AfterViewInit } from '@angular/core';
import * as flowchart from 'flowchart.js';
import { switchMap, map } from 'rxjs/operators';
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
      switchMap((id) => this.flowchartService.getFlowchartJsString(id)),
      map((x) => flowchart.parse(x))
    ).subscribe(
      (c) => c.drawSVG(this.el.nativeElement.querySelector("#diagram"))
    )
  }
}
