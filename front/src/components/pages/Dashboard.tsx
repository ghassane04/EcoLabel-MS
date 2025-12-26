import { useState, useEffect } from 'react';
import {
  FileText,
  BrainCircuit,
  Leaf,
  Award,
  Globe,
  Database,
  RefreshCcw,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';

interface ServiceStatus {
  name: string;
  port: number;
  status: 'online' | 'offline' | 'loading';
  description: string;
  icon: any;
}

const SERVICES_CONFIG = [
  { name: 'ParserProduit', port: 8001, description: 'Extraction OCR des produits', icon: FileText },
  { name: 'NLPIngredients', port: 8002, description: 'Analyse NLP des ingrédients', icon: BrainCircuit },
  { name: 'LCALite', port: 8003, description: 'Calcul Cycle de Vie (ACV)', icon: Leaf },
  { name: 'Scoring', port: 8004, description: 'Score environnemental A-E', icon: Award },
  { name: 'WidgetAPI', port: 8005, description: 'API publique REST', icon: Globe },
  { name: 'Provenance', port: 8007, description: 'Traçabilité des données', icon: Database },
];

export function Dashboard() {
  const [services, setServices] = useState<ServiceStatus[]>(
    SERVICES_CONFIG.map(s => ({ ...s, status: 'loading' as const }))
  );
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const checkServiceHealth = async (port: number): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`http://localhost:${port}/health`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeout);
      return response.ok;
    } catch {
      return false;
    }
  };

  const refreshStatus = async () => {
    setIsRefreshing(true);

    const results = await Promise.all(
      SERVICES_CONFIG.map(async (service) => {
        const isOnline = await checkServiceHealth(service.port);
        return {
          ...service,
          status: isOnline ? 'online' as const : 'offline' as const,
        };
      })
    );

    setServices(results);
    setLastUpdate(new Date());
    setIsRefreshing(false);
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const onlineCount = services.filter(s => s.status === 'online').length;
  const totalCount = services.length;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            EcoLabel-MS — Dashboard
          </h1>
          <p className="text-gray-600">
            Statut en temps réel des microservices
          </p>
        </div>
        <div className="text-right">
          <button
            onClick={refreshStatus}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCcw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
          {lastUpdate && (
            <p className="text-xs text-gray-500 mt-2">
              Dernière mise à jour: {lastUpdate.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      {/* Status Summary */}
      <div className="mb-6 p-4 bg-white rounded-xl border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-4 h-4 rounded-full ${onlineCount === totalCount ? 'bg-emerald-500' :
              onlineCount > 0 ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
            <span className="text-lg font-semibold text-gray-900">
              {onlineCount}/{totalCount} services actifs
            </span>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${onlineCount === totalCount ? 'bg-emerald-100 text-emerald-800' :
            onlineCount > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
            }`}>
            {onlineCount === totalCount ? 'Tout opérationnel' :
              onlineCount > 0 ? 'Partiellement opérationnel' : 'Services arrêtés'}
          </span>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {services.map((service) => {
          const Icon = service.icon;
          return (
            <div
              key={service.name}
              className={`bg-white rounded-xl border p-5 transition-all hover:shadow-md ${service.status === 'online' ? 'border-emerald-200' :
                service.status === 'offline' ? 'border-red-200' : 'border-gray-200'
                }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg ${service.status === 'online' ? 'bg-emerald-100' :
                  service.status === 'offline' ? 'bg-red-100' : 'bg-gray-100'
                  }`}>
                  <Icon className={`w-5 h-5 ${service.status === 'online' ? 'text-emerald-600' :
                    service.status === 'offline' ? 'text-red-600' : 'text-gray-600'
                    }`} />
                </div>
                {service.status === 'loading' ? (
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                ) : service.status === 'online' ? (
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
              </div>

              <h3 className="font-semibold text-gray-900 mb-1">{service.name}</h3>
              <p className="text-sm text-gray-600 mb-2">{service.description}</p>

              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Port: {service.port}</span>
                <a
                  href={`http://localhost:${service.port}/docs`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-600 hover:underline"
                >
                  API Docs →
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
