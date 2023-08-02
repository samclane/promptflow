import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobsService } from './jobs.service';
import { map, switchMap, tap } from 'rxjs/operators';
import { combineLatest, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { InputResponse } from './input-response';

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.css']
})
export class JobDetailComponent {
  constructor(
    private route: ActivatedRoute,
    private jobsService: JobsService,
    private http: HttpClient,
  ) { }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }
  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }
      
  private readonly jobId$ = this.route.params.pipe(
    map((x) => x['id']),
  );

  public readonly job$ = this.jobId$.pipe(
    switchMap(
      (x) => this.jobsService.getJob(x).pipe(
        map((x) => x.valueOrUndefined()),
      )
    ),
  );

  public readonly vm$ = combineLatest({
    jobId: this.jobId$,
    job: this.job$,
  });

  public input: string = '';

  public get onSubmit$(): Observable<InputResponse> {
    return this.jobId$.pipe(
      switchMap(id =>
        this.http.post<InputResponse>(this.buildUrl('/jobs/' + id + '/input'), {'input': this.input})
      ),
      tap(() => window.location.reload()),
    );
  }
  
  public onSubmit(): void {
    this.onSubmit$.subscribe();
  }
}
