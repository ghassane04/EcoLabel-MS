import { useState } from 'react';
import { Leaf, TrendingUp, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

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

export function LCALitePage() {
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<LCAResult | null>(null);

  const handleCalculate = async () => {
    setCalculating(true);

    // Construct sample payload (hardcoded for demo, but hitting real backend)
    const payload = {
      product_name: "Sauce Tomate Bio Basilic (Demo UI)",
      ingredients: [
        { name: "tomato", quantity_kg: 0.92 },
        { name: "sugar", quantity_kg: 0.05 }
      ],
      packaging: {
        material: "glass",
        weight_kg: 0.72
      },
      transport: {
        distance_km: 250,
        mode: "truck"
      }
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

      // Map API breakdown to UI breakdown if possible, or just mock percentages based on backend totals
      // The backend returns a detailed "breakdown" object if properly implemented

      setResult({
        product: data.product_name,
        co2: parseFloat(data.total_co2_kg.toFixed(2)),
        water: parseFloat(data.total_water_l.toFixed(2)),
        energy: parseFloat(data.total_energy_mj.toFixed(2)),
        breakdown: [
          { category: 'Ingrédients', co2: parseFloat((totalCo2 * 0.4).toFixed(1)), percentage: 40 },
          { category: 'Emballage', co2: parseFloat((totalCo2 * 0.4).toFixed(1)), percentage: 40 },
          { category: 'Transport', co2: parseFloat((totalCo2 * 0.2).toFixed(1)), percentage: 20 }
        ]
      });
    } catch (e) {
      console.error(e);
      alert("Erreur lors du calcul ACV (Port 8003).");
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="p-8">
      <PageHeader
        title="LCALite"
        description="Analyse du cycle de vie simplifiée - Calcul des impacts CO₂, eau et énergie basé sur AGRIBALYSE et données ADEME"
        endpoint="POST /lca/calc"
      />

      {/* Input Product */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-gray-900 mb-4">Produit à analyser (Démo)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Ingrédients normalisés</label>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-900 text-sm">Tomates bio (92%), Sucre (5%)</p>
            </div>
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Emballage</label>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-900 text-sm">Verre recyclable 720g</p>
            </div>
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-2 block">Transport</label>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-900 text-sm">Camion - 250km</p>
            </div>
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

      {/* Technology */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-900 mb-1">Méthode</p>
          <p className="text-green-700 text-sm">ACV Simplifiée</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-900 mb-1">Sources de données</p>
          <p className="text-blue-700 text-sm">AGRIBALYSE, ADEME, FAO</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-purple-900 mb-1">Stockage</p>
          <p className="text-purple-700 text-sm">PostgreSQL + MinIO</p>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border border-emerald-200 p-6">
            <h3 className="text-gray-900 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-emerald-600" />
              Résultats de l'analyse — {result.product}
            </h3>

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
              <h4 className="text-gray-900 mb-4">Répartition de l'empreinte CO₂ (Estimée)</h4>
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
