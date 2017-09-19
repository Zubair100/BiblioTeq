import {Component} from "@angular/core";
import {HttpAPIService} from "../http-api.service";
import {SafeResourceUrl} from "@angular/platform-browser";
import {EncodedPDF} from "./EncodedPdf";
import {Router} from "@angular/router";

@Component({
  selector: 'app-upload-paper',
  templateUrl: './upload-paper.component.html',
  styleUrls: ['./upload-paper.component.css'],
  providers: [HttpAPIService]
})
export class UploadPaperComponent {

  courseCode: string;
  paperYear: number;
  paperName: string;
  encodedPdf: EncodedPDF;
  questions: string;
  pdfSrc: SafeResourceUrl;
  showInvalidFormAlert: boolean = false;

  constructor(private apiService: HttpAPIService,
              private router: Router
  ) {}

  updateFile(file: HTMLInputElement) {
    let reader: FileReader = new FileReader();
    reader.onloadend = (ev: ProgressEvent) => {
      this.encodedPdf = new EncodedPDF(btoa(reader.result));
      this.pdfSrc = this.apiService.makePDF(this.encodedPdf.pdfAsString);
    };
    reader.readAsBinaryString(file.files[0]);
  }

  onSubmit(): void {
    if (!this.isValidSubmission()) {
      this.showInvalidFormAlert = true;
      return;
    }
    let questionList: string[] = this.questions.toLowerCase().replace(/\s/g, '').split(',');

    let jsonPaper: string;
    this.apiService.submitPaper(this.courseCode, this.paperYear, this.paperName, this.encodedPdf).subscribe(
      jsonData => jsonPaper = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        let parsedPaper = JSON.parse(jsonPaper);
        this.apiService.submitPaperQuestions(parsedPaper.id, questionList).subscribe(
          res => {},
          error => {
            console.log(error);
            alert('Something went wrong...');
            },
          () => {
            console.log('paper submitted');
            this.router.navigate(['/' + this.courseCode + '/' + this.paperYear]);
          }
        );
      }
    );
  }

  private isValidSubmission(): boolean {
    return this.paperYear > 2000 && this.paperYear < 2020;
  }
}


