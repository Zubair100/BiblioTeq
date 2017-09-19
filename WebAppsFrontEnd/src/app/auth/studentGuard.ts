import {Injectable} from "@angular/core";
import {CanActivate, Router} from "@angular/router";
import {AppSettings} from "../../AppSettings";

@Injectable()
export class StudentGuard implements CanActivate {
  constructor(private router: Router) {
  }


  canActivate(): boolean {
    let isLecturer = parseInt(localStorage.getItem(AppSettings.privilege)) > 0;
    if (!isLecturer) {
      this.router.navigate(['/search']);
    }
    return isLecturer;
  }

}

