import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, ReplaySubject, Subject, switchMap, shareReplay, filter, tap, startWith, catchError, of } from 'rxjs';
import { Flowchart, FlowchartConfirmation } from './flowchart';

@Injectable({
  providedIn: 'root'
})
export class FlowchartService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  public readonly deleteFlowchartSource = new Subject<string>();
  public readonly getFlowchartsSource = new Subject<void>();

  private readonly deleteFlowchart$ = this.deleteFlowchartSource.pipe(
     switchMap((flowchartId) => this.http.delete(`${this.apiUrl}/flowcharts/${flowchartId}`).pipe(
      filter((x): x is FlowchartConfirmation => !!x),
      tap(() => this.getFlowcharts())
    ))
  )

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
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}`) as Observable<Flowchart>;
  }

  upsertFlowchart(flowchartJson: Flowchart): Observable<Flowchart> {
    return this.http.post(`${this.apiUrl}/flowcharts`, flowchartJson) as Observable<Flowchart>;
  }

  runFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/run`) as Observable<FlowchartConfirmation>;
  }

  stopFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/stop`) as Observable<FlowchartConfirmation>;
  }

  deleteFlowchart(flowchartId: string): void {
    this.deleteFlowchartSource.next(flowchartId);
  }

  getFlowchartPng(flowchartId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/png`, { responseType: 'blob' }) as Observable<Blob>;
  }
  
}
