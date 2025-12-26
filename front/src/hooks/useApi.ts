/**
 * React Hooks pour les appels API aux microservices
 */
import { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS, apiCall, checkServiceHealth } from '../config/api';

// Types
export interface ServiceStatus {
    name: string;
    status: 'active' | 'inactive' | 'loading';
    lastCheck?: Date;
}

// Hook: Statut de tous les services
export function useServicesStatus() {
    const [statuses, setStatuses] = useState<Record<string, ServiceStatus>>({
        parser: { name: 'ParserProduit', status: 'loading' },
        nlp: { name: 'NLPIngrédients', status: 'loading' },
        lca: { name: 'LCALite', status: 'loading' },
        scoring: { name: 'Scoring', status: 'loading' },
        widget: { name: 'WidgetAPI', status: 'loading' },
        provenance: { name: 'Provenance', status: 'loading' },
    });

    const checkAllServices = useCallback(async () => {
        const services = [
            { key: 'parser', url: API_ENDPOINTS.parser.health },
            { key: 'nlp', url: API_ENDPOINTS.nlp.health },
            { key: 'lca', url: API_ENDPOINTS.lca.health },
            { key: 'scoring', url: API_ENDPOINTS.scoring.health },
            { key: 'widget', url: API_ENDPOINTS.widget.health },
            { key: 'provenance', url: API_ENDPOINTS.provenance.health },
        ];

        const results = await Promise.all(
            services.map(async (service) => {
                const isHealthy = await checkServiceHealth(service.url);
                return {
                    key: service.key,
                    status: isHealthy ? 'active' as const : 'inactive' as const,
                };
            })
        );

        setStatuses((prev) => {
            const newStatuses = { ...prev };
            results.forEach((result) => {
                newStatuses[result.key] = {
                    ...newStatuses[result.key],
                    status: result.status,
                    lastCheck: new Date(),
                };
            });
            return newStatuses;
        });
    }, []);

    useEffect(() => {
        checkAllServices();
        const interval = setInterval(checkAllServices, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, [checkAllServices]);

    return { statuses, refresh: checkAllServices };
}

// Hook: Parse produit
export function useParseProduct() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const parse = async (file: File) => {
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(API_ENDPOINTS.parser.parse, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Parsing failed');

            const data = await response.json();
            setLoading(false);
            return { data };
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            setLoading(false);
            return { error: message };
        }
    };

    return { parse, loading, error };
}

// Hook: NLP Extract
export function useNLPExtract() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const extract = async (text: string) => {
        setLoading(true);
        setError(null);

        const { data, error: apiError } = await apiCall(
            API_ENDPOINTS.nlp.extract,
            { method: 'POST', body: JSON.stringify({ text }) }
        );

        if (apiError) {
            setError(apiError);
        } else {
            setResult(data);
        }

        setLoading(false);
        return { data, error: apiError };
    };

    return { extract, loading, result, error };
}

// Hook: LCA Calculation
export function useLCACalc() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const calculate = async (ingredients: string[], packaging: string, transport: string) => {
        setLoading(true);
        setError(null);

        const { data, error: apiError } = await apiCall(
            API_ENDPOINTS.lca.calc,
            {
                method: 'POST',
                body: JSON.stringify({ ingredients, packaging, transport })
            }
        );

        if (apiError) {
            setError(apiError);
        } else {
            setResult(data);
        }

        setLoading(false);
        return { data, error: apiError };
    };

    return { calculate, loading, result, error };
}

// Hook: Scoring
export function useScoring() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const computeScore = async (
        product_name: string,
        total_co2: number,
        total_water: number,
        total_energy: number
    ) => {
        setLoading(true);
        setError(null);

        const { data, error: apiError } = await apiCall(
            API_ENDPOINTS.scoring.compute,
            {
                method: 'POST',
                body: JSON.stringify({ product_name, total_co2, total_water, total_energy })
            }
        );

        if (apiError) {
            setError(apiError);
        } else {
            setResult(data);
        }

        setLoading(false);
        return { data, error: apiError };
    };

    return { computeScore, loading, result, error };
}
