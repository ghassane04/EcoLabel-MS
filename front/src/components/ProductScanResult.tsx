import { Leaf, Droplet, Zap, CheckCircle } from 'lucide-react';
import { GradeDisplay } from './GradeDisplay';
import { MetricBar } from './MetricBar';

interface Product {
  name: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  score: number;
  carbonFootprint: number;
  waterUsage: number;
  energy: number;
  reliability: number;
  ingredients: { name: string; impact: string }[];
}

interface ProductScanResultProps {
  product: Product;
}

export function ProductScanResult({ product }: ProductScanResultProps) {
  return (
    <div className="space-y-6 mb-8">
      {/* Main Grade Card */}
      <div className="bg-white/60 backdrop-blur-md rounded-3xl p-8 shadow-xl border border-white/40">
        <div className="text-center mb-6">
          <p className="text-gray-600 mb-4">{product.name}</p>
        </div>

        {/* Grade Display */}
        <GradeDisplay grade={product.grade} />

        {/* Score Gauge */}
        <div className="mt-8 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">Score Écologique</span>
            <span className="text-emerald-600">{product.score}/100</span>
          </div>
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full transition-all duration-1000"
              style={{ width: `${product.score}%` }}
            />
          </div>
        </div>

        {/* Metrics */}
        <div className="space-y-4">
          <MetricBar
            icon={<Leaf className="w-5 h-5" />}
            label="Empreinte Carbone"
            value={product.carbonFootprint}
            level={product.carbonFootprint < 35 ? 'Faible' : product.carbonFootprint < 65 ? 'Moyen' : 'Élevé'}
          />
          <MetricBar
            icon={<Droplet className="w-5 h-5" />}
            label="Usage d'Eau"
            value={product.waterUsage}
            level={product.waterUsage < 35 ? 'Faible' : product.waterUsage < 65 ? 'Moyen' : 'Élevé'}
          />
          <MetricBar
            icon={<Zap className="w-5 h-5" />}
            label="Énergie"
            value={product.energy}
            level={product.energy < 35 ? 'Faible' : product.energy < 65 ? 'Moyen' : 'Élevé'}
          />
        </div>
      </div>

      {/* Ingredients Details Card */}
      <div className="bg-white/60 backdrop-blur-md rounded-3xl p-6 shadow-xl border border-white/40">
        <h3 className="text-gray-800 mb-4 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-emerald-600" />
          Ingrédients Clés
        </h3>
        <div className="space-y-3">
          {product.ingredients.map((ingredient, index) => (
            <div key={index} className="bg-white/80 rounded-xl p-4">
              <div className="text-gray-800">{ingredient.name}</div>
              <div className="text-gray-600 mt-1">{ingredient.impact}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Reliability Badge */}
      <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-2xl p-5 shadow-lg">
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6" />
            <span>Indice de Fiabilité</span>
          </div>
          <span className="text-2xl">{product.reliability}%</span>
        </div>
      </div>
    </div>
  );
}
