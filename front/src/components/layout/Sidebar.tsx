import { 
  LayoutDashboard, 
  FileText, 
  BrainCircuit, 
  Leaf, 
  Award, 
  Globe, 
  Database,
  Activity
} from 'lucide-react';

type Page = 'dashboard' | 'parser' | 'nlp' | 'lca' | 'scoring' | 'widget' | 'provenance';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

const menuItems = [
  { id: 'dashboard' as Page, label: 'Dashboard', icon: LayoutDashboard },
  { id: 'parser' as Page, label: 'ParserProduit', icon: FileText },
  { id: 'nlp' as Page, label: 'NLPIngrédients', icon: BrainCircuit },
  { id: 'lca' as Page, label: 'LCALite', icon: Leaf },
  { id: 'scoring' as Page, label: 'Scoring', icon: Award },
  { id: 'widget' as Page, label: 'WidgetAPI', icon: Globe },
  { id: 'provenance' as Page, label: 'Provenance', icon: Database },
];

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 bg-gradient-to-b from-emerald-900 to-emerald-800 text-white flex flex-col">
      <div className="p-6 border-b border-emerald-700">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-emerald-400" />
          <div>
            <h1 className="text-white">EcoLabel-MS</h1>
            <p className="text-emerald-300 text-xs">Microservices Platform</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4">
        <div className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-emerald-700 text-white shadow-lg'
                    : 'text-emerald-100 hover:bg-emerald-800/50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      <div className="p-4 border-t border-emerald-700">
        <div className="bg-emerald-800/50 rounded-lg p-3">
          <div className="flex items-center gap-2 text-emerald-300 mb-1">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-xs">Système opérationnel</span>
          </div>
          <p className="text-xs text-emerald-400">6/6 services actifs</p>
        </div>
      </div>
    </aside>
  );
}
