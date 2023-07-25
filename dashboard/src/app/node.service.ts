import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { NodeTypes } from './node';
import {environment} from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NodeService {

  constructor(private http: HttpClient) { }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  getNodeTypes(): Observable<NodeTypes> {
    return this.http.get(`${this.apiUrl}/nodes/types`) as Observable<NodeTypes>;
  }

  addNode(flowchartId: string, nodeType: string): Observable<Node> {
    console.log('addNode', flowchartId, nodeType);
    return this.http.post(`${this.apiUrl}/flowcharts/${flowchartId}/nodes`, { node_type: nodeType }) as Observable<Node>;
  }

  removeNode(flowchartId: string, nodeId: string): Observable<Node> {
    return this.http.delete(`${this.apiUrl}/flowcharts/${flowchartId}/nodes/${nodeId}`) as Observable<Node>;
  }
}
