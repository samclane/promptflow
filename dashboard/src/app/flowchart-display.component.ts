import { Component, ElementRef, AfterViewInit } from '@angular/core';
import { switchMap, map, take } from 'rxjs/operators';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';
import * as mermaid from 'mermaid';
import { of } from 'rxjs';

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
      switchMap((id) => this.flowchartService.getMermaidString(id)),
      switchMap((mermaidString) => {
        mermaid.default.initialize({
          startOnLoad: false,
          theme: 'base',
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#fff',
            secondaryColor: '#fff',
            edgeBorderColor: '#3b82f6',
            nodeTextColor: '#000',
          }
        });
        let element = document.querySelector('#diagram');
        if (element) {
          console.log(mermaidString);
          return mermaid.default.render('graphDiv', mermaidString, element);
        }
        return of(null);
      })
    ).subscribe(
      (result) => {
        if (result) {
          const { svg, bindFunctions } = result;
          let element = document.querySelector('#diagram');
          if (element) {
            const container = document.createElement('div');
            container.innerHTML = svg;
            const svgElement = container.querySelector('svg');
            if (svgElement) {
              svgElement.style.margin = 'auto';
            }
            element.innerHTML = container.innerHTML;
            bindFunctions?.(element);
          }
        }
      }
    );
  }
  
  
  
}
