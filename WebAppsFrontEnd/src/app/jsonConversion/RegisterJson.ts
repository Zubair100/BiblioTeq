import {LoginDetails} from "../login/LoginDetails";


export class UserDetails implements LoginDetails {
  username: string;
  password: string;


  constructor(username: string, password: string) {
    this.username = username;
    this.password = password;
  }
}
