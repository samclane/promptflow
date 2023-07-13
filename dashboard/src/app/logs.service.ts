// logs.service.ts
import { Injectable } from '@angular/core';
import { WebSocketService } from './web-socket.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LogsService {
  private logs$!: Observable<any>;

  constructor(private webSocketService: WebSocketService) { }

  startLogging(jobId: string): void {
    this.webSocketService.connect(jobId);
    this.logs$ = this.webSocketService.getObservable();
  }

  getLogs(): Observable<any> {
    return this.logs$;
  }
}
