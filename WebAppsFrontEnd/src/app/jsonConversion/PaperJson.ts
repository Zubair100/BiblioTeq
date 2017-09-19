
export class Paper implements PaperJson{
  course: string;
  year: number;
  title: string;
  pdf: string;

  constructor(course: string, year: number, title: string, pdf: string) {
    this.course = course;
    this.year = year;
    this.title = title;
    this.pdf = pdf;
  }

}

export interface PaperJson {
  course: string;
  year: number;
  title: string;
  pdf: string;
}


