

export interface UserJsonInterface {
  readonly id: number;
  readonly username: string;
}

export class UserJson implements UserJsonInterface {
  id: number;
  username: string;

  constructor(id: number, username: string) {
    this.id = id;
    this.username = username;
  }
}
