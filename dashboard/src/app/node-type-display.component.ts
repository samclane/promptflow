import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { NodeTypes } from './node';

interface NodeType {
  nodeType: string;
  options: string[];
  description: string;
}

@Component({
  selector: 'app-node-type-display',
  templateUrl: "./node-type-display.component.html",
  styles: []
})
export class NodeListComponent implements OnInit {
  nodeTypes$?: Observable<NodeType[]>;

  constructor(private http: HttpClient) { }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }

  ngOnInit(): void {
    this.nodeTypes$ = this.http.get<NodeTypes>(this.buildUrl('/nodes/types')).pipe(
      map(({ node_types }) =>
        node_types.map(nodeType => ({
          nodeType: nodeType.name,
          options: nodeType.options,
          description: nodeType.description
        }))
      )
    );
  }
}
