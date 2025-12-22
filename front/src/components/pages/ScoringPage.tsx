import { useState } from 'react';
import { Award, Info, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

interface ScoreResult {
  product: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  score: number;
  confidence: number;
  weights: {
    factor: string;
    weight: number;
    value: number;
    contribution: number;
  }[];
  explanation: string;
}

export function ScoringPage() {
  const [computing, setComputing] = useState(false);
  const [result, setResult] = useState<ScoreResult | null>(null);

  const handleCompute = async () => {
    setComputing(true);

    // Sample inputs from LCALite (manually forwarded for demo)
    const payload = {
      product_name: 'Sauce Tomate Bio Basilic',
      total_co2: 4.5,   // kg
      total_water: 120, // L
      total_energy: 2.8, // MJ
      max_co2_ref: 10,
      max_water_ref: 500,
      max_energy_ref: 50
    };

    try {
      const response = await fetch('http://localhost:8004/score/compute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error("API Error");
      const data = await response.json();

      setResult({
        product: data.product_name,
        grade: data.score_letter as any,
        score: Math.round(data.score_numerical),
        confidence: Math.round(data.confidence_level * 100),
        weights: [
          { factor: 'Empreinte CO₂', weight: 50, value: payload.total_co2, contribution: 50 * (payload.total_co2 / payload.max_co2_ref) },
          { factor: 'Usage d\'eau', weight: 25, value: payload.total_water, contribution: 25 * (payload.total_water / payload.max_water_ref) },
          { factor: 'Énergie', weight: 25, value: payload.total_energy, contribution: 25 * (payload.total_energy / payload.max_energy_ref) },
        ],
        explanation: data.explanation
      });

    } catch (e) {
      console.error(e);
      alert("Erreur lors du calcul du Score (Port 8004).");
    } finally {
      setComputing(false);
    }
  };

  const gradeColors = {
    A: 'bg-emerald-600',
    B: 'bg-lime-500',
    C: 'bg-yellow-500',
    D: 'bg-orange-500',
    E: 'bg-red-500'
  };

  return (
    <div className="p-8">
      <PageHeader
        title="Scoring"
        description="Génération du score environnemental final (A-E) avec pondération scientifique et explications détaillées"
        endpoint="POST /score/compute"
      />

      {/* Input Indicators */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-gray-900 mb-4">Indicateurs ACV calculés (Entrée du service Scoring)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <p className="text-green-700 text-sm mb-1">CO₂</p>
            <p className="text-green-900">4.5 kg/kg</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <p className="text-blue-700 text-sm mb-1">Eau</p>
            <p className="text-blue-900">120 L/kg</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
            <p className="text-yellow-700 text-sm mb-1">Énergie</p>
            <p className="text-yellow-900">2.8 MJ/kg</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
            <p className="text-purple-700 text-sm mb-1">Référentiel</p>
            <p className="text-purple-900">Ref Max standard</p>
          </div>
        </div>
        <button
          onClick={handleCompute}
          disabled={computing}
          className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors flex items-center gap-2"
        >
          <Award className="w-5 h-5" />
          {computing ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Calcul du score...
            </span>
          ) : 'Générer le score'}
        </button>
      </div>

      {/* Technology */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <p className="text-orange-900 mb-1">Framework</p>
          <p className="text-orange-700 text-sm">FastAPI (Python)</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-900 mb-1">Algorithme</p>
          <p className="text-blue-700 text-sm">Normalisation scikit-learn</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-900 mb-1">Méthode</p>
          <p className="text-green-700 text-sm">Pondération multicritère</p>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border-2 border-emerald-300 p-8">
            <div className="text-center mb-6">
              <div className="flex justify-center mb-4">
                <div className={`${gradeColors[result.grade]} text-white w-32 h-32 rounded-3xl flex items-center justify-center text-6xl shadow-2xl`}>
                  {result.grade}
                </div>
              </div>
              <h3 className="text-gray-900 mb-2">{result.product}</h3>
              <p className="text-gray-600">Score environnemental: {result.score}/100</p>
              <div className="flex items-center justify-center gap-2 mt-2">
                <Info className="w-4 h-4 text-emerald-600" />
                <span className="text-emerald-600 text-sm">Confiance: {result.confidence}%</span>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 mb-6">
              <h4 className="text-gray-900 mb-4">Détails du calcul pondéré</h4>
              <div className="space-y-3">
                {result.weights.map((w) => (
                  <div key={w.factor} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-700">{w.factor}</span>
                        <span className="text-gray-600 text-sm">Poids: {w.weight}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full"
                          style={{ width: `${Math.min(w.contribution * 3, 100)}%` }} // Visual scaling
                        />
                      </div>
                    </div>
                    <div className="text-emerald-600 text-sm w-16 text-right">
                      +{w.contribution.toFixed(1)} pt
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-emerald-100 border border-emerald-300 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-emerald-700 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-emerald-900 mb-1">Explication du score</p>
                  <p className="text-emerald-800 text-sm">{result.explanation}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
