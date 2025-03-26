import { Component, HostListener, OnInit } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'PNLP - Programme National de Lutte contre le Paludisme';
  isScrolled = false;

  ngOnInit() {
    // Initial check on page load
    this.checkScroll();
  }

  @HostListener('window:scroll', [])
  checkScroll() {
    // Apply 'scrolled' class when user scrolls down more than 50px
    this.isScrolled = window.scrollY > 50;
  }
}
