import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

interface ProductParsed {
  id: number;
  gtin: string | null;
  raw_text: string;
  source_type: string;
  created_at: string;
}

export function ParserProduitPage() {
  const [parsing, setParsing] = useState(false);
  const [results, setResults] = useState<ProductParsed[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setParsing(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    // Optional: formData.append('gtin', '123456');

    try {
      const response = await fetch('http://localhost:8001/product/parse', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Parsing failed');

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Error parsing files:", error);
      alert("Erreur lors de l'analyse des fichiers. Vérifiez que le microservice Parser est lancé.");
    } finally {
      setParsing(false);
      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="p-8">
      <PageHeader
        title="ParserProduit"
        description="Extraction automatique des données produits depuis fiches PDF, HTML, images ou codes-barres (GTIN)"
        endpoint="POST /product/parse"
      />

      {/* Upload Section */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-12 mb-6 hover:border-emerald-500 transition-colors">
        <div className="text-center">
          <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-gray-900 mb-2">Importer des fichiers produits</h3>
          <p className="text-gray-600 mb-4">
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

      {/* Technology Stack */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-900 mb-1">OCR</p>
          <p className="text-blue-700 text-sm">Tesseract</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-purple-900 mb-1">Web Scraping</p>
          <p className="text-purple-700 text-sm">BeautifulSoup</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-900 mb-1">Base de données</p>
          <p className="text-green-700 text-sm">PostgreSQL</p>
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          <h3 className="text-gray-900 mb-4">
            Résultats bruts ({results.length})
          </h3>
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
