interface GradeDisplayProps {
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
}

const gradeColors = {
  A: 'from-emerald-600 to-emerald-700',
  B: 'from-lime-500 to-lime-600',
  C: 'from-yellow-500 to-yellow-600',
  D: 'from-orange-500 to-orange-600',
  E: 'from-red-500 to-red-600'
};

const gradeShadows = {
  A: 'shadow-emerald-200',
  B: 'shadow-lime-200',
  C: 'shadow-yellow-200',
  D: 'shadow-orange-200',
  E: 'shadow-red-200'
};

export function GradeDisplay({ grade }: GradeDisplayProps) {
  return (
    <div className="flex justify-center">
      <div className="relative">
        {/* Leaf-shaped container */}
        <div
          className={`w-40 h-40 bg-gradient-to-br ${gradeColors[grade]} rounded-[40%_60%_60%_40%/60%_30%_70%_40%] shadow-2xl ${gradeShadows[grade]} flex items-center justify-center transform rotate-[-15deg] transition-all duration-500`}
        >
          <div className="transform rotate-[15deg]">
            <div className="text-white text-6xl tracking-tight">{grade}</div>
          </div>
        </div>
        
        {/* Leaf stem */}
        <div className={`absolute top-0 right-12 w-1 h-8 bg-gradient-to-b ${gradeColors[grade]} transform -translate-y-6 rotate-45`} />
      </div>
    </div>
  );
}
