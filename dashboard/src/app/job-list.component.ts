import { Component, OnInit, Input } from '@angular/core';
import { JobsService } from './jobs.service';
import { Job } from './job';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrls: ['./job-list.component.css']
})
export class JobListComponent implements OnInit {
  @Input() graphId?: string;
  jobs: Job[] = [];
  sortDirection = 1; // 1 for ascending, -1 for descending
  currentSortColumn: string | null = null;

  constructor(private jobsService: JobsService) { }

  ngOnInit(): void {
    this.getJobs();
  }

  getJobs(): void {
    this.jobsService.getJobs().subscribe(jobs => {
      if (this.graphId) {
        this.jobs = jobs.filter(job => job.graph_id === Number(this.graphId));
      } else {
        this.jobs = jobs;
      }
    });
  }

  sortJobs<T extends keyof Job>(property: T): Job[] {
    this.sortDirection = this.sortDirection * -1; // flip the direction
    this.currentSortColumn = property;
    return this.jobs.sort((a: Job, b: Job) => {
      if (a[property] < b[property]) {
        return -1 * this.sortDirection;
      } else if (a[property] > b[property]) {
        return 1 * this.sortDirection;
      } else {
        return 0;
      }
    });
  }
}
