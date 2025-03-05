import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ContactService, ContactFormData } from '../../services/contact.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink],
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.scss']
})
export class ContactComponent {
  contactForm: FormGroup;
  submitted = false;
  formSuccess = false;
  formError = false;

  constructor(
    private fb: FormBuilder,
    private contactService: ContactService
  ) {
    this.contactForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      subject: ['', Validators.required],
      message: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  // Getter for easy access to form fields
  get f() { return this.contactForm.controls; }

  onSubmit() {
    this.submitted = true;
    this.formSuccess = false;
    this.formError = false;

    // Stop here if form is invalid
    if (this.contactForm.invalid) {
      return;
    }

    const formData: ContactFormData = {
      name: this.contactForm.value.name,
      email: this.contactForm.value.email,
      subject: this.contactForm.value.subject,
      message: this.contactForm.value.message
    };

    this.contactService.sendContactForm(formData).subscribe({
      next: (response) => {
        this.formSuccess = true;
        this.submitted = false;
        this.contactForm.reset();
      },
      error: (error) => {
        console.error('Error submitting form:', error);
        this.formError = true;
        this.submitted = false;
      }
    });
  }
}
