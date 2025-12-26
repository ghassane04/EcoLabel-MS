import { useState, useRef } from 'react';
import { Upload, CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';
import { useProduct } from '../../context/ProductContext';

interface ProductParsed {
  id: number;
  gtin: string | null;
  raw_text: string;
  source_type: string;
  created_at: string;
}

interface ParserProduitPageProps {
  onNavigate?: (page: 'nlp' | 'lca' | 'scoring' | 'dashboard') => void;
}

export function ParserProduitPage({ onNavigate }: ParserProduitPageProps) {
  const { parsedProduct, setParsedProduct, setCurrentStep } = useProduct();
  const [parsing, setParsing] = useState(false);
  // Initialize results from context if available
  const [results, setResults] = useState<ProductParsed[]>(parsedProduct ? [parsedProduct] : []);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setParsing(true);
    setCurrentStep('parsing');
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await fetch('http://localhost:8001/product/parse', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Parsing failed');

      const data = await response.json();
      setResults(data);

      // Store first result in shared context
      if (data.length > 0) {
        setParsedProduct(data[0]);
        setCurrentStep('nlp');
      }
    } catch (error) {
      console.error("Error parsing files:", error);
      alert("Erreur lors de l'analyse des fichiers. Vérifiez que le microservice Parser est lancé.");
      setCurrentStep('idle');
    } finally {
      setParsing(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  const goToNLP = () => {
    if (onNavigate) onNavigate('nlp');
  };

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="ParserProduit"
        description="Extraction automatique des données produits depuis fiches PDF, HTML, images ou codes-barres (GTIN)"
        endpoint="POST /product/parse"
      />

      {/* Upload Section */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-6 md:p-12 mb-6 hover:border-emerald-500 transition-colors">
        <div className="text-center">
          <Upload className="w-12 h-12 md:w-16 md:h-16 text-gray-400 mx-auto mb-3 md:mb-4" />
          <h3 className="text-base md:text-lg text-gray-900 mb-2">Importer des fichiers produits</h3>
          <p className="text-sm md:text-base text-gray-600 mb-4">
            PDF, HTML, images (JPG, PNG) ou fichiers texte
          </p>

          <input
            type="file"
            multiple
            onChange={handleFileChange}
            ref={fileInputRef}
            className="hidden"
            accept="image/*, .html, .txt, .pdf"
          />

          <button
            onClick={triggerUpload}
            disabled={parsing}
            className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {parsing ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Analyse en cours...
              </span>
            ) : 'Sélectionner des fichiers'}
          </button>
        </div>
      </div>



      {/* Results */}
      {results.length > 0 && (
        <div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <h3 className="text-base md:text-lg text-gray-900">
              Résultats bruts ({results.length})
            </h3>
            <button
              onClick={goToNLP}
              className="flex items-center justify-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm md:text-base"
            >
              Étape suivante: NLP <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-4">
            {results.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-xl border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-gray-900">ID: {product.id} - Source: {product.source_type}</h4>
                      <CheckCircle className="w-5 h-5 text-emerald-500" />
                    </div>
                    <p className="text-xs text-gray-500">{new Date(product.created_at).toLocaleString()}</p>
                  </div>
                  {product.gtin && (
                    <span className="bg-gray-100 px-3 py-1 rounded-lg text-gray-700 text-sm">
                      GTIN: {product.gtin}
                    </span>
                  )}
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <p className="text-gray-600 text-sm mb-1 font-semibold">Texte Extrait :</p>
                  <p className="text-gray-800 text-sm font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                    {product.raw_text}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
