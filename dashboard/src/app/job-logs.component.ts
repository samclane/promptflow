import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { LogsService } from './logs.service';
import { timer, Subject } from 'rxjs';
import { switchMap, retry, takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-job-logs',
  templateUrl: './job-logs.component.html',
  styleUrls: ['./job-logs.component.css']
})
export class JobLogsComponent implements OnInit, OnDestroy {
  @Input() jobId!: string;
  logs = new Subject<string>();
  private unsubscribe = new Subject<void>();

  constructor(private logsService: LogsService) { }

  ngOnInit(): void {
    timer(0, 1000).pipe(
      switchMap(() => this.logsService.getLogs(this.jobId)),
      retry(),
      takeUntil(this.unsubscribe)
    ).subscribe(logs => {
      this.logs.next(logs.logs.map((x) => x.message).join('\n'));
    });
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }
}
