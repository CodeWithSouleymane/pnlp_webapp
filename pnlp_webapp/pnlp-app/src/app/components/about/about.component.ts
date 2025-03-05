import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent {
  // Team members
  teamMembers = [
    {
      name: 'Dr. Doudou Sène',
      position: 'Coordonnateur National',
      bio: 'Dr. Sène dirige le Programme National de Lutte contre le Paludisme depuis 2018. Il a plus de 20 ans d\'expérience dans la santé publique.',
      image: 'assets/images/team/coordinator.jpg'
    },
    {
      name: 'Dr. Aminata Diallo',
      position: 'Responsable Suivi-Évaluation',
      bio: 'Dr. Diallo supervise le suivi et l\'évaluation des interventions de lutte contre le paludisme dans tout le pays.',
      image: 'assets/images/team/member1.jpg'
    },
    {
      name: 'Dr. Moussa Ndiaye',
      position: 'Responsable Prévention',
      bio: 'Dr. Ndiaye coordonne les activités de prévention, notamment la distribution de moustiquaires et les campagnes de pulvérisation.',
      image: 'assets/images/team/member2.jpg'
    },
    {
      name: 'Dr. Fatou Mbaye',
      position: 'Responsable Prise en Charge',
      bio: 'Dr. Mbaye supervise les protocoles de diagnostic et de traitement du paludisme dans les structures de santé.',
      image: 'assets/images/team/member3.jpg'
    }
  ];

  // Timeline events
  milestones = [
    {
      year: '1995',
      title: 'Création du PNLP',
      description: 'Création du Programme National de Lutte contre le Paludisme au Sénégal.'
    },
    {
      year: '2005',
      title: 'Adoption des ACT',
      description: 'Introduction des combinaisons thérapeutiques à base d\'artémisinine (ACT) comme traitement de première ligne.'
    },
    {
      year: '2008',
      title: 'Couverture universelle en MILDA',
      description: 'Lancement de la stratégie de couverture universelle en moustiquaires imprégnées d\'insecticide à longue durée d\'action.'
    },
    {
      year: '2010',
      title: 'Diagnostic parasitologique',
      description: 'Généralisation du diagnostic parasitologique par TDR ou microscopie avant tout traitement.'
    },
    {
      year: '2015',
      title: 'Pré-élimination',
      description: 'Entrée dans la phase de pré-élimination du paludisme dans certains districts.'
    },
    {
      year: '2020',
      title: 'Stratégie "Zéro Palu"',
      description: 'Lancement de la stratégie "Zéro Palu, Je m\'engage" pour mobiliser toutes les couches de la société.'
    }
  ];

  // Strategic objectives
  objectives = [
    {
      title: 'Prévention',
      description: 'Assurer la couverture universelle des populations à risque par des mesures préventives efficaces.',
      icon: 'bi-shield-check'
    },
    {
      title: 'Prise en charge',
      description: 'Garantir un accès universel au diagnostic précoce et au traitement efficace du paludisme.',
      icon: 'bi-heart-pulse'
    },
    {
      title: 'Surveillance',
      description: 'Renforcer le système de surveillance pour détecter, investiguer et répondre à tous les cas de paludisme.',
      icon: 'bi-graph-up'
    },
    {
      title: 'Communication',
      description: 'Promouvoir les comportements favorables à la prévention et à la prise en charge précoce du paludisme.',
      icon: 'bi-megaphone'
    },
    {
      title: 'Recherche',
      description: 'Soutenir la recherche opérationnelle pour améliorer les stratégies de lutte contre le paludisme.',
      icon: 'bi-search'
    },
    {
      title: 'Coordination',
      description: 'Renforcer la gouvernance, la coordination et le partenariat pour la mobilisation des ressources.',
      icon: 'bi-people'
    }
  ];
}
