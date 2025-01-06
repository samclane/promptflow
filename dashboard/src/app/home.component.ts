import { ChangeDetectionStrategy, Component } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import { JobsService } from './jobs.service';
import { map, catchError} from 'rxjs/operators';
import {combineLatest, of} from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HomeComponent {
  constructor(
    private readonly flowchartService: FlowchartService,
    private readonly jobService: JobsService
  ) { }

  private readonly flowchartCount$ = this.flowchartService.flowchartsCount$;

  private readonly jobs$ = this.jobService.getJobs()
  private readonly jobsCount$ = this.jobs$.pipe(
    map((x) => x.length),
    catchError(() => of(0))
  )

  public readonly vm$ = combineLatest({
    flowchartsCount: this.flowchartCount$,
    jobsCount: this.jobsCount$
  });

}
