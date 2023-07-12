// node-type-list.component.ts
import { Component, OnInit } from '@angular/core';
import { NodeService } from './node.service';

@Component({
  selector: 'app-node-type-list',
  templateUrl: './node-type-list.component.html',
  styleUrls: ['./node-type-list.component.css']
})
export class NodeTypeListComponent implements OnInit {
  nodeTypes: any[] = [];

  constructor(private nodeService: NodeService) { }

  ngOnInit(): void {
    this.getNodeTypes();
  }

  getNodeTypes(): void {
    this.nodeService.getNodeTypes().subscribe(nodeTypes => this.nodeTypes = nodeTypes["node_types"]);
  }

  // Other methods for interacting with node types...
}
