import { Component, OnInit } from '@angular/core';
import { JobsService } from './jobs.service';
import { Job } from './job';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrls: ['./job-list.component.css']
})
export class JobListComponent implements OnInit {
  jobs: Job[] = [];
  sortDirection = 1; // 1 for ascending, -1 for descending

  constructor(private jobsService: JobsService) { }

  ngOnInit(): void {
    this.getJobs();
  }

  getJobs(): void {
    this.jobsService.getJobs().subscribe(jobs => this.jobs = jobs);
  }

  sortJobs<T extends keyof Job>(property: T): Job[] {
    return this.jobs.sort((a: Job, b: Job) => {
        if (a[property] < b[property]) {
            return -1;
        } else if (a[property] > b[property]) {
            return 1;
        } else {
            return 0;
        }
    });
}

}
