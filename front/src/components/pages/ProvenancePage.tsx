import { useState, useEffect } from 'react';
import { Database, Search, Loader2, History, BarChart3, RefreshCcw, ChevronRight } from 'lucide-react';
import { PageHeader } from '../layout/PageHeader';

interface ScoreResult {
  id: number;
  product_name: string;
  score_numerical: number;
  score_letter: string;
  confidence_level: number;
  created_at: string | null;
}

interface Stats {
  scores: { count: number; avg_score: number };
  score_distribution: Record<string, number>;
  lca: { count: number; avg_co2: number; avg_water: number; avg_energy: number };
  products_parsed: number;
  emission_factors: number;
}

export function ProvenancePage() {
  const [scoreId, setScoreId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [auditData, setAuditData] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<ScoreResult[]>([]);
  const [history, setHistory] = useState<ScoreResult[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'audit' | 'search' | 'history' | 'stats'>('stats');

  // Load stats on mount
  useEffect(() => {
    loadStats();
    loadHistory();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8007/provenance/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8007/provenance/history/scores?limit=10');
      if (response.ok) {
        const data = await response.json();
        setHistory(data.scores || []);
      }
    } catch (e) {
      console.error('Failed to load history:', e);
    }
  };

  const handleAudit = async () => {
    if (!scoreId.trim()) return;
    setLoading(true);
    setAuditData(null);

    try {
      const response = await fetch(`http://localhost:8007/provenance/${scoreId}`);
      if (!response.ok) throw new Error("Provenance introuvable");
      const data = await response.json();
      setAuditData(data);
    } catch (e) {
      console.error(e);
      alert("Score ID introuvable. Vérifiez l'ID et réessayez.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setSearchResults([]);

    try {
      const response = await fetch(`http://localhost:8007/provenance/search/${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (letter: string) => {
    const colors: Record<string, string> = {
      'A': 'bg-emerald-500',
      'B': 'bg-green-500',
      'C': 'bg-yellow-500',
      'D': 'bg-orange-500',
      'E': 'bg-red-500'
    };
    return colors[letter] || 'bg-gray-500';
  };

  return (
    <div className="p-8">
      <PageHeader
        title="Provenance"
        description="Traçabilité complète et audit des calculs - Recherchez par ID ou nom de produit"
        endpoint="GET /provenance/stats"
      />

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {['stats', 'audit', 'search', 'history'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg transition-colors ${activeTab === tab
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            {tab === 'stats' && 'Statistiques'}
            {tab === 'audit' && 'Audit par ID'}
            {tab === 'search' && 'Recherche'}
            {tab === 'history' && 'Historique'}
          </button>
        ))}
        <button
          onClick={() => { loadStats(); loadHistory(); }}
          className="ml-auto px-3 py-2 text-gray-500 hover:text-gray-700"
        >
          <RefreshCcw className="w-5 h-5" />
        </button>
      </div>

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="w-5 h-5 text-emerald-600" />
                <span className="text-gray-500 text-sm">Scores calculés</span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.scores.count}</p>
              <p className="text-sm text-gray-500">Moyenne: {stats.scores.avg_score}/100</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Database className="w-5 h-5 text-blue-600" />
                <span className="text-gray-500 text-sm">Calculs LCA</span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.lca.count}</p>
              <p className="text-sm text-gray-500">CO₂ moyen: {stats.lca.avg_co2} kg</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Database className="w-5 h-5 text-purple-600" />
                <span className="text-gray-500 text-sm">Produits analysés</span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.products_parsed}</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Database className="w-5 h-5 text-orange-600" />
                <span className="text-gray-500 text-sm">Facteurs d'émission</span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.emission_factors}</p>
            </div>
          </div>

          {/* Score Distribution */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution des scores</h3>
            <div className="flex gap-4">
              {['A', 'B', 'C', 'D', 'E'].map((letter) => (
                <div key={letter} className="flex-1 text-center">
                  <div className={`${getScoreColor(letter)} text-white text-2xl font-bold py-3 rounded-lg mb-2`}>
                    {letter}
                  </div>
                  <p className="text-xl font-semibold text-gray-900">
                    {stats.score_distribution[letter] || 0}
                  </p>
                  <p className="text-sm text-gray-500">produits</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Audit Tab */}
      {activeTab === 'audit' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-gray-900 font-semibold mb-4">Auditer un score par ID</h3>
            <div className="flex gap-4">
              <input
                type="text"
                value={scoreId}
                onChange={(e) => setScoreId(e.target.value)}
                placeholder="Entrez un ID de score (ex: 1, 2, 3...)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                onKeyDown={(e) => e.key === 'Enter' && handleAudit()}
              />
              <button
                onClick={handleAudit}
                disabled={loading || !scoreId}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                Auditer
              </button>
            </div>
          </div>

          {auditData && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Résultat de l'audit</h3>

              {auditData.score && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-700 mb-2">Score</h4>
                  <div className="bg-gray-50 rounded-lg p-4 flex items-center gap-4">
                    <div className={`${getScoreColor(auditData.score.score_letter)} text-white text-2xl font-bold w-14 h-14 rounded-lg flex items-center justify-center`}>
                      {auditData.score.score_letter}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{auditData.score.product_name}</p>
                      <p className="text-sm text-gray-500">
                        Score: {auditData.score.score_numerical}/100 •
                        Confiance: {(auditData.score.confidence_level * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-400">
                        Calculé le: {auditData.score.created_at}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {auditData.lca && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Données LCA associées</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-2xl font-bold text-emerald-600">{auditData.lca.total_co2.toFixed(2)}</p>
                        <p className="text-sm text-gray-500">kg CO₂</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-blue-600">{auditData.lca.total_water.toFixed(1)}</p>
                        <p className="text-sm text-gray-500">L eau</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-orange-600">{auditData.lca.total_energy.toFixed(1)}</p>
                        <p className="text-sm text-gray-500">MJ énergie</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-gray-900 font-semibold mb-4">Rechercher par nom de produit</h3>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Nom du produit (ex: Pizza, Tomato...)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                disabled={loading || !searchQuery}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                Rechercher
              </button>
            </div>
          </div>

          {searchResults.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {searchResults.length} résultat(s) trouvé(s)
              </h3>
              <div className="space-y-2">
                {searchResults.map((score) => (
                  <div
                    key={score.id}
                    className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                    onClick={() => { setScoreId(String(score.id)); setActiveTab('audit'); handleAudit(); }}
                  >
                    <div className={`${getScoreColor(score.score_letter)} text-white font-bold w-10 h-10 rounded flex items-center justify-center`}>
                      {score.score_letter}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{score.product_name}</p>
                      <p className="text-sm text-gray-500">ID: {score.id} • Score: {score.score_numerical}/100</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <History className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Derniers scores calculés</h3>
          </div>

          {history.length > 0 ? (
            <div className="space-y-2">
              {history.map((score) => (
                <div
                  key={score.id}
                  className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => { setScoreId(String(score.id)); setActiveTab('audit'); }}
                >
                  <div className={`${getScoreColor(score.score_letter)} text-white font-bold w-10 h-10 rounded flex items-center justify-center`}>
                    {score.score_letter}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{score.product_name}</p>
                    <p className="text-sm text-gray-500">
                      Score: {score.score_numerical}/100 • Confiance: {(score.confidence_level * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">{score.created_at?.split('T')[0]}</p>
                    <p className="text-xs text-gray-400">ID: {score.id}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Aucun historique disponible</p>
          )}
        </div>
      )}
    </div>
  );
}
