import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { NodeTypes } from './node';

@Injectable({
  providedIn: 'root'
})
export class NodeService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getNodeTypes(): Observable<NodeTypes> {
    return this.http.get(`${this.apiUrl}/nodes/types`) as Observable<NodeTypes>;
  }

  addNode(flowchartId: string, nodeType: string): Observable<Node> {
    return this.http.post(`${this.apiUrl}/flowcharts/${flowchartId}/nodes`, { node_type: nodeType }) as Observable<Node>;
  }

  removeNode(flowchartId: string, nodeId: string): Observable<Node> {
    return this.http.delete(`${this.apiUrl}/flowcharts/${flowchartId}/nodes/${nodeId}`) as Observable<Node>;
  }
}
