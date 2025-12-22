import { useState } from 'react';
import { Database, GitBranch, History, Shield, Search, Loader2 } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

export function ProvenancePage() {
  const [scoreId, setScoreId] = useState('');
  const [auditData, setAuditData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAudit = async () => {
    if (!scoreId.trim()) return;
    setLoading(true);
    setAuditData(null);

    try {
      const response = await fetch(`http://localhost:8006/provenance/${scoreId}`);
      if (!response.ok) throw new Error("Provenance introuvable");
      const data = await response.json();
      setAuditData(data);
    } catch (e) {
      console.error(e);
      // Show dummy data for demo if not found or server error
      // (User likely won't have valid score IDs without running the full pipeline manually first)
      alert("Provenance introuvable pour cet ID. Assurez-vous d'avoir enregistré un score via le service Provenance.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <PageHeader
        title="Provenance"
        description="Traçabilité complète et versioning des données, modèles et facteurs de calcul pour garantir la reproductibilité scientifique"
        endpoint="GET /provenance/:score_id"
      />

      {/* Audit Search */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-gray-900 mb-4">Auditer un calcul de score</h3>
        <div className="flex gap-4">
          <input
            type="text"
            value={scoreId}
            onChange={(e) => setScoreId(e.target.value)}
            placeholder="Entrez un ID de score (ex: 12345)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            onClick={handleAudit}
            disabled={loading || !scoreId}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <Search className="w-5 h-5" />
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Auditer'}
          </button>
        </div>
      </div>

      {auditData && (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-6">
          <pre className="text-xs">{JSON.stringify(auditData, null, 2)}</pre>
        </div>
      )}

      {/* Technology Stack */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-purple-900 mb-1">Versioning</p>
          <p className="text-purple-700 text-sm">DVC (Data Version Control)</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-900 mb-1">Tracking</p>
          <p className="text-blue-700 text-sm">MLflow</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-900 mb-1">Stockage</p>
          <p className="text-green-700 text-sm">MinIO (Artefacts)</p>
        </div>
      </div>

      {/* Traceability Example (Static for Edu) */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-6 h-6 text-blue-600" />
          <h3 className="text-gray-900">Exemple de traçabilité complète (Statique)</h3>
        </div>
        {/* ... existing static content could go here if user wants to keep the edu part ... */}
        <p className="text-sm text-gray-600">
          La traçabilité garantit que chaque score est recalculable.
        </p>
      </div>

    </div>
  );
}
