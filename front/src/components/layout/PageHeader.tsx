import { Code } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  description: string;
  endpoint: string;
}

export function PageHeader({ title, description, endpoint }: PageHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h1 className="text-gray-900 mb-2">{title}</h1>
          <p className="text-gray-600 max-w-3xl">{description}</p>
        </div>
        <div className="bg-gray-900 text-emerald-400 px-4 py-2 rounded-lg flex items-center gap-2 font-mono text-sm">
          <Code className="w-4 h-4" />
          {endpoint}
        </div>
      </div>
      <div className="h-1 bg-gradient-to-r from-emerald-500 to-green-500 rounded-full w-24" />
    </div>
  );
}
