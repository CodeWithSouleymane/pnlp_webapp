import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  // Slider images for the hero section
  sliderImages = [
    { 
      src: 'assets/images/slider1.jpg', 
      alt: 'Lutte contre le paludisme', 
      title: 'Ensemble contre le paludisme',
      description: 'Le Programme National de Lutte contre le Paludisme œuvre pour l\'élimination du paludisme au Sénégal.'
    },
    { 
      src: 'assets/images/slider2.jpg', 
      alt: 'Prévention du paludisme', 
      title: 'Prévenir le paludisme',
      description: 'L\'utilisation de moustiquaires imprégnées est un moyen efficace de prévention.'
    },
    { 
      src: 'assets/images/slider3.jpg', 
      alt: 'Sensibilisation', 
      title: 'Sensibiliser les populations',
      description: 'La sensibilisation est essentielle pour lutter efficacement contre le paludisme.'
    }
  ];

  // Latest news items
  newsItems = [
    {
      title: 'Campagne de distribution de moustiquaires',
      date: '28 Février 2025',
      summary: 'Le PNLP lance une nouvelle campagne de distribution de moustiquaires imprégnées dans les régions du Sud.',
      image: 'assets/images/news1.jpg',
      link: '#'
    },
    {
      title: 'Journée mondiale de lutte contre le paludisme',
      date: '25 Avril 2025',
      summary: 'Célébration de la journée mondiale de lutte contre le paludisme sous le thème "Zéro palu, je m\'engage".',
      image: 'assets/images/news2.jpg',
      link: '#'
    },
    {
      title: 'Nouveaux médicaments antipaludiques',
      date: '15 Janvier 2025',
      summary: 'Introduction de nouveaux médicaments antipaludiques dans les centres de santé du pays.',
      image: 'assets/images/news3.jpg',
      link: '#'
    }
  ];

  // Key statistics
  statistics = [
    { label: 'Cas de paludisme', value: '24,853', change: '-12%', icon: 'bi-activity' },
    { label: 'Moustiquaires distribuées', value: '1.2M', change: '+15%', icon: 'bi-shield-check' },
    { label: 'Centres de santé équipés', value: '458', change: '+8%', icon: 'bi-hospital' },
    { label: 'Agents formés', value: '2,750', change: '+22%', icon: 'bi-people' }
  ];

  // Partners
  partners = [
    { name: 'OMS', logo: 'assets/images/partners/who.png' },
    { name: 'UNICEF', logo: 'assets/images/partners/unicef.png' },
    { name: 'Fonds Mondial', logo: 'assets/images/partners/global-fund.png' },
    { name: 'USAID', logo: 'assets/images/partners/usaid.png' },
    { name: 'PMI', logo: 'assets/images/partners/pmi.png' }
  ];
}
