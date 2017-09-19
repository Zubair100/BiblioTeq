
export class EncodedPDF {
  private _pdfAsString: string;

  constructor(encodedPdf: string) {
    this._pdfAsString = encodedPdf;
  }


  get pdfAsString(): string {
    return this._pdfAsString;
  }
}
