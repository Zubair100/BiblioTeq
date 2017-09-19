import {RouterModule, Routes} from "@angular/router";
import {LoginComponent} from "./login/login.component";
import {SearchComponent} from "./search/search.component";
import {AuthGuard} from "./auth/auth-guard.service";
import {SolutionPageComponent} from "./solution-page/solution-page.component";
import {NgModule} from "@angular/core";
import {UploadPaperComponent} from "./upload-paper/upload-paper.component";
import {LoginGuard} from "./auth/login-guard-service";
import {RegisterUserComponent} from "./register-user/register-user.component";
import {StudentGuard} from "./auth/studentGuard";


const routes: Routes = [
  {path: '', redirectTo: '/login', pathMatch: 'full'},
  {path: 'login', component: LoginComponent, canActivate: [LoginGuard]},
  {path: 'register', component: RegisterUserComponent, canActivate: [LoginGuard]},
  {path: 'search', component: SearchComponent, canActivate: [AuthGuard]},
  {path: ':paperCode/:paperYear', component: SolutionPageComponent, canActivate: [AuthGuard]},
  {path: 'upload', component: UploadPaperComponent, canActivate: [AuthGuard, StudentGuard]},
  {path: '**', redirectTo: '/login', pathMatch: 'full'}
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes),
  ],
  exports: [
    RouterModule
  ]
})

export class AppRoutingModule {}
