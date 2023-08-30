import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, OnInit } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: 'app-flowchart-tree',
    templateUrl: './flowchart-tree.component.html',
    styleUrls: ['./flowchart-tree.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartTreeComponent implements OnInit, OnChanges {
  @Input() treeData: string | undefined | null;
  parsedJson: any;
  constructor() {}
  private _vm$ = new BehaviorSubject<any>(null);
  public readonly vm$ = this._vm$.asObservable();

  ngOnInit() {
    console.log('Component initialized');
  }
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['treeData'] && changes['treeData'].currentValue) {
      this.parsedJson = JSON.parse(this.treeData as string);
      this._vm$.next(this.parsedJson);
    }
  }
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
  
}


