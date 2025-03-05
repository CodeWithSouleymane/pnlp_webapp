import { Routes } from '@angular/router';

// Component imports
import { HomeComponent } from './components/home/home.component';
import { AboutComponent } from './components/about/about.component';
import { StatisticsComponent } from './components/statistics/statistics.component';
import { ResourcesComponent } from './components/resources/resources.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'statistics', component: StatisticsComponent },
  { path: 'resources', component: ResourcesComponent },
  { path: '**', redirectTo: '' } // Redirect to home for any unknown routes
];
