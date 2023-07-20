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

  id!: string;

  constructor(private route: ActivatedRoute, private flowchartService: FlowchartService) {
    this.id = this.route.snapshot.paramMap.get('id')!;
  }

  ngOnInit(): void {
    this.flowchartService.getFlowchartPng(this.id).pipe(take(1)).subscribe(png => {
      const url = URL.createObjectURL(png);
      const img = document.createElement('img');
      img.src = url;
      let elm = document.getElementById('flowchart-display');
      if (elm) {
        elm.appendChild(img);
      } else {
        console.error('Could not find element with id flowchart-display');
      }
    });
  }
  
  
}
