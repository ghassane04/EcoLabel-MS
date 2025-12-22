import { Package, TrendingUp, Database, Users } from 'lucide-react';

const stats = [
  {
    label: 'Produits analysés',
    value: '12,847',
    change: '+12%',
    icon: Package,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100'
  },
  {
    label: 'Scores calculés',
    value: '8,523',
    change: '+8%',
    icon: TrendingUp,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-100'
  },
  {
    label: 'Bases de données',
    value: '6',
    change: '100%',
    icon: Database,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100'
  },
  {
    label: 'Utilisateurs API',
    value: '342',
    change: '+23%',
    icon: Users,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100'
  }
];

export function StatsGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <span className="text-emerald-600 text-sm">{stat.change}</span>
            </div>
            <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
            <p className="text-gray-900 text-2xl">{stat.value}</p>
          </div>
        );
      })}
    </div>
  );
}
