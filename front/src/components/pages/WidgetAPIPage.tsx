import { useState } from 'react';
import { Globe, Code, Eye, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';
import { ProductScanResult } from '../ProductScanResult';
import { SearchBar } from '../SearchBar';
import { HistoryList } from '../HistoryList';

interface Product {
  id: string;
  name: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  score: number;
  carbonFootprint: number;
  waterUsage: number;
  energy: number;
  reliability: number;
  ingredients: { name: string; impact: string }[];
  timestamp: Date;
}

const SAMPLE_PRODUCT: Product = {
  id: 'demo',
  name: 'Produit Démo (Statique)',
  grade: 'A',
  score: 92,
  carbonFootprint: 25,
  waterUsage: 55,
  energy: 30,
  reliability: 90,
  ingredients: [
    { name: 'Tomates bio', impact: 'Très faible empreinte carbone' },
    { name: 'Sel de mer', impact: 'Impact minimal sur l\'eau' }
  ],
  timestamp: new Date()
};

export function WidgetAPIPage() {
  const [view, setView] = useState<'api' | 'preview'>('preview'); // Default to preview for user interaction
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setCurrentProduct(null);

    try {
      const response = await fetch(`http://localhost:8005/public/product/${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error("Produit non trouvé");
      }
      const data = await response.json();

      // Map API response to UI Product model
      // Note: Backend currently gives { product_name, score_letter, score_numerical, confidence, created_at }
      const mappedProduct: Product = {
        id: Date.now().toString(),
        name: data.product_name,
        grade: data.score_letter as any,
        score: Math.round(data.score_numerical),
        // Placeholders based on score mostly (since backend doesn't send details yet)
        carbonFootprint: Math.round(100 - data.score_numerical) * 2,
        waterUsage: Math.round(100 - data.score_numerical) * 3,
        energy: Math.round(100 - data.score_numerical) * 1.5,
        reliability: Math.round(data.confidence * 100),
        ingredients: [
          { name: 'Données ACV', impact: 'Calculé via LCALite' },
          { name: 'Analyse NLP', impact: 'Ingrédients extraits' }
        ],
        timestamp: new Date(data.created_at)
      };

      setCurrentProduct(mappedProduct);
    } catch (err) {
      setError("Produit introuvable. Avez-vous analysé ce produit via le Parser ?");
    } finally {
      setLoading(false);
    }
  };

  const apiExample = `// REST API
GET /public/product/:id

// Response
{
  "id": "3245670123456",
  "name": "Sauce Tomate Bio Basilic",
  "grade": "A",
  "score": 92,
  "confidence": 90,
  "carbonFootprint": 450,
  "waterUsage": 120,
  "energy": 2.8,
  "ingredients": [...],
  "breakdown": {...}
}`;

  const graphqlExample = `# GraphQL Query
query GetProductScore($gtin: String!) {
  product(gtin: $gtin) {
    name
    grade
    score
    confidence
    impacts {
      carbon
      water
      energy
    }
  }
}`;

  const embedCode = `<!-- Intégration Widget -->
<div id="ecolabel-widget" data-gtin="3245670123456"></div>
<script src="https://api.ecolabel.io/widget.js"></script>`;

  return (
    <div className="p-8">
      <PageHeader
        title="WidgetAPI"
        description="API publique REST et GraphQL pour intégration dans sites e-commerce et applications mobiles"
        endpoint="GET /public/product/:id"
      />

      {/* View Toggle */}
      <div className="bg-white rounded-xl border border-gray-200 p-2 mb-6 inline-flex gap-2">
        <button
          onClick={() => setView('api')}
          className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${view === 'api'
              ? 'bg-emerald-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
            }`}
        >
          <Code className="w-4 h-4" />
          Documentation API
        </button>
        <button
          onClick={() => setView('preview')}
          className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${view === 'preview'
              ? 'bg-emerald-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
            }`}
        >
          <Eye className="w-4 h-4" />
          Aperçu Widget
        </button>
      </div>

      {view === 'api' ? (
        <div className="space-y-6">
          {/* Technology */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-blue-900 mb-1">Frontend</p>
              <p className="text-blue-700 text-sm">React + Tailwind CSS</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <p className="text-purple-900 mb-1">API Backend</p>
              <p className="text-purple-700 text-sm">FastAPI + GraphQL</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-green-900 mb-1">Base de données</p>
              <p className="text-green-700 text-sm">PostgreSQL (Public)</p>
            </div>
          </div>

          {/* REST API */}
          <div className="bg-gray-900 rounded-xl p-6 text-white">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-emerald-400" />
              <h3 className="text-white">REST API</h3>
            </div>
            <pre className="text-emerald-300 text-sm overflow-x-auto">
              <code>{apiExample}</code>
            </pre>
          </div>

          {/* GraphQL */}
          <div className="bg-gray-900 rounded-xl p-6 text-white">
            <div className="flex items-center gap-2 mb-4">
              <Code className="w-5 h-5 text-purple-400" />
              <h3 className="text-white">GraphQL API</h3>
            </div>
            <pre className="text-purple-300 text-sm overflow-x-auto">
              <code>{graphqlExample}</code>
            </pre>
          </div>

          {/* Embed Widget */}
          <div className="bg-gray-900 rounded-xl p-6 text-white">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-orange-400" />
              <h3 className="text-white">Widget Embed</h3>
            </div>
            <pre className="text-orange-300 text-sm overflow-x-auto">
              <code>{embedCode}</code>
            </pre>
          </div>

          {/* Rate Limits */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-gray-900 mb-4">Limites et Quotas</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
                <p className="text-emerald-700 text-sm mb-1">Free Tier</p>
                <p className="text-emerald-900">1,000 req/jour</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-blue-700 text-sm mb-1">Business</p>
                <p className="text-blue-900">50,000 req/jour</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <p className="text-purple-700 text-sm mb-1">Enterprise</p>
                <p className="text-purple-900">Illimité</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-md mx-auto">
          <div className="bg-gradient-to-br from-emerald-50 via-white to-green-50 rounded-xl p-6 border-2 border-emerald-200 shadow-xl">
            <h3 className="text-gray-900 mb-4 text-center font-bold text-lg">
              Widget Public — Consommateurs
            </h3>

            <SearchBar onSearch={handleSearch} />

            {loading && (
              <div className="flex justify-center p-8 text-emerald-600">
                <Loader2 className="w-8 h-8 animate-spin" />
              </div>
            )}

            {error && (
              <div className="text-center p-4 text-red-500 bg-red-50 rounded-lg mb-4">
                {error}
              </div>
            )}

            {currentProduct && !loading && <ProductScanResult product={currentProduct} />}

            {!currentProduct && !loading && !error && (
              <div className="text-center text-gray-400 text-sm p-4">
                Essayez de rechercher "Tomato Sauce"
              </div>
            )}

            <HistoryList history={[]} onProductClick={() => { }} />
          </div>
        </div>
      )}
    </div>
  );
}
