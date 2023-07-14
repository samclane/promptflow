import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { LogsService } from './logs.service';
import { WebSocketService } from './web-socket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-job-logs',
  templateUrl: './job-logs.component.html',
  styleUrls: ['./job-logs.component.css']
})
export class JobLogsComponent implements OnInit, OnDestroy {
  @Input() jobId!: string;
  logs: string = '';
  private logSubscription?: Subscription;

  constructor(private logsService: LogsService, private webSocketService: WebSocketService) { }

  ngOnInit(): void {
    this.logsService.startLogging(this.jobId);
    this.logSubscription = this.logsService.getLogs().subscribe(logs => {
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
    this.webSocketService.close();
  }
}
