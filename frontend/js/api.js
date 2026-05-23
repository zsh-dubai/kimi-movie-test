// 添加环境判断
const getBaseUrl = () => {
    // 本地开发环境判断
    if (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.protocol === 'file:') {  // 直接打开HTML文件
        return 'http://127.0.0.1:8000/api';
    }
    // 生产环境
    return 'http://8.163.56.200/api';
};

const API_BASE_URL = getBaseUrl();

class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem('token');

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers
            },
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.error || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    static getReviews(movieId) {
        return this.request(`/interactions/reviews/?movie=${movieId}`);
    }

   static getRecommendations() {
        return this.request('/recommendations/for-you/');
    }
    static getTrending() {
        return this.request('/recommendations/trending/');
    }

    static getSimilar(movieId) {
        return this.request(`/recommendations/similar/${movieId}/`);
    }

    static createReview(data) {
        return this.request('/interactions/reviews/', {
            method: 'POST',
            body: data
        });
    }

    static login(credentials) {
        return this.request('/users/login/', {
            method: 'POST',
            body: credentials
        });
    }

    static register(userData) {
        return this.request('/users/register/', {
            method: 'POST',
            body: userData
        });
    }

    static getMovies(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/movies/?${query}`);

    }

    static getMovie(id) {
        return this.request(`/movies/${id}/`);
    }

    static searchMovies(query) {
        return this.request(`/movies/?search=${encodeURIComponent(query)}`);
    }

    static toggleFavorite(movieId) {
        return this.request('/interactions/my/toggle_favorite/', {
            method: 'POST',
            body: { movie: movieId }
        });
    }
    static checkInteractionStatus(movieId) {
        return this.request(`/interactions/my/check_status/?movie=${movieId}`);
    }

    static rateMovie(movieId, rating) {
        return this.request(`/movies/${movieId}/rate/`, {
            method: 'POST',
            body: { rating }
        });
    }
    static getFavorites() {
        return this.request('/interactions/my/favorites/');
    }

    static getHistory() {
        return this.request('/interactions/my/history/');
    }

    static getWatchlist() {
        return this.request('/interactions/my/watchlist/');
    }

    static addToWatchlist(movieId) {
        return this.request('/interactions/my/toggle_watchlist/',{
            method: 'POST',
            body: {
                movie: movieId,
                interaction_type: 'watchlist'
            }
        });
    }

    static markAsWatched(movieId) {
        return this.request('/interactions/my/toggle_watched/',{
            method: 'POST',
            body: {
                movie: movieId,
                interaction_type: 'watched'
            }
        });
    }

}
