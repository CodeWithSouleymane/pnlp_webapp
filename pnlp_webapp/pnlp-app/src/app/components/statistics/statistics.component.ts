import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-statistics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss']
})
export class StatisticsComponent implements OnInit, AfterViewInit {
  // Key indicators
  indicators = [
    { 
      title: 'Incidence du paludisme', 
      value: '12.3', 
      unit: 'pour 1000 habitants', 
      change: '-15%', 
      description: 'Nombre de nouveaux cas de paludisme pour 1000 habitants en 2024',
      trend: 'down'
    },
    { 
      title: 'Mortalité liée au paludisme', 
      value: '0.8', 
      unit: 'pour 100 000 habitants', 
      change: '-22%', 
      description: 'Taux de mortalité liée au paludisme pour 100 000 habitants en 2024',
      trend: 'down'
    },
    { 
      title: 'Couverture en MILDA', 
      value: '85', 
      unit: '%', 
      change: '+5%', 
      description: 'Pourcentage de la population ayant accès à une moustiquaire imprégnée en 2024',
      trend: 'up'
    },
    { 
      title: 'Femmes enceintes sous TPI', 
      value: '78', 
      unit: '%', 
      change: '+8%', 
      description: 'Pourcentage de femmes enceintes ayant reçu au moins 3 doses de TPI en 2024',
      trend: 'up'
    }
  ];

  // Regional data for the map
  regionalData = [
    { region: 'Dakar', incidence: 5.2, coverage: 82, mortality: 0.3 },
    { region: 'Thiès', incidence: 8.7, coverage: 85, mortality: 0.5 },
    { region: 'Saint-Louis', incidence: 7.4, coverage: 80, mortality: 0.4 },
    { region: 'Louga', incidence: 10.1, coverage: 78, mortality: 0.6 },
    { region: 'Fatick', incidence: 15.3, coverage: 83, mortality: 0.9 },
    { region: 'Kaolack', incidence: 18.2, coverage: 79, mortality: 1.1 },
    { region: 'Kaffrine', incidence: 22.5, coverage: 75, mortality: 1.3 },
    { region: 'Matam', incidence: 12.8, coverage: 77, mortality: 0.8 },
    { region: 'Diourbel', incidence: 14.2, coverage: 81, mortality: 0.9 },
    { region: 'Tambacounda', incidence: 28.7, coverage: 72, mortality: 1.7 },
    { region: 'Kédougou', incidence: 35.2, coverage: 70, mortality: 2.1 },
    { region: 'Kolda', incidence: 30.5, coverage: 73, mortality: 1.9 },
    { region: 'Sédhiou', incidence: 27.3, coverage: 74, mortality: 1.6 },
    { region: 'Ziguinchor', incidence: 20.1, coverage: 76, mortality: 1.2 }
  ];

  // Yearly trend data
  yearlyTrends = {
    years: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    incidence: [28.5, 25.2, 22.1, 19.8, 16.5, 14.2, 12.3],
    mortality: [2.8, 2.3, 1.9, 1.5, 1.2, 1.0, 0.8],
    coverage: [65, 68, 72, 75, 78, 82, 85]
  };

  // Age distribution data
  ageDistribution = {
    labels: ['0-5 ans', '5-15 ans', '15-25 ans', '25-45 ans', '45+ ans'],
    data: [42, 28, 15, 10, 5]
  };

  // Seasonal variation data
  seasonalVariation = {
    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
    data: [8, 5, 3, 2, 4, 10, 25, 45, 60, 35, 20, 12]
  };

  constructor() { }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    this.createTrendChart();
    this.createAgeDistributionChart();
    this.createSeasonalVariationChart();
  }

  createTrendChart(): void {
    const ctx = document.getElementById('trendChart') as HTMLCanvasElement;
    if (ctx) {
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.yearlyTrends.years,
          datasets: [
            {
              label: 'Incidence (pour 1000)',
              data: this.yearlyTrends.incidence,
              borderColor: '#007bff',
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.3
            },
            {
              label: 'Mortalité (pour 100 000)',
              data: this.yearlyTrends.mortality,
              borderColor: '#dc3545',
              backgroundColor: 'rgba(220, 53, 69, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Évolution de l\'incidence et de la mortalité liées au paludisme'
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Taux'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Année'
              }
            }
          }
        }
      });
    }
  }

  createAgeDistributionChart(): void {
    const ctx = document.getElementById('ageDistributionChart') as HTMLCanvasElement;
    if (ctx) {
      new Chart(ctx, {
        type: 'pie',
        data: {
          labels: this.ageDistribution.labels,
          datasets: [
            {
              data: this.ageDistribution.data,
              backgroundColor: [
                '#007bff',
                '#28a745',
                '#ffc107',
                '#17a2b8',
                '#6c757d'
              ],
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Distribution des cas de paludisme par tranche d\'âge (%)'
            },
            legend: {
              position: 'right'
            }
          }
        }
      });
    }
  }

  createSeasonalVariationChart(): void {
    const ctx = document.getElementById('seasonalVariationChart') as HTMLCanvasElement;
    if (ctx) {
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.seasonalVariation.labels,
          datasets: [
            {
              label: 'Cas de paludisme',
              data: this.seasonalVariation.data,
              backgroundColor: 'rgba(0, 123, 255, 0.7)',
              borderColor: '#007bff',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Variation saisonnière des cas de paludisme (en milliers)'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Nombre de cas (en milliers)'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Mois'
              }
            }
          }
        }
      });
    }
  }
}
