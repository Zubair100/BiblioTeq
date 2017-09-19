import {Injectable} from "@angular/core";
import {CanActivate, Router} from "@angular/router";
import {isAuthenticated} from "./auth.module";


@Injectable()
export class LoginGuard implements CanActivate {
  constructor(private router: Router) {}


  canActivate() {
    let auth = isAuthenticated();
    if (auth) {
      this.router.navigate(['/search']);
    }
    return !auth;
  }

}
