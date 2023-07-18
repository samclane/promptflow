import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobsService } from './jobs.service';
import { Job } from './job';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.css']
})
export class JobDetailComponent implements OnInit {
  jobId!: string;
  job!: Job;

  constructor(
    private route: ActivatedRoute,
    private jobsService: JobsService
  ) { }

  ngOnInit(): void {
    this.jobId = this.route.snapshot.paramMap.get('id') as string;
    if (this.jobId){ 
        this.getJob();

    }
  }

  getJob(): void {
    if (this.jobId) {
        this.jobsService.getJob(this.jobId).pipe(take(1)).subscribe(job => this.job = job);
    }
  }

}
