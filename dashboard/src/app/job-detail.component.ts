import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobsService } from './jobs.service';
import { map, switchMap } from 'rxjs/operators';
import {combineLatest} from 'rxjs';

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.css']
})
export class JobDetailComponent {
  constructor(
    private route: ActivatedRoute,
    private jobsService: JobsService
  ) { }

  private readonly jobId$ = this.route.params.pipe(
    map((x) => x['id']),
  );

  public readonly job$ = this.jobId$.pipe(
    switchMap(
      (x) => this.jobsService.getJob(x).pipe(
        map((x) => x.valueOrUndefined()),
      )
    ),
  )

  public readonly vm$ = combineLatest({
    jobId: this.jobId$,
    job: this.job$
  });
}
