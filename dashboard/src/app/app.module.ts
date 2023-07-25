import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; 

import { AppComponent } from './app.component';
import { FlowchartListComponent } from './flowchart-list.component';
import { JobListComponent } from './job-list.component';
import { NodeTypeListComponent } from './node-type-list.component';
import { FlowchartDetailComponent } from './flowchart-detail.component';
import { JobDetailComponent } from './job-detail.component';

import { RouterModule, Routes } from '@angular/router';
import { JobLogsComponent } from './job-logs.component';
import { HeaderComponent } from './header.component';
import { HomeComponent } from './home.component';
import { FlowchartListContainerComponent } from './flowchart-list-container.component';
import { FlowchartDisplayComponent } from './flowchart-display.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AddNodeComponent } from './add-node.component';
import {FlowchartImportJson} from './flowchart-import-json.component';
import { JobListContainerComponent } from './job-list-container.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'flowcharts', component: FlowchartListContainerComponent },
  { path: 'flowcharts/:id', component: FlowchartDetailComponent },
  { path: 'jobs', component: JobListContainerComponent },
  { path: 'jobs/:id', component: JobDetailComponent }
];



@NgModule({
  declarations: [
    AppComponent,
    FlowchartListComponent,
    JobListComponent,
    NodeTypeListComponent,
    FlowchartDetailComponent,
    JobDetailComponent,
    JobLogsComponent,
    HeaderComponent,
    HomeComponent,
    FlowchartListContainerComponent,
    FlowchartDisplayComponent,
    FlowchartImportJson,
    AddNodeComponent,
    JobListContainerComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    FormsModule,
    ReactiveFormsModule

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
