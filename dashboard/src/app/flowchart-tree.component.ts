import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, ChangeDetectorRef, OnInit } from '@angular/core';
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
  constructor(private cdr: ChangeDetectorRef) {}  // <-- Inject ChangeDetectorRef
  private _vm$ = new BehaviorSubject<any>(null);
  public readonly vm$ = this._vm$.asObservable();

  ngOnInit() {
    console.log('Component initialized');
  }
  ngOnChanges(changes: SimpleChanges): void {
    console.log('Changes detected', changes);
    if (changes['treeData'] && changes['treeData'].currentValue) {
      console.log("I'm here, with data:", this.treeData);
      this.parsedJson = JSON.parse(this.treeData as string);
      this._vm$.next(this.parsedJson);
      this.cdr.markForCheck();  // <-- Manually mark for check
    }
  }
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
  
}


