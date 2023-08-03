import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, catchError, of } from 'rxjs';
import { Job, JobLog } from './job';
import {environment} from 'src/environments/environment';
import {maybe, Maybe, none} from 'typescript-monads';

@Injectable({
  providedIn: 'root'
})
export class JobsService {
  constructor(private http: HttpClient) { }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(path: string): string {
    return `${this.apiUrl}${path}`;
  }

  getJobs(): Observable<Job[]> {
    return this.http.get<Job[]>(this.buildUrl('/jobs'));
  }

  getJobsByGraphId(graphId: string): Observable<Job[]> {
    return this.http.get<Job[]>(this.buildUrl('/jobs'), { params: { graph_uid: graphId } });
  }

  getJob(jobId: string): Observable<Maybe<Job>> {
    return this.http.get<Job>(this.buildUrl(`/jobs/${jobId}`)).pipe(
      map((x) => maybe<Job>(x)),
      catchError(() => of(none<Job>())),
    )
  }

  getJobLogs(jobId: string): Observable<JobLog> {
    return this.http.get<JobLog>(this.buildUrl(`/jobs/${jobId}/logs`));
  }

  createJob(jobData: Record<string, unknown>): Observable<Job> {
    return this.http.post<Job>(this.buildUrl(`/jobs`), jobData);
  }

  getJobCount(): Observable<number> {
    return this.getJobs().pipe(
      map(jobs => jobs.length)
    );
  }

  submitInput(jobId: string, input: string): Observable<unknown> {
    return this.http.post(this.buildUrl(`/jobs/${jobId}/input`), { 'input': input });
  }
}
