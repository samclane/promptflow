import { ChangeDetectionStrategy, Component } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import {combineLatest} from 'rxjs';

@Component({
  selector: 'app-flowchart-list',
  templateUrl: './flowchart-list.component.html',
  styleUrls: ['./flowchart-list.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartListComponent {
  constructor(private readonly flowchartService: FlowchartService) { }

  private readonly flowcharts$ = this.flowchartService.flowcharts$;

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$
  });

  deleteFlowchart(id: string): void {
    this.flowchartService.deleteFlowchart(id)
  }

}
