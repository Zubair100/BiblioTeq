import {Component, OnInit} from '@angular/core';
import {Router} from "@angular/router";
import {HttpAPIService} from "../http-api.service";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css',
    '../../assets/forms.css']
})
export class SearchComponent {

  validPapers: Map<string, number[]> = new Map();
  courseCodes: string[] = [];
  courseCodesWithName: Map<string, string> = new Map();
  selectedCode: string;
  selectedYear: number;


  constructor(private router: Router,
              private apiService: HttpAPIService) {
    let validPaperJson: string;
    this.apiService.retrieveAllPapers().subscribe(
      res => validPaperJson = JSON.stringify(res),
      error => console.log(error),
      () => {
        let parsedPapers = JSON.parse(validPaperJson);
        Object.keys(parsedPapers).forEach((courseCode: string) => {
          this.validPapers.set(courseCode + ' : ' + parsedPapers[courseCode]['Name'],
            parsedPapers[courseCode]['Years'].map(year => parseInt(year)));
          this.courseCodes.push(courseCode + ' : ' + parsedPapers[courseCode]['Name']);
          this.courseCodesWithName.set(courseCode + ' : ' + parsedPapers[courseCode]['Name'], courseCode);
        });
        this.sortAll();

      }
    );
  }

  private sortAll(): void {
    this.courseCodes.sort((a, b) => a.localeCompare(b));
    this.validPapers.forEach(val => {
      val.sort((a, b) => b - a);
    });
  }

  setDefaultYear() {
    this.selectedYear = this.validPapers.get(this.selectedCode)[0];
  }

  getPaper() {
    this.router.navigate(['/' + this.courseCodesWithName.get(this.selectedCode) + '/' + this.selectedYear]);
  }

}

