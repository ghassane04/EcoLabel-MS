import { createContext, useContext, useState, ReactNode } from 'react';

// Types
export interface ParsedProduct {
    id: number;
    gtin: string | null;
    raw_text: string;
    source_type: string;
    created_at: string;
}

export interface NLPResult {
    entities: Array<{
        word: string;
        entity_group: string;
        score: number;
    }>;
    normalized_ingredients: string[];
}

export interface LCAResult {
    product_name: string;
    total_co2_kg: number;
    total_water_l: number;
    total_energy_mj: number;
}

export interface ScoreResult {
    product_name: string;
    score_letter: string;
    score_numerical: number;
    confidence_level: number;
    explanation: string;
}

interface ProductContextType {
    // Parser data
    parsedProduct: ParsedProduct | null;
    setParsedProduct: (product: ParsedProduct | null) => void;

    // NLP data
    nlpResult: NLPResult | null;
    setNlpResult: (result: NLPResult | null) => void;

    // LCA data
    lcaResult: LCAResult | null;
    setLcaResult: (result: LCAResult | null) => void;

    // Score data
    scoreResult: ScoreResult | null;
    setScoreResult: (result: ScoreResult | null) => void;

    // Pipeline status
    currentStep: 'idle' | 'parsing' | 'nlp' | 'lca' | 'scoring' | 'done';
    setCurrentStep: (step: 'idle' | 'parsing' | 'nlp' | 'lca' | 'scoring' | 'done') => void;

    // Clear all data
    clearAll: () => void;
}

const ProductContext = createContext<ProductContextType | undefined>(undefined);

export function ProductProvider({ children }: { children: ReactNode }) {
    const [parsedProduct, setParsedProduct] = useState<ParsedProduct | null>(null);
    const [nlpResult, setNlpResult] = useState<NLPResult | null>(null);
    const [lcaResult, setLcaResult] = useState<LCAResult | null>(null);
    const [scoreResult, setScoreResult] = useState<ScoreResult | null>(null);
    const [currentStep, setCurrentStep] = useState<'idle' | 'parsing' | 'nlp' | 'lca' | 'scoring' | 'done'>('idle');

    const clearAll = () => {
        setParsedProduct(null);
        setNlpResult(null);
        setLcaResult(null);
        setScoreResult(null);
        setCurrentStep('idle');
    };

    return (
        <ProductContext.Provider
            value={{
                parsedProduct,
                setParsedProduct,
                nlpResult,
                setNlpResult,
                lcaResult,
                setLcaResult,
                scoreResult,
                setScoreResult,
                currentStep,
                setCurrentStep,
                clearAll,
            }}
        >
            {children}
        </ProductContext.Provider>
    );
}

export function useProduct() {
    const context = useContext(ProductContext);
    if (context === undefined) {
        throw new Error('useProduct must be used within a ProductProvider');
    }
    return context;
}
