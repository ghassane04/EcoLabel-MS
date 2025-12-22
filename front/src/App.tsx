import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './components/pages/Dashboard';
import { ParserProduitPage } from './components/pages/ParserProduitPage';
import { NLPIngredientsPage } from './components/pages/NLPIngredientsPage';
import { LCALitePage } from './components/pages/LCALitePage';
import { ScoringPage } from './components/pages/ScoringPage';
import { WidgetAPIPage } from './components/pages/WidgetAPIPage';
import { ProvenancePage } from './components/pages/ProvenancePage';

type Page = 'dashboard' | 'parser' | 'nlp' | 'lca' | 'scoring' | 'widget' | 'provenance';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'parser':
        return <ParserProduitPage />;
      case 'nlp':
        return <NLPIngredientsPage />;
      case 'lca':
        return <LCALitePage />;
      case 'scoring':
        return <ScoringPage />;
      case 'widget':
        return <WidgetAPIPage />;
      case 'provenance':
        return <ProvenancePage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="flex-1 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}
