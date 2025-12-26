import { useState, useEffect } from 'react';
import { Leaf, TrendingUp, Loader2, ArrowRight, Sparkles } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';
import { useProduct } from '../../context/ProductContext';

interface LCAResult {
  product: string;
  co2: number;
  water: number;
  energy: number;
  breakdown: {
    category: string;
    co2: number;
    percentage: number;
  }[];
}

interface LCALitePageProps {
  onNavigate?: (page: 'scoring' | 'dashboard') => void;
}

export function LCALitePage({ onNavigate }: LCALitePageProps) {
  const { parsedProduct, nlpResult, lcaResult: contextLcaResult, setLcaResult, setCurrentStep } = useProduct();
  const [calculating, setCalculating] = useState(false);
  // Initialize result from context if available
  const [result, setResult] = useState<LCAResult | null>(contextLcaResult ? {
    product: contextLcaResult.product_name,
    impacts: {
      co2: contextLcaResult.total_co2_kg,
      water: contextLcaResult.total_water_l,
      energy: contextLcaResult.total_energy_mj
    },
    breakdown: []
  } : null);

  // Dynamic input fields
  const [productName, setProductName] = useState('Sauce Tomate Bio Basilic');
  const [ingredients, setIngredients] = useState('Tomates bio (92%), Sucre (5%)');
  const [packaging, setPackaging] = useState('Verre recyclable 720g');
  const [transport, setTransport] = useState('Camion - 250km');

  // Auto-fill from context
  useEffect(() => {
    if (parsedProduct?.raw_text) {
      const text = parsedProduct.raw_text;
      const lines = text.split('\n').map(l => l.trim());

      // Extract product name from first line (e.g., "FICHE PRODUIT - Sauce Tomate Bio Basilic")
      const firstLine = lines.find(l => l.includes('FICHE PRODUIT')) || '';
      if (firstLine) {
        const name = firstLine.replace('FICHE PRODUIT', '').replace(/-/g, '').trim();
        if (name) setProductName(name);
      }

      // Extract ingredients section
      const ingredientIndex = lines.findIndex(l => l.includes('INGRÉDIENTS') || l.includes('INGREDIENTS'));
      if (ingredientIndex !== -1) {
        const ingredientLines: string[] = [];
        for (let i = ingredientIndex + 1; i < lines.length; i++) {
          if (lines[i].startsWith('-')) {
            ingredientLines.push(lines[i].replace('-', '').trim());
          } else if (lines[i] === '' || lines[i].includes(':')) {
            break;
          }
        }
        if (ingredientLines.length > 0) {
          setIngredients(ingredientLines.join(', '));
        }
      }

      // Extract packaging
      const packagingIndex = lines.findIndex(l => l.includes('EMBALLAGE'));
      if (packagingIndex !== -1) {
        const packagingLines: string[] = [];
        for (let i = packagingIndex + 1; i < lines.length; i++) {
          if (lines[i].startsWith('-')) {
            packagingLines.push(lines[i].replace('-', '').trim());
          } else if (lines[i] === '' && packagingLines.length > 0) {
            break;
          }
        }
        if (packagingLines.length > 0) {
          setPackaging(packagingLines.join(' - '));
        }
      }

      // Extract transport
      const transportIndex = lines.findIndex(l => l.includes('TRANSPORT'));
      if (transportIndex !== -1) {
        const transportLines: string[] = [];
        for (let i = transportIndex + 1; i < lines.length; i++) {
          if (lines[i].startsWith('-')) {
            transportLines.push(lines[i].replace('-', '').trim());
          } else if (lines[i] === '' && transportLines.length > 0) {
            break;
          }
        }
        if (transportLines.length > 0) {
          setTransport(transportLines.join(' - '));
        }
      }
    }
    if (nlpResult?.normalized_ingredients?.length) {
      setIngredients(nlpResult.normalized_ingredients.slice(0, 5).join(', '));
    }
  }, [parsedProduct, nlpResult]);

  const handleCalculate = async () => {
    setCalculating(true);
    setCurrentStep('lca');

    // Parse ingredients from text like "Tomates bio (92%), Sucre (5%)"
    const parseIngredients = (text: string) => {
      const items = text.split(',').map(s => s.trim());
      return items.map(item => {
        // Extract name and percentage
        const match = item.match(/^(.+?)\s*\(?\s*(\d+(?:\.\d+)?)\s*%?\s*\)?$/);
        if (match) {
          const name = match[1].toLowerCase().replace(/\s+/g, '_');
          const percent = parseFloat(match[2]) / 100;
          return { name, quantity_kg: percent };
        }
        // Default if no percentage found
        return { name: item.toLowerCase().replace(/\s+/g, '_'), quantity_kg: 0.1 };
      });
    };

    // Parse packaging: "Verre recyclable 720g" or "Matériau: Plastique - Poids: 500g"
    const parsePackaging = (text: string) => {
      let material = 'plastic';
      let weight = 0.5;

      const lowerText = text.toLowerCase();
      if (lowerText.includes('verre') || lowerText.includes('glass')) material = 'glass';
      else if (lowerText.includes('papier') || lowerText.includes('paper')) material = 'paper';
      else if (lowerText.includes('plastique') || lowerText.includes('plastic')) material = 'plastic';
      else if (lowerText.includes('carton')) material = 'cardboard';

      const weightMatch = text.match(/(\d+(?:\.\d+)?)\s*(g|kg)/i);
      if (weightMatch) {
        weight = parseFloat(weightMatch[1]);
        if (weightMatch[2].toLowerCase() === 'g') weight = weight / 1000;
      }

      return { material, weight_kg: weight };
    };

    // Parse transport: "Camion - 250km" or "Distance: 800 km"
    const parseTransport = (text: string) => {
      let distance = 250;
      let mode = 'truck';

      const distMatch = text.match(/(\d+(?:\.\d+)?)\s*(km|kilometre)/i);
      if (distMatch) distance = parseFloat(distMatch[1]);

      const lowerText = text.toLowerCase();
      if (lowerText.includes('avion') || lowerText.includes('air')) mode = 'air';
      else if (lowerText.includes('bateau') || lowerText.includes('ship')) mode = 'ship';
      else if (lowerText.includes('vélo') || lowerText.includes('bike')) mode = 'bike';

      return { distance_km: distance, mode };
    };

    const parsedIngredients = parseIngredients(ingredients);
    const parsedPackaging = parsePackaging(packaging);
    const parsedTransport = parseTransport(transport);

    const payload = {
      product_name: productName,
      ingredients: parsedIngredients,
      packaging: parsedPackaging,
      transport: parsedTransport
    };

    try {
      const response = await fetch('http://localhost:8003/lca/calc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error("API Error");
      const data = await response.json();

      const totalCo2 = data.total_co2_kg;

      const lcaResult = {
        product: data.product_name,
        co2: parseFloat(data.total_co2_kg.toFixed(2)),
        water: parseFloat(data.total_water_l.toFixed(2)),
        energy: parseFloat(data.total_energy_mj.toFixed(2)),
        breakdown: [
          { category: 'Ingrédients', co2: parseFloat((totalCo2 * 0.4).toFixed(1)), percentage: 40 },
          { category: 'Emballage', co2: parseFloat((totalCo2 * 0.4).toFixed(1)), percentage: 40 },
          { category: 'Transport', co2: parseFloat((totalCo2 * 0.2).toFixed(1)), percentage: 20 }
        ]
      };

      setResult(lcaResult);

      // Store in shared context
      setLcaResult({
        product_name: data.product_name,
        total_co2_kg: data.total_co2_kg,
        total_water_l: data.total_water_l,
        total_energy_mj: data.total_energy_mj
      });
      setCurrentStep('scoring');
    } catch (e) {
      console.error(e);
      alert("Erreur lors du calcul ACV (Port 8003).");
      setCurrentStep('idle');
    } finally {
      setCalculating(false);
    }
  };

  const goToScoring = () => {
    if (onNavigate) onNavigate('scoring');
  };

  return (
    <div className="p-8">
      <PageHeader
        title="LCALite"
        description="Analyse du cycle de vie simplifiée - Calcul des impacts CO₂, eau et énergie basé sur AGRIBALYSE et données ADEME"
        endpoint="POST /lca/calc"
      />

      {/* Alert if we have context data */}
      {(parsedProduct || nlpResult) && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div>
            <p className="text-emerald-900 font-medium">Données du pipeline chargées</p>
            <p className="text-emerald-700 text-sm">Les données Parser/NLP sont utilisées pour le calcul.</p>
          </div>
        </div>
      )}

      {/* Input Product */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-gray-900 mb-4">Produit à analyser</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Nom du produit</label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Ingrédients</label>
            <input
              type="text"
              value={ingredients}
              onChange={(e) => setIngredients(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Emballage</label>
            <input
              type="text"
              value={packaging}
              onChange={(e) => setPackaging(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Transport</label>
            <input
              type="text"
              value={transport}
              onChange={(e) => setTransport(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
        <button
          onClick={handleCalculate}
          disabled={calculating}
          className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors flex items-center gap-2"
        >
          <Leaf className="w-5 h-5" />
          {calculating ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Calcul en cours...
            </span>
          ) : 'Lancer le Calcul ACV'}
        </button>
      </div>



      {/* Results */}
      {result && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border border-emerald-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-emerald-600" />
                Résultats de l'analyse — {result.product}
              </h3>
              <button
                onClick={goToScoring}
                className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
              >
                Étape suivante: Scoring <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4 border border-emerald-200">
                <p className="text-gray-600 mb-1">Empreinte CO₂</p>
                <p className="text-3xl text-gray-900">{result.co2}</p>
                <p className="text-gray-600 text-sm">kg CO₂eq</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <p className="text-gray-600 mb-1">Usage d'eau</p>
                <p className="text-3xl text-gray-900">{result.water}</p>
                <p className="text-gray-600 text-sm">Litres</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-yellow-200">
                <p className="text-gray-600 mb-1">Énergie</p>
                <p className="text-3xl text-gray-900">{result.energy}</p>
                <p className="text-gray-600 text-sm">MJ</p>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6">
              <h4 className="text-gray-900 mb-4">Répartition de l'empreinte CO₂</h4>
              <div className="space-y-3">
                {result.breakdown.map((item) => (
                  <div key={item.category}>
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-700">{item.category}</span>
                      <span className="text-gray-900">{item.co2}kg ({item.percentage}%)</span>
                    </div>
                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
