import { TestBed, inject } from '@angular/core/testing';

import { HttpAPIService } from './http-api.service';

describe('HttpAPIService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [HttpAPIService]
    });
  });

  it('should be created', inject([HttpAPIService], (service: HttpAPIService) => {
    expect(service).toBeTruthy();
  }));
});
