
export interface EditAnswerJson {
  readonly id: number;
  readonly html: string;
}

export class EditAnswer implements EditAnswerJson {
  id: number;
  html: string;

  constructor(id: number, html: string) {
    this.id = id;
    this.html = html;
  }
}
