import { Component } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';
import { map, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent {

  constructor(private route: ActivatedRoute, private flowchartService: FlowchartService) {}

  public readonly base64Img$ = this.route.params.pipe(
    map((x) => x['id']),
    switchMap((id) => this.flowchartService.getFlowchartPng(id)),
    map((x) => `data:img/png;base64,${x}`)
  )
}
