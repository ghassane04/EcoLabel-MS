import { useState } from 'react';
import { BrainCircuit, Sparkles, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

interface ExtractedEntity {
  text: string;
  type: 'ingredient' | 'label' | 'origin' | 'packaging';
  normalized: string;
  impact: string;
  confidence: number;
}

export function NLPIngredientsPage() {
  const [inputText, setInputText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [entities, setEntities] = useState<ExtractedEntity[]>([]);

  const handleExtract = async () => {
    if (!inputText.trim()) return;

    setExtracting(true);
    try {
      const response = await fetch('http://localhost:8002/nlp/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) throw new Error("API Error");
      const data = await response.json();

      // Map API response
      // Response: { entities: [{entity, score, word}], normalized_ingredients: [] }
      const mapped: ExtractedEntity[] = data.entities.map((e: any) => ({
        text: e.word,
        type: mapEntityType(e.entity_group),
        normalized: e.word.toLowerCase(), // Simplfied
        impact: 'Impact calculé via LCALite',
        confidence: e.score
      }));

      setEntities(mapped);
    } catch (e) {
      console.error(e);
      alert("Erreur lors de l'appel au service NLP (Port 8002).");
    } finally {
      setExtracting(false);
    }
  };

  const mapEntityType = (group: string): ExtractedEntity['type'] => {
    // Map BERT NER groups to our UI types
    if (group === 'ORG' || group === 'MISC') return 'ingredient';
    if (group === 'LOC') return 'origin';
    return 'label';
  };

  const typeColors = {
    ingredient: 'bg-green-100 text-green-700 border-green-200',
    label: 'bg-blue-100 text-blue-700 border-blue-200',
    origin: 'bg-purple-100 text-purple-700 border-purple-200',
    packaging: 'bg-orange-100 text-orange-700 border-orange-200'
  };

  const typeLabels = {
    ingredient: 'Ingrédient / Entité',
    label: 'Label',
    origin: 'Origine',
    packaging: 'Emballage'
  };

  return (
    <div className="p-8">
      <PageHeader
        title="NLPIngrédients"
        description="Identification et normalisation automatique des ingrédients via NLP et modèles transformers (BERT multilingue)"
        endpoint="POST /nlp/extract"
      />

      {/* Input Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <label className="text-gray-900 mb-2 block">
          Texte brut à analyser
        </label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ex: Sauce tomate bio (92%), basilic frais, huile de palme durable, conditionnée dans un emballage verre recyclable..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
          rows={4}
        />
        <button
          onClick={handleExtract}
          disabled={extracting || !inputText.trim()}
          className="mt-4 bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <BrainCircuit className="w-5 h-5" />
          {extracting ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Analyse en cours...
            </span>
          ) : 'Extraire les entités'}
        </button>
      </div>

      {/* Technology Stack */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-purple-900 mb-1">NLP Engine</p>
          <p className="text-purple-700 text-sm">Hugging Face Transformers</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-900 mb-1">Modèle</p>
          <p className="text-blue-700 text-sm">BERT Multilingue (NER)</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-900 mb-1">Référentiels</p>
          <p className="text-green-700 text-sm">PostgreSQL</p>
        </div>
      </div>

      {/* Results */}
      {entities.length > 0 && (
        <div>
          <h3 className="text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-600" />
            Entités extraites et normalisées ({entities.length})
          </h3>
          <div className="space-y-3">
            {entities.map((entity, index) => (
              <div
                key={index}
                className="bg-white rounded-xl border border-gray-200 p-5"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-lg border text-sm ${typeColors[entity.type]}`}>
                      {typeLabels[entity.type]}
                    </span>
                    <span className="text-gray-900">"{entity.text}"</span>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500 mb-1">Confiance</div>
                    <div className="text-emerald-600">{(entity.confidence * 100).toFixed(0)}%</div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 mb-2">
                  <p className="text-gray-600 text-sm mb-1">Normalisation</p>
                  <p className="text-gray-900">{entity.normalized}</p>
                </div>

                <div className="bg-emerald-50 rounded-lg p-3">
                  <p className="text-emerald-700 text-sm mb-1">Impact environnemental</p>
                  <p className="text-emerald-900">{entity.impact}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
