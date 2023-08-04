import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { LogsService } from './logs.service';
import { Subscription, timer } from 'rxjs';
import { switchMap, retry } from 'rxjs/operators';

@Component({
  selector: 'app-job-logs',
  templateUrl: './job-logs.component.html',
  styleUrls: ['./job-logs.component.css']
})
export class JobLogsComponent implements OnInit, OnDestroy {
  @Input() jobId!: string;
  logs: string = '';
  private logSubscription?: Subscription;

  constructor(private logsService: LogsService) { }

  ngOnInit(): void {
    this.logSubscription = timer(0, 1000).pipe(
      switchMap(() => this.logsService.getLogs(this.jobId)),
      retry()
    ).subscribe(logs => {
      this.logs = '';
      for (let log of logs.logs) {
        this.logs += log.message + '\n';
      }
    });
  }

  ngOnDestroy(): void {
    if (this.logSubscription) {
      this.logSubscription.unsubscribe();
    }
  }
}
