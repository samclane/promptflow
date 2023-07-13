import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';  // Import HttpClientModule

import { AppComponent } from './app.component';
import { FlowchartListComponent } from './flowchart-list.component';
import { JobListComponent } from './job-list.component';
import { NodeTypeListComponent } from './node-type-list.component';
import { FlowchartDetailComponent } from './flowchart-detail.component';

import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'flowcharts', component: FlowchartListComponent },
  { path: 'flowcharts/:id', component: FlowchartDetailComponent },
  { path: 'jobs', component: JobListComponent },
  //... other routes ...
];



@NgModule({
  declarations: [
    AppComponent,
    FlowchartListComponent,
    JobListComponent,
    NodeTypeListComponent,
    FlowchartDetailComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,  // Add HttpClientModule to imports
    RouterModule.forRoot(routes)  // Add RouterModule to imports
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
