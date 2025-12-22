import { ServiceCard } from '../dashboard/ServiceCard';
import { StatsGrid } from '../dashboard/StatsGrid';
import { SystemFlow } from '../dashboard/SystemFlow';
import { RecentActivity } from '../dashboard/RecentActivity';
import { 
  FileText, 
  BrainCircuit, 
  Leaf, 
  Award, 
  Globe, 
  Database 
} from 'lucide-react';

const services = [
  {
    name: 'ParserProduit',
    icon: FileText,
    status: 'active' as const,
    description: 'Extraction automatique des données produits',
    metrics: { requests: 1243, avgTime: '120ms' }
  },
  {
    name: 'NLPIngrédients',
    icon: BrainCircuit,
    status: 'active' as const,
    description: 'Normalisation des ingrédients via NLP',
    metrics: { requests: 987, avgTime: '340ms' }
  },
  {
    name: 'LCALite',
    icon: Leaf,
    status: 'active' as const,
    description: 'Analyse du cycle de vie simplifiée',
    metrics: { requests: 856, avgTime: '580ms' }
  },
  {
    name: 'Scoring',
    icon: Award,
    status: 'active' as const,
    description: 'Calcul du score environnemental',
    metrics: { requests: 823, avgTime: '95ms' }
  },
  {
    name: 'WidgetAPI',
    icon: Globe,
    status: 'active' as const,
    description: 'API publique et interface web',
    metrics: { requests: 5421, avgTime: '45ms' }
  },
  {
    name: 'Provenance',
    icon: Database,
    status: 'active' as const,
    description: 'Traçabilité et versioning',
    metrics: { requests: 412, avgTime: '75ms' }
  }
];

export function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Tableau de bord — EcoLabel Microservices</h1>
        <p className="text-gray-600">
          Plateforme de calcul automatisé des scores environnementaux produits
        </p>
      </div>

      <StatsGrid />

      <div className="mt-8">
        <h2 className="text-gray-900 mb-4">Architecture des Microservices</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {services.map((service) => (
            <ServiceCard key={service.name} service={service} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="lg:col-span-2">
          <SystemFlow />
        </div>
        <div>
          <RecentActivity />
        </div>
      </div>
    </div>
  );
}
