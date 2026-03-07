class MovieApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkAuth();
        this.bindEvents();
        this.loadMovies();

        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    checkAuth() {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
        try {
            this.currentUser = JSON.parse(userStr);
            this.updateUserUI();
        } catch (e) {
            // 如果解析失败，清除存储
            localStorage.removeItem('token');
            localStorage.removeItem('refresh');
            localStorage.removeItem('user');
        }
    }
}


    bindEvents() {
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();  // 添加这行

                const page = e.target.dataset.page;
                console.log('点击导航:', page);  // 添加调试信息

                if (page) {
                    this.navigate(page);
                }
            });
        });

        document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
    }


    updateUserUI() {
        const section = document.getElementById('userSection');
        if (this.currentUser) {
            section.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <a href="#" onclick="app.loadProfile(); return false;" style="color: white; text-decoration: none;">
                        ${this.currentUser.nickname || this.currentUser.username}
                    </a>
                    <button class="btn-login" onclick="app.logout()">退出</button>
                </div>
            `;
        } else {
            section.innerHTML = `<button class="btn-login" onclick="app.showLogin()">登录</button>`;
        }
    }


    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user'); // 清除用户信息
        this.currentUser = null;
        this.updateUserUI();
        this.showToast('已退出登录');
        this.loadMovies();
    }



    async loadMovies() {
        //alert('开始加载电影！');
        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载中...</div>';
        try {
            const data = await API.getMovies({page_size: 100});
            //alert('API返回了 ' + (data.length || data.results?.length) + ' 部电影');
            const movies = Array.isArray(data) ? data : data.results;  // 兼容处理
            //alert('第一部电影：' + movies[0]?.title);
            const html = Components.movieGrid(movies);
            //alert('生成的HTML长度：' + html.length);  // ← 加这行
            main.innerHTML = Components.movieGrid(movies);
            //alert('页面已更新！');  // ← 加这行
        } catch (error) {
            alert('错误：' + error.message);
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }
    async loadRecommendations() {
        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载推荐中...</div>';

        try {
            const data = await API.getRecommendations();
            main.innerHTML = `
                <div style="padding: 2rem 0;">
                    <h2 style="margin-bottom: 1.5rem;">
                        <i class="fas fa-magic" style="color: var(--primary);"></i> 
                        为你推荐
                        <small style="color: var(--text-secondary); font-size: 0.6em; margin-left: 1rem;">
                            ${data.algorithm === 'popular_for_new_user' ? '热门推荐' : '个性化推荐'}
                        </small>
                    </h2>
                    ${Components.movieGrid(data.recommendations)}
                </div>
            `;
        } catch (error) {
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }
    async loadRecommendations() {
        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载推荐中...</div>';

        try {
            const data = await API.getRecommendations();
            main.innerHTML = `
                <div style="padding: 2rem 0;">
                    <h2 style="margin-bottom: 1.5rem;">
                        <i class="fas fa-magic" style="color: var(--primary);"></i> 
                        为你推荐
                        <small style="color: var(--text-secondary); font-size: 0.6em; margin-left: 1rem;">
                            ${data.algorithm === 'popular_for_new_user' ? '热门推荐' : '个性化推荐'}
                        </small>
                    </h2>
                    ${Components.movieGrid(data.recommendations)}
                </div>
            `;
        } catch (error) {
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }

    async navigate(page) {
        console.log('导航到:', page);  // 添加调试信息
        // 更新导航栏激活状态
         document.querySelectorAll('.nav-links a').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });

        switch(page) {
            case 'home':
                // 首页显示全部电影
                this.loadMovies();
                break;
            case 'recommend':
                // 推荐页面
                console.log('加载推荐...');  // 添加调试信息
                if (this.currentUser) {
                    this.loadRecommendations();
                } else {
                    this.showLogin();
                }
                break;
            case 'movies':
            case 'tv':
            case 'anime':
                const typeMap = { movies: 'movie', tv: 'tv', anime: 'anime' };
                await this.loadCategory(typeMap[page]);
                break;
            default:
                this.loadMovies();
        }
    }

    async loadCategory(type) {
        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载中...</div>';

        try {
            let params = {};

            if (type === 'anime') {
                // 动漫 = 动画类型
                params = { genre: '动画' };
            } else if (type === 'tv') {
                // 电视剧 - 暂无数据
                main.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);"><i class="fas fa-tv" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>暂无电视剧数据<br><small>即将上线</small></div>';
                return;
            } else if (type === 'movie') {
                // 电影 - 显示全部
                params = {};
            }

            const data = await API.getMovies(params);
            const movies = Array.isArray(data) ? data : data.results;

            // 添加分类标题
            const titles = { movie: '电影', tv: '电视剧', anime: '动漫' };
            main.innerHTML = `
                <div style="padding: 1rem 0;">
                    <h2 style="margin-bottom: 1.5rem;">
                        <i class="fas fa-film" style="color: var(--primary);"></i> 
                        ${titles[type] || '影视'}
                    </h2>
                    ${Components.movieGrid(movies)}
                </div>
            `;
        } catch (error) {
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }



    async search() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) return;

        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">搜索中...</div>';

        try {
            const data = await API.searchMovies(query);
            main.innerHTML = `<h2 style="margin-bottom: 1rem;">搜索结果: "${query}"</h2>` +
                           Components.movieGrid(data.results);
        } catch (error) {
            main.innerHTML = `<div class="loading">搜索失败</div>`;
        }
    }

    async showDetail(movieId) {
        const modal = document.getElementById('movieModal');
        const body = document.getElementById('modalBody');
        modal.classList.add('active');
        body.innerHTML = '<div class="loading">加载中...</div>';

        try {
            // 先获取电影和评论（核心功能）
            const [movie, reviews] = await Promise.all([
                API.getMovie(movieId),
                API.getReviews(movieId)
            ]);

            // 单独获取状态（失败不影响主功能）
            let status = { is_favorite: false, in_watchlist: false, is_watched: false };
            if (this.currentUser) {
                try {
                    status = await API.checkInteractionStatus(movieId);
                } catch (e) {
                    console.log('获取状态失败:', e);
                }
            }

            console.log('最终状态:', status);
            this.currentMovieStatus = status;

            const movieReviews = reviews.results ? reviews.results.filter(r => r.movie === movieId || r.movie_title === movie.title) : [];

            body.innerHTML = `
                ${Components.movieDetail(movie, status)}
                <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <h3>用户评论 (${movieReviews.length})</h3>
                    ${Components.reviewList(movieReviews)}
                </div>
                ${this.currentUser ? Components.reviewForm(movieId) : '<div style="margin-top: 2rem; text-align: center; color: var(--text-secondary);">登录后发表评论</div>'}
            `;

            if (this.currentUser) {
                this.recordView(movieId);
            }
        } catch (error) {
            console.error('Error:', error);
            body.innerHTML = '<div class="loading">加载失败: ' + error.message + '</div>';
        }
    }



    async submitReview(e, movieId) {
        e.preventDefault();
        const form = e.target;

        try {
            await API.createReview({
                movie: movieId,
                rating: parseFloat(form.rating.value),
                content: form.content.value
            });

            this.showToast('评论发表成功');
            this.showDetail(movieId); // 刷新评论列表
        } catch (error) {
            this.showToast('评论失败: ' + error.message, 'error');
        }
    }

    async recordView(movieId) {
        // 记录浏览历史，用于推荐算法
        try {
            await API.request('/interactions/my/', {
                method: 'POST',
                body: {
                    movie: movieId,
                    interaction_type: 'view'
                }
            });
        } catch (e) {
            // 忽略错误
        }
    }

    closeModal() {
        document.getElementById('movieModal').classList.remove('active');
    }

    showLogin() {
        const modal = document.getElementById('loginModal');
        modal.innerHTML = `
            <div class="modal-content login-box">
                <span class="close" onclick="app.closeLogin()">&times;</span>
                <h2>欢迎回来</h2>
                <form id="loginForm" onsubmit="app.handleLogin(event)">
                    <input type="text" name="username" placeholder="用户名" required>
                    <input type="password" name="password" placeholder="密码" required>
                    <button type="submit" class="btn-primary">登录</button>
                </form>
                <p>还没有账号？<a href="#" onclick="app.showRegister()">立即注册</a></p>
            </div>
        `;
        modal.classList.add('active');
    }

    closeLogin() {
        document.getElementById('loginModal').classList.remove('active');
    }

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;

        try {
            const response = await API.login({
                username: form.username.value,
                password: form.password.value
            });

            localStorage.setItem('token', response.access);
            localStorage.setItem('refresh', response.refresh);
            localStorage.setItem('user', JSON.stringify(response.user)); // 保存用户信息
            this.currentUser = response.user;
            this.updateUserUI();
            this.closeLogin();
            this.showToast('登录成功');
        } catch (error) {
            this.showToast('登录失败: ' + error.message, 'error');
        }
    }
    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;

        try {
            await API.register({
                username: form.username.value,
                password: form.password.value,
                nickname: form.nickname.value,
                email: form.email.value
            });

            this.showToast('注册成功，请登录');
            this.showLogin(); // 切换到登录
        } catch (error) {
            this.showToast('注册失败: ' + error.message, 'error');
        }
    }

    showRegister() {
        const modal = document.getElementById('loginModal');
        modal.innerHTML = `
            <div class="modal-content login-box">
                <span class="close" onclick="app.closeLogin()">&times;</span>
                <h2>注册账号</h2>
                <form id="registerForm" onsubmit="app.handleRegister(event)">
                    <input type="text" name="username" placeholder="用户名" required>
                    <input type="text" name="nickname" placeholder="昵称" required>
                    <input type="email" name="email" placeholder="邮箱" required>
                    <input type="password" name="password" placeholder="密码" required>
                    <button type="submit" class="btn-primary">注册</button>
                </form>
                <p>已有账号？<a href="#" onclick="app.showLogin()">立即登录</a></p>
            </div>
        `;
    }

    async toggleFavorite(movieId) {
    if (!this.currentUser) {
        this.showLogin();
        return;
    }

    try {
        const result = await API.toggleFavorite(movieId);
        this.showToast(result.message);

        // 更新按钮文字
        const btn = document.getElementById(`fav-text-${movieId}`);
        if (btn) {
            btn.textContent = result.status === 'added' ? '已收藏' : '收藏';
        }
    } catch (error) {
        this.showToast('操作失败: ' + error.message, 'error');
    }
}

// 添加方法：检查是否已收藏
    async checkFavorite(movieId) {
        if (!this.currentUser) return false;

        try {
            // 这里简化处理，实际应该调用API检查
            return false;
        } catch (error) {
            return false;
        }
    }


    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.style.borderLeftColor = type === 'error' ? '#e50914' : 'var(--primary)';
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    async addToWatchlist(movieId) {
        if (!this.currentUser) {
            this.showLogin();
            return;
        }

        try {
            const result = await API.addToWatchlist(movieId);
            this.showToast(result.message);

            // 重新获取状态并刷新界面
            const [movie, reviews, status] = await Promise.all([
                API.getMovie(movieId),
                API.getReviews(movieId),
                API.checkInteractionStatus(movieId)
            ]);
            this.currentMovieStatus = status;
            const movieReviews = reviews.results ? reviews.results.filter(r => r.movie === movieId || r.movie_title === movie.title) : [];

            // 重新渲染详情页
            const modalBody = document.getElementById('modalBody');
            modalBody.innerHTML = `
                ${Components.movieDetail(movie, status)}
                <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <h3>用户评论 (${movieReviews.length})</h3>
                    ${Components.reviewList(movieReviews)}
                </div>
                ${this.currentUser ? Components.reviewForm(movieId) : '<div style="margin-top: 2rem; text-align: center; color: var(--text-secondary);">登录后发表评论</div>'}
            `;

        } catch (error) {
            this.showToast('操作失败: ' + error.message, 'error');
        }
    }

    async markAsWatched(movieId) {
        if (!this.currentUser) {
            this.showLogin();
            return;
        }

        try {
            const result = await API.markAsWatched(movieId);
            this.showToast(result.message);

            // 重新获取状态并刷新界面
            const [movie, reviews, status] = await Promise.all([
                API.getMovie(movieId),
                API.getReviews(movieId),
                API.checkInteractionStatus(movieId)
            ]);

            this.currentMovieStatus = status;
            const movieReviews = reviews.results ? reviews.results.filter(r => r.movie === movieId || r.movie_title === movie.title) : [];


            // 重新渲染详情页
            const modalBody = document.getElementById('modalBody');
            modalBody.innerHTML = `
                ${Components.movieDetail(movie, status)}
                <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <h3>用户评论 (${movieReviews.length})</h3>
                    ${Components.reviewList(movieReviews)}
                </div>
                ${this.currentUser ? Components.reviewForm(movieId) : '<div style="margin-top: 2rem; text-align: center; color: var(--text-secondary);">登录后发表评论</div>'}
            `;
        } catch (error) {
            this.showToast('操作失败: ' + error.message, 'error');
        }
    }

    async loadProfile(tab = 'history') {
        if (!this.currentUser) {
            this.showLogin();
            return;
        }

        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载中...</div>';

        try {
            // 获取统计数据
            const [history, favorites, watchlist] = await Promise.all([
                API.getHistory().catch(() => []),
                API.getFavorites().catch(() => []),
                API.getWatchlist().catch(() => [])
            ]);

            // 统一处理数据格式（可能是数组或 {results: [...]}）
            const historyData = Array.isArray(history) ? history : (history.results || []);
            const favoritesData = Array.isArray(favorites) ? favorites : (favorites.results || []);
            const watchlistData = Array.isArray(watchlist) ? watchlist : (watchlist.results || []);

            const stats = {
                watched: historyData.filter(h => h.interaction_type === 'watched').length,
                favorites: favoritesData.length,
                watchlist: watchlistData.length,
            };

            let data = [];
            switch(tab) {
                case 'history':
                    // 只显示 watched（已看），不显示 view（浏览）
                    data = historyData.filter(h => h.interaction_type === 'watched');
                    break;
                case 'favorites':
                    data = favoritesData;
                    break;
                case 'watchlist':
                    data = watchlistData;
                    break;
            }

            main.innerHTML = `
                <div style="padding: 2rem 0;">
                    <h2 style="margin-bottom: 2rem;">
                        <i class="fas fa-user-circle" style="color: var(--primary);"></i> 
                        个人中心
                    </h2>
                    ${Components.userStats(stats)}
                    ${Components.tabButtons(tab)}
                    <div>
                        ${data.length > 0 
                            ? data.map(item => Components.historyItem(item)).join('')
                            : '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">暂无数据</div>'
                        }
                    </div>
                </div>
            `;
        } catch (error) {
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }
    async removeInteraction(interactionId) {
        if (!confirm('确定要移除吗？')) return;

        try {
            await API.request(`/interactions/my/${interactionId}/`, { method: 'DELETE' });
            this.showToast('已移除');
            // 刷新当前标签页
            const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'history';
            this.loadProfile(activeTab);
        } catch (error) {
            this.showToast('移除失败', 'error');
        }
}


}

const app = new MovieApp();
