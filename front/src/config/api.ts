/**
 * EcoLabel-MS API Configuration
 * Configuration des URLs des microservices
 */

// Base URLs des microservices
const API_CONFIG = {
    // Infrastructure
    GATEWAY: 'http://localhost:80',       // Traefik API Gateway (si Docker)

    // Microservices (accès direct local)
    PARSER_PRODUIT: 'http://localhost:8001',
    NLP_INGREDIENTS: 'http://localhost:8002',
    LCA_LITE: 'http://localhost:8003',
    SCORING: 'http://localhost:8004',
    WIDGET_API: 'http://localhost:8005',
    PROVENANCE: 'http://localhost:8007',
};

// Endpoints par service
export const API_ENDPOINTS = {
    // ParserProduit - Extraction de données
    parser: {
        base: API_CONFIG.PARSER_PRODUIT,
        parse: `${API_CONFIG.PARSER_PRODUIT}/product/parse`,
        health: `${API_CONFIG.PARSER_PRODUIT}/health`,
    },

    // NLPIngredients - Analyse NLP
    nlp: {
        base: API_CONFIG.NLP_INGREDIENTS,
        extract: `${API_CONFIG.NLP_INGREDIENTS}/nlp/extract`,
        health: `${API_CONFIG.NLP_INGREDIENTS}/health`,
    },

    // LCALite - Analyse Cycle de Vie
    lca: {
        base: API_CONFIG.LCA_LITE,
        calc: `${API_CONFIG.LCA_LITE}/lca/calc`,
        health: `${API_CONFIG.LCA_LITE}/health`,
    },

    // Scoring - Calcul du score
    scoring: {
        base: API_CONFIG.SCORING,
        compute: `${API_CONFIG.SCORING}/score/compute`,
        health: `${API_CONFIG.SCORING}/health`,
    },

    // WidgetAPI - API publique
    widget: {
        base: API_CONFIG.WIDGET_API,
        product: (id: string) => `${API_CONFIG.WIDGET_API}/public/product/${id}`,
        health: `${API_CONFIG.WIDGET_API}/health`,
    },

    // Provenance - Traçabilité
    provenance: {
        base: API_CONFIG.PROVENANCE,
        getScore: (id: string) => `${API_CONFIG.PROVENANCE}/provenance/${id}`,
        health: `${API_CONFIG.PROVENANCE}/health`,
    },
};

// Helper pour vérifier le statut d'un service
export async function checkServiceHealth(healthUrl: string): Promise<boolean> {
    try {
        const response = await fetch(healthUrl, {
            method: 'GET',
            mode: 'cors',
            signal: AbortSignal.timeout(3000)
        });
        return response.ok;
    } catch {
        return false;
    }
}

// Helper pour appeler une API
export async function apiCall<T>(
    url: string,
    options?: RequestInit
): Promise<{ data?: T; error?: string }> {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return { data };
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export default API_CONFIG;
