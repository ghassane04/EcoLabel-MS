import { LucideIcon } from 'lucide-react';

interface Service {
  name: string;
  icon: LucideIcon;
  status: 'active' | 'warning' | 'error';
  description: string;
  metrics: {
    requests: number;
    avgTime: string;
  };
}

interface ServiceCardProps {
  service: Service;
}

const statusColors = {
  active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  warning: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  error: 'bg-red-100 text-red-700 border-red-200'
};

const statusDots = {
  active: 'bg-emerald-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500'
};

export function ServiceCard({ service }: ServiceCardProps) {
  const Icon = service.icon;
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${statusColors[service.status]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${statusDots[service.status]}`} />
          <span className="text-xs text-gray-600">Active</span>
        </div>
      </div>

      <h3 className="text-gray-900 mb-2">{service.name}</h3>
      <p className="text-gray-600 text-sm mb-4">{service.description}</p>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <div>
          <p className="text-xs text-gray-500 mb-1">Requêtes/jour</p>
          <p className="text-gray-900">{service.metrics.requests.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Temps moyen</p>
          <p className="text-gray-900">{service.metrics.avgTime}</p>
        </div>
      </div>
    </div>
  );
}
