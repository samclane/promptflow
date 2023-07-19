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
    this.flowchartService.getFlowchartSvg(this.id).pipe(take(1)).subscribe(svg => {
      const div = document.getElementById('flowchart-display')!;
      div.innerHTML = svg;
    }
    );
  }
}
