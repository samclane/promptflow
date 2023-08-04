import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

interface NodeType {
  nodeType: string;
  options: string[];
}

@Component({
  selector: 'app-node-type-display',
  templateUrl: "./node-type-display.component.html",
  styles: []
})
export class NodeListComponent implements OnInit {
  nodeTypes$?: Observable<NodeType[]>;

  constructor(private http: HttpClient) {}

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }

  ngOnInit(): void {
    this.nodeTypes$ = this.http.get<{ node_types: string[] }>(this.buildUrl('/nodes/types')).pipe(
      switchMap(({ node_types }) =>
        forkJoin(
          node_types.map(nodeType =>
            this.http.get<{ options: string[] }>(this.buildUrl(`/nodes/${nodeType}/options`)).pipe(
              map(({ options }) => ({ nodeType, options }))
            )
          )
        )
      )
    );
  }
}
