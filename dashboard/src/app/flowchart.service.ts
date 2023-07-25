import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, ReplaySubject, Subject, switchMap, shareReplay, filter, tap, startWith, catchError, of } from 'rxjs';
import { Flowchart, FlowchartConfirmation } from './flowchart';
import {environment} from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FlowchartService {
  constructor(
    private http: HttpClient
  ) { }

  public readonly deleteFlowchartSource = new Subject<string>();
  public readonly getFlowchartsSource = new Subject<void>();

  private readonly deleteFlowchart$ = this.deleteFlowchartSource.pipe(
     switchMap((flowchartId) => this.http.delete<FlowchartConfirmation>(this.buildUrl(`/flowcharts/${flowchartId}`)).pipe(
      tap(() => this.getFlowcharts())
    ))
  )

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  public deleteFlowchartSub = this.deleteFlowchart$.subscribe();
  
  public readonly flowcharts$ = this.getFlowchartsSource.pipe(
    startWith(undefined),
    switchMap(() => 
      this.http.get(this.buildUrl('/flowcharts')).pipe(
        catchError(() => of([]))
      )
    ),
    filter((x): x is Flowchart[] => !!x),
    catchError(() => []),
    shareReplay({ refCount: true, bufferSize: 1 })
  )

  public readonly flowchartsCount$ = this.flowcharts$.pipe(
    map((x) => x.length)
  )

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }

  getFlowcharts(): void {
    this.getFlowchartsSource.next();
  }

  getFlowchart(flowchartId: string): Observable<Flowchart> {
    return this.http.get<Flowchart>(this.buildUrl(`/flowcharts/${flowchartId}`));
  }

  upsertFlowchart(flowchartJson: Flowchart): Observable<Flowchart> {
    return this.http.post<Flowchart>(this.buildUrl(`/flowcharts`), flowchartJson);
  }

  runFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get<FlowchartConfirmation>(this.buildUrl(`/flowcharts/${flowchartId}/run`));
  }

  stopFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get<FlowchartConfirmation>(this.buildUrl(`/flowcharts/${flowchartId}/stop`));
  }

  deleteFlowchart(flowchartId: string): void {
    this.deleteFlowchartSource.next(flowchartId);
  }

  getFlowchartPng(flowchartId: string): Observable<Blob> {
    // I think this cast is lying
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/png`, { responseType: 'blob' }) as Observable<Blob>;
  }
  
}
