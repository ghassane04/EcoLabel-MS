import { useState, useEffect } from 'react';
import { BrainCircuit, Sparkles, Loader2, ArrowRight, AlertCircle } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';
import { useProduct } from '../../context/ProductContext';

interface ExtractedEntity {
  text: string;
  type: 'ingredient' | 'label' | 'origin' | 'packaging';
  normalized: string;
  confidence: number;
}

interface NLPIngredientsPageProps {
  onNavigate?: (page: 'lca' | 'scoring' | 'dashboard') => void;
}

export function NLPIngredientsPage({ onNavigate }: NLPIngredientsPageProps) {
  const { parsedProduct, nlpResult: contextNlpResult, setNlpResult, setCurrentStep } = useProduct();
  const [inputText, setInputText] = useState('');
  const [extracting, setExtracting] = useState(false);
  // Initialize entities from context if available
  const [entities, setEntities] = useState<ExtractedEntity[]>(
    contextNlpResult?.entities ? contextNlpResult.entities.map((e: any) => ({
      text: e.word,
      type: 'ingredient' as const,
      normalized: e.word?.toLowerCase() || '',
      confidence: e.score || 0
    })) : []
  );

  // Auto-fill with parsed product text
  useEffect(() => {
    if (parsedProduct?.raw_text) {
      setInputText(parsedProduct.raw_text);
    }
  }, [parsedProduct]);

  const handleExtract = async () => {
    if (!inputText.trim()) return;

    setExtracting(true);
    setCurrentStep('nlp');
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
      const mapped: ExtractedEntity[] = data.entities.map((e: any) => ({
        text: e.word,
        type: mapEntityType(e.entity_group),
        normalized: e.word.toLowerCase(),
        confidence: e.score
      }));

      setEntities(mapped);

      // Store in shared context
      setNlpResult({
        entities: data.entities,
        normalized_ingredients: mapped.map(e => e.normalized)
      });
      setCurrentStep('lca');
    } catch (e) {
      console.error(e);
      alert("Erreur lors de l'appel au service NLP (Port 8002). Le modèle peut prendre 2-3 minutes à charger.");
      setCurrentStep('idle');
    } finally {
      setExtracting(false);
    }
  };

  const mapEntityType = (group: string): ExtractedEntity['type'] => {
    if (group === 'ORG' || group === 'MISC') return 'ingredient';
    if (group === 'LOC') return 'origin';
    return 'label';
  };

  const goToLCA = () => {
    if (onNavigate) onNavigate('lca');
  };

  const typeColors = {
    ingredient: 'bg-green-100 text-green-700 border-green-200',
    label: 'bg-blue-100 text-blue-700 border-blue-200',
    origin: 'bg-purple-100 text-purple-700 border-purple-200',
    packaging: 'bg-orange-100 text-orange-700 border-orange-200'
  };

  const typeLabels = {
    ingredient: 'Ingrédient',
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

      {/* Alert if we have parsed data */}
      {parsedProduct && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div>
            <p className="text-emerald-900 font-medium">Texte du Parser chargé automatiquement</p>
            <p className="text-emerald-700 text-sm">Le texte extrait de votre fichier est prêt à analyser.</p>
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <label className="text-gray-900 mb-2 block">
          Texte brut à analyser
        </label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ex: Sauce tomate bio (92%), basilic frais, huile de palme durable..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
          rows={6}
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



      {/* Results */}
      {entities.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              Entités extraites ({entities.length})
            </h3>
            <button
              onClick={goToLCA}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Étape suivante: LCA <ArrowRight className="w-4 h-4" />
            </button>
          </div>
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
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
