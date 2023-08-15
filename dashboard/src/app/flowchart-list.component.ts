import { ChangeDetectionStrategy, Component, ViewChild } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import { Router } from '@angular/router';
import { PopoverComponent } from './popover.component';
import { BehaviorSubject, combineLatest } from 'rxjs';

@Component({
  selector: 'app-flowchart-list',
  templateUrl: './flowchart-list.component.html',
  styleUrls: ['./flowchart-list.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartListComponent {
  constructor(
    private readonly flowchartService: FlowchartService,
    private readonly router: Router
  ) { }

  private readonly flowcharts$ = this.flowchartService.flowcharts$;

  @ViewChild('popover') popover?: PopoverComponent;
  private deleteUid$ = new BehaviorSubject<string | null>(null);
  deleteMessage$ = new BehaviorSubject<string>('');

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$
  });

  navigateToFlowchart(uid: string): void {
    this.router.navigate(['/flowcharts', uid]);
  }

  deleteFlowchart(id: string): void {
    this.flowchartService.deleteFlowchart(id)
  }

  openDeleteConfirmation(uid: string) {
    this.deleteUid$.next(uid);
    this.deleteMessage$.next(`Are you sure you want to delete the flowchart with ID ${uid}?`);
    this.popover?.openPopover();
  }
  
  handleDeleteConfirmation(result: boolean) {
    if (result) {
      const deleteUid = this.deleteUid$.getValue();
      if (deleteUid) {
        this.deleteFlowchart(deleteUid);
      }
    }
    this.deleteUid$.next(null);
  }
}
