import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-resources',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './resources.component.html',
  styleUrls: ['./resources.component.scss']
})
export class ResourcesComponent {
  // Resource categories
  categories = [
    { id: 'all', name: 'Tous les documents' },
    { id: 'strategic', name: 'Plans stratégiques' },
    { id: 'reports', name: 'Rapports annuels' },
    { id: 'guidelines', name: 'Guides et protocoles' },
    { id: 'training', name: 'Matériels de formation' },
    { id: 'communication', name: 'Outils de communication' },
    { id: 'research', name: 'Publications de recherche' }
  ];

  // Active category
  activeCategory: string = 'all';

  // Resources list
  resources = [
    {
      title: 'Plan Stratégique National de Lutte contre le Paludisme 2021-2025',
      category: 'strategic',
      description: 'Document de référence qui définit les orientations stratégiques et les interventions prioritaires pour la lutte contre le paludisme au Sénégal pour la période 2021-2025.',
      fileType: 'PDF',
      fileSize: '4.2 MB',
      date: '15 Janvier 2021',
      thumbnail: 'assets/images/resources/strategic-plan.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Rapport annuel d\'activités du PNLP 2024',
      category: 'reports',
      description: 'Bilan des activités réalisées par le Programme National de Lutte contre le Paludisme au cours de l\'année 2024.',
      fileType: 'PDF',
      fileSize: '3.8 MB',
      date: '28 Février 2025',
      thumbnail: 'assets/images/resources/annual-report.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Guide de prise en charge du paludisme au Sénégal - Edition 2023',
      category: 'guidelines',
      description: 'Protocoles nationaux de diagnostic et de traitement du paludisme à l\'usage des professionnels de santé.',
      fileType: 'PDF',
      fileSize: '2.5 MB',
      date: '10 Mai 2023',
      thumbnail: 'assets/images/resources/treatment-guide.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Manuel de formation des agents de santé communautaire',
      category: 'training',
      description: 'Support de formation destiné aux agents de santé communautaire pour le diagnostic et la prise en charge du paludisme au niveau communautaire.',
      fileType: 'PDF',
      fileSize: '5.1 MB',
      date: '22 Juillet 2022',
      thumbnail: 'assets/images/resources/training-manual.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Boîte à outils de communication sur le paludisme',
      category: 'communication',
      description: 'Ensemble d\'outils de communication (affiches, dépliants, spots radio et TV) pour les campagnes de sensibilisation sur le paludisme.',
      fileType: 'ZIP',
      fileSize: '15.3 MB',
      date: '05 Avril 2024',
      thumbnail: 'assets/images/resources/communication-toolkit.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Évaluation de l\'efficacité des moustiquaires imprégnées d\'insecticide au Sénégal',
      category: 'research',
      description: 'Étude sur l\'efficacité des moustiquaires imprégnées d\'insecticide à longue durée d\'action dans la prévention du paludisme au Sénégal.',
      fileType: 'PDF',
      fileSize: '1.8 MB',
      date: '12 Décembre 2023',
      thumbnail: 'assets/images/resources/research-paper.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Plan de suivi-évaluation du PNLP 2021-2025',
      category: 'strategic',
      description: 'Cadre de suivi-évaluation des interventions de lutte contre le paludisme au Sénégal pour la période 2021-2025.',
      fileType: 'PDF',
      fileSize: '3.5 MB',
      date: '20 Février 2021',
      thumbnail: 'assets/images/resources/monitoring-plan.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Rapport d\'enquête sur les indicateurs du paludisme 2023',
      category: 'reports',
      description: 'Résultats de l\'enquête nationale sur les indicateurs du paludisme réalisée en 2023.',
      fileType: 'PDF',
      fileSize: '4.7 MB',
      date: '18 Mars 2024',
      thumbnail: 'assets/images/resources/survey-report.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Guide de la pulvérisation intra-domiciliaire',
      category: 'guidelines',
      description: 'Directives techniques pour la mise en œuvre des campagnes de pulvérisation intra-domiciliaire d\'insecticide.',
      fileType: 'PDF',
      fileSize: '2.2 MB',
      date: '30 Juin 2022',
      thumbnail: 'assets/images/resources/spray-guide.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Module de formation sur la microscopie du paludisme',
      category: 'training',
      description: 'Support de formation pour le diagnostic microscopique du paludisme destiné aux techniciens de laboratoire.',
      fileType: 'PDF',
      fileSize: '6.3 MB',
      date: '15 Août 2023',
      thumbnail: 'assets/images/resources/microscopy-training.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Étude sur la résistance aux insecticides des vecteurs du paludisme',
      category: 'research',
      description: 'Recherche sur la résistance aux insecticides des moustiques vecteurs du paludisme au Sénégal.',
      fileType: 'PDF',
      fileSize: '2.1 MB',
      date: '25 Septembre 2024',
      thumbnail: 'assets/images/resources/resistance-study.jpg',
      downloadUrl: '#'
    },
    {
      title: 'Rapport d\'évaluation à mi-parcours du Plan Stratégique National',
      category: 'reports',
      description: 'Évaluation à mi-parcours de la mise en œuvre du Plan Stratégique National de Lutte contre le Paludisme 2021-2025.',
      fileType: 'PDF',
      fileSize: '3.9 MB',
      date: '10 Janvier 2024',
      thumbnail: 'assets/images/resources/midterm-evaluation.jpg',
      downloadUrl: '#'
    }
  ];

  // Filtered resources
  filteredResources = [...this.resources];

  // Get category name by id
  getCategoryName(categoryId: string): string {
    const category = this.categories.find(cat => cat.id === categoryId);
    return category ? category.name : '';
  }

  // Filter resources by category
  filterByCategory(categoryId: string): void {
    this.activeCategory = categoryId;
    
    if (categoryId === 'all') {
      this.filteredResources = [...this.resources];
    } else {
      this.filteredResources = this.resources.filter(resource => resource.category === categoryId);
    }
  }
}
