import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { LogsService } from './logs.service';
import { Subscription, timer, Subject } from 'rxjs';
import { switchMap, retry } from 'rxjs/operators';

@Component({
  selector: 'app-job-logs',
  templateUrl: './job-logs.component.html',
  styleUrls: ['./job-logs.component.css']
})
export class JobLogsComponent implements OnInit, OnDestroy {
  @Input() jobId!: string;
  logs = new Subject<string>();
  private logSubscription?: Subscription;

  constructor(private logsService: LogsService) { }

  ngOnInit(): void {
    this.logSubscription = timer(0, 1000).pipe(
      switchMap(() => this.logsService.getLogs(this.jobId)),
      retry()
    ).subscribe(logs => {
      this.logs.next(logs.logs.map((x) => x.message).join('\n'));
    });
  }

  ngOnDestroy(): void {
    if (this.logSubscription) {
      this.logSubscription.unsubscribe();
    }
    this.logs.complete();
  }
}
