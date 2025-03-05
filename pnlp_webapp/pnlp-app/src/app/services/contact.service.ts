import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  private apiUrl = `${environment.apiUrl}${environment.contactApiEndpoint}`;

  constructor(private http: HttpClient) { }

  /**
   * Send contact form data to the server
   * @param formData The contact form data
   * @returns An Observable with the response
   */
  sendContactForm(formData: ContactFormData): Observable<any> {
    // In a real application, you would use this to send data to your backend
    // return this.http.post<any>(this.apiUrl, formData);
    
    // For demo purposes, we'll simulate a successful API response
    return this.simulateApiResponse(formData);
  }

  /**
   * Simulate an API response (for demo purposes only)
   * @param formData The contact form data
   * @returns An Observable that simulates an API response
   */
  private simulateApiResponse(formData: ContactFormData): Observable<any> {
    console.log('Contact form submitted:', formData);
    console.log('API URL (for real implementation):', this.apiUrl);
    
    // Simulate a successful response after a delay
    return of({
      success: true,
      message: 'Votre message a été envoyé avec succès.',
      data: formData
    }).pipe(delay(1500)); // Simulate network delay
  }
}
