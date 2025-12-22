import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

const activities = [
  {
    id: 1,
    type: 'success',
    service: 'Scoring',
    message: 'Score calculé pour "Jus Bio Orange"',
    time: 'Il y a 2 min'
  },
  {
    id: 2,
    type: 'success',
    service: 'ParserProduit',
    message: '45 nouveaux produits importés',
    time: 'Il y a 15 min'
  },
  {
    id: 3,
    type: 'warning',
    service: 'NLPIngrédients',
    message: 'Ingrédient non reconnu détecté',
    time: 'Il y a 32 min'
  },
  {
    id: 4,
    type: 'success',
    service: 'LCALite',
    message: 'Analyse ACV terminée',
    time: 'Il y a 1h'
  },
  {
    id: 5,
    type: 'success',
    service: 'Provenance',
    message: 'Version v2.3.1 enregistrée',
    time: 'Il y a 2h'
  }
];

export function RecentActivity() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-gray-900 mb-4">Activité récente</h3>
      
      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex gap-3">
            <div className="flex-shrink-0">
              {activity.type === 'success' && (
                <CheckCircle className="w-5 h-5 text-emerald-500" />
              )}
              {activity.type === 'warning' && (
                <AlertCircle className="w-5 h-5 text-yellow-500" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900">{activity.message}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-emerald-600">{activity.service}</span>
                <span className="text-xs text-gray-400">•</span>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {activity.time}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
