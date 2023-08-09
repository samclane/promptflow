import { Component, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FlowchartService } from './flowchart.service';
import { filter, share, startWith, switchMap, tap } from 'rxjs/operators';
import {JobListComponent} from './job-list.component';
import {combineLatest, merge, Subject} from 'rxjs';

@Component({
  selector: 'app-flowchart-detail',
  templateUrl: './flowchart-detail.component.html',
  styleUrls: ['./flowchart-detail.component.css']
})
export class FlowchartDetailComponent {
  @ViewChild(JobListComponent) jobListComponent?: JobListComponent;

  constructor(
    private route: ActivatedRoute,
    private flowchartService: FlowchartService
  ) {
   }

  public readonly id = this.route.snapshot.paramMap.get('id');
  private readonly flowchart$ = this.flowchartService.getFlowchart(this.id ?? '');

  private readonly flowChartActionSource = new Subject<'RUN' | 'STOP'>();
  private readonly flowChartAction$ = this.flowChartActionSource.pipe(share())

  private readonly flowChartActionProcess$ = merge(
    this.flowChartAction$.pipe(
      filter((x) => x === 'RUN'),
      switchMap(() => this.flowchartService.runFlowchart(this.id ?? ''))
    ),
    this.flowChartAction$.pipe(
      filter((x) => x === 'STOP'),
      switchMap(() => this.flowchartService.stopFlowchart(this.id ?? ''))
    )
  ).pipe(
    tap(() => this.jobListComponent?.getJobs()),
    startWith(null)
  );

  public readonly vm$ = combineLatest({
    flowChartActionProcess: this.flowChartActionProcess$,
    flowchart: this.flowchart$
  }); 

  runFlowchart(): void {
    this.flowChartActionSource.next('RUN');
  }

  stopFlowchart(): void {
    this.flowChartActionSource.next('STOP');
  }
}
