import { ReactNode } from 'react';

interface MetricBarProps {
  icon: ReactNode;
  label: string;
  value: number;
  level: string;
}

const getLevelColor = (value: number) => {
  if (value < 35) return 'from-emerald-400 to-emerald-600';
  if (value < 65) return 'from-yellow-400 to-yellow-600';
  return 'from-red-400 to-red-600';
};

const getLevelTextColor = (value: number) => {
  if (value < 35) return 'text-emerald-600';
  if (value < 65) return 'text-yellow-600';
  return 'text-red-600';
};

export function MetricBar({ icon, label, value, level }: MetricBarProps) {
  return (
    <div className="bg-white/80 rounded-xl p-4">
      <div className="flex items-center gap-3 mb-2">
        <div className="text-emerald-600">{icon}</div>
        <div className="flex-1 flex justify-between items-center">
          <span className="text-gray-700">{label}</span>
          <span className={`${getLevelTextColor(value)}`}>{level}</span>
        </div>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${getLevelColor(value)} rounded-full transition-all duration-1000`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
