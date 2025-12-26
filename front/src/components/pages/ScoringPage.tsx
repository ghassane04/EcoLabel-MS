import { useState, useEffect } from 'react';
import { Award, Info, Loader2, Sparkles } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';
import { useProduct } from '../../context/ProductContext';

interface ScoreResultUI {
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
  const { lcaResult, parsedProduct, scoreResult: contextScoreResult, setScoreResult, setCurrentStep } = useProduct();
  const [computing, setComputing] = useState(false);
  // Initialize result from context if available
  const [result, setResult] = useState<ScoreResultUI | null>(contextScoreResult ? {
    product: contextScoreResult.product_name,
    grade: contextScoreResult.score_letter as 'A' | 'B' | 'C' | 'D' | 'E',
    score: contextScoreResult.score_numerical,
    confidence: contextScoreResult.confidence_level,
    weights: [],
    explanation: contextScoreResult.explanation
  } : null);

  // Dynamic inputs from LCA or defaults
  const [productName, setProductName] = useState('Sauce Tomate Bio Basilic');
  const [co2, setCo2] = useState(4.5);
  const [water, setWater] = useState(120);
  const [energy, setEnergy] = useState(2.8);

  // Auto-fill from context
  useEffect(() => {
    if (lcaResult) {
      setProductName(lcaResult.product_name);
      setCo2(lcaResult.total_co2_kg);
      setWater(lcaResult.total_water_l);
      setEnergy(lcaResult.total_energy_mj);
    }
  }, [lcaResult]);

  const handleCompute = async () => {
    setComputing(true);
    setCurrentStep('scoring');

    const payload = {
      product_name: productName,
      total_co2: co2,
      total_water: water,
      total_energy: energy,
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

      const scoreResult: ScoreResultUI = {
        product: data.product_name,
        grade: data.score_letter as any,
        score: Math.round(data.score_numerical),
        confidence: Math.round(data.confidence_level * 100),
        weights: [
          { factor: 'Empreinte CO₂', weight: 50, value: co2, contribution: 50 * (co2 / payload.max_co2_ref) },
          { factor: 'Usage d\'eau', weight: 25, value: water, contribution: 25 * (water / payload.max_water_ref) },
          { factor: 'Énergie', weight: 25, value: energy, contribution: 25 * (energy / payload.max_energy_ref) },
        ],
        explanation: data.explanation
      };

      setResult(scoreResult);

      // Store in shared context
      setScoreResult({
        product_name: data.product_name,
        score_letter: data.score_letter,
        score_numerical: data.score_numerical,
        confidence_level: data.confidence_level,
        explanation: data.explanation
      });
      setCurrentStep('done');
    } catch (e) {
      console.error(e);
      alert("Erreur lors du calcul du Score (Port 8004).");
      setCurrentStep('idle');
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
    <div className="p-4 md:p-8">
      <PageHeader
        title="Scoring"
        description="Génération du score environnemental final (A-E) avec pondération scientifique et explications détaillées"
        endpoint="POST /score/compute"
      />

      {/* Alert if we have LCA data */}
      {lcaResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div>
            <p className="text-emerald-900 font-medium">Données LCA chargées automatiquement</p>
            <p className="text-emerald-700 text-sm">CO₂: {lcaResult.total_co2_kg.toFixed(2)}kg | Eau: {lcaResult.total_water_l.toFixed(0)}L | Énergie: {lcaResult.total_energy_mj.toFixed(1)}MJ</p>
          </div>
        </div>
      )}

      {/* Input Indicators */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 md:p-6 mb-6">
        <h3 className="text-base md:text-lg text-gray-900 mb-4">Indicateurs ACV (Entrée du service Scoring)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4">
          <div>
            <label className="text-gray-700 text-sm mb-1 block">CO₂ (kg)</label>
            <input
              type="number"
              value={co2}
              onChange={(e) => setCo2(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-1 block">Eau (L)</label>
            <input
              type="number"
              value={water}
              onChange={(e) => setWater(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="text-gray-700 text-sm mb-1 block">Énergie (MJ)</label>
            <input
              type="number"
              value={energy}
              onChange={(e) => setEnergy(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200 flex items-center justify-center">
            <span className="text-purple-900 text-sm">Réf. Max standard</span>
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



      {/* Result */}
      {result && (
        <div className="space-y-4 md:space-y-6">
          <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border-2 border-emerald-300 p-4 md:p-8">
            <div className="text-center mb-4 md:mb-6">
              <div className="flex justify-center mb-3 md:mb-4">
                <div className={`${gradeColors[result.grade]} text-white w-24 h-24 md:w-32 md:h-32 rounded-2xl md:rounded-3xl flex items-center justify-center text-4xl md:text-6xl shadow-2xl`}>
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
                          style={{ width: `${Math.min(w.contribution * 3, 100)}%` }}
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
