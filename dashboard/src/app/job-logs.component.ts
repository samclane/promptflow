import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { LogsService } from './logs.service';
import { Subscription, interval } from 'rxjs';
import { startWith, switchMap } from 'rxjs/operators';

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
    this.logSubscription = interval(1000).pipe(
      startWith(0),
      switchMap(() => this.logsService.getLogs(this.jobId))
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
