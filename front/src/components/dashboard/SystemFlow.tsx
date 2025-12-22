import { ArrowRight } from 'lucide-react';

export function SystemFlow() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-gray-900 mb-6">Flux de données du système</h3>
      
      <div className="space-y-4">
        {/* Flow 1 */}
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg flex-1 text-center">
            Import produit
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="bg-emerald-100 text-emerald-700 px-4 py-2 rounded-lg flex-1 text-center">
            ParserProduit
          </div>
        </div>

        {/* Flow 2 */}
        <div className="flex items-center gap-3">
          <div className="bg-emerald-100 text-emerald-700 px-4 py-2 rounded-lg flex-1 text-center">
            Données normalisées
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="bg-purple-100 text-purple-700 px-4 py-2 rounded-lg flex-1 text-center">
            NLPIngrédients
          </div>
        </div>

        {/* Flow 3 */}
        <div className="flex items-center gap-3">
          <div className="bg-purple-100 text-purple-700 px-4 py-2 rounded-lg flex-1 text-center">
            Ingrédients extraits
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="bg-green-100 text-green-700 px-4 py-2 rounded-lg flex-1 text-center">
            LCALite
          </div>
        </div>

        {/* Flow 4 */}
        <div className="flex items-center gap-3">
          <div className="bg-green-100 text-green-700 px-4 py-2 rounded-lg flex-1 text-center">
            Indicateurs ACV
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg flex-1 text-center">
            Scoring
          </div>
        </div>

        {/* Flow 5 */}
        <div className="flex items-center gap-3">
          <div className="bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg flex-1 text-center">
            Score A-E
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="bg-orange-100 text-orange-700 px-4 py-2 rounded-lg flex-1 text-center">
            WidgetAPI
          </div>
        </div>

        {/* Provenance - parallel */}
        <div className="border-t border-gray-200 pt-4 mt-4">
          <div className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-center">
            <span className="mr-2">🔒</span>
            Provenance — Traçabilité complète de chaque étape
          </div>
        </div>
      </div>
    </div>
  );
}
