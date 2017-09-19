import {Injectable} from "@angular/core";
import {CanActivate, Router} from "@angular/router";
import {isAuthenticated} from "./auth.module";

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private router: Router) {}


  canActivate() {
    let auth = isAuthenticated();
    if (!auth) {
      //not authenticated, redirect to login
      this.router.navigate(['/login']);
    }
    return auth;
  }

}
