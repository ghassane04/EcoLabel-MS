import { Clock } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  score: number;
  carbonFootprint: number;
  waterUsage: number;
  energy: number;
  timestamp: Date;
}

interface HistoryListProps {
  history: Product[];
  onProductClick: (product: Product) => void;
}

const gradeColors = {
  A: 'bg-emerald-600',
  B: 'bg-lime-500',
  C: 'bg-yellow-500',
  D: 'bg-orange-500',
  E: 'bg-red-500'
};

export function HistoryList({ history, onProductClick }: HistoryListProps) {
  if (history.length === 0) return null;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-2 mb-4 text-gray-700">
        <Clock className="w-5 h-5" />
        <h2>Historique Récent</h2>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        {history.map((product) => (
          <button
            key={product.id}
            onClick={() => onProductClick(product)}
            className="bg-white/60 backdrop-blur-md rounded-2xl p-4 shadow-lg border border-white/40 hover:shadow-xl hover:scale-105 transition-all text-left"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="text-gray-800 line-clamp-2">{product.name}</div>
              <div className={`${gradeColors[product.grade]} text-white w-8 h-8 rounded-lg flex items-center justify-center ml-2 flex-shrink-0`}>
                {product.grade}
              </div>
            </div>
            <div className="text-emerald-600">{product.score}/100</div>
          </button>
        ))}
      </div>
    </div>
  );
}
