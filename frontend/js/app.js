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

    async loadProfile(tab = 'history') {
        console.log('=== loadProfile 开始 ===');
        console.log('currentUser:', this.currentUser);

        if (!this.currentUser) {
            console.log('currentUser 为空，显示登录');
            this.showLogin();
            return;
        }

        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载中...</div>';

        try {
            console.log('进入 try 块');

        const [history, favorites, watchlist, profileData] = await Promise.all([
            API.getHistory().catch(() => []),
            API.getFavorites().catch(() => []),
            API.getWatchlist().catch(() => []),
            API.getRecommendations().catch(() => null)
        ]);

        const stats = {
            watched: Array.isArray(history) ? history.filter(h => h.interaction_type === 'watched').length : 0,
            favorites: Array.isArray(favorites) ? favorites.length : 0,
            watchlist: Array.isArray(watchlist) ? watchlist.length : 0,
            reviews: 0
        };

        let data = [];
        switch(tab) {
            case 'history': data = Array.isArray(history) ? history : []; break;
            case 'favorites': data = Array.isArray(favorites) ? favorites : []; break;
            case 'watchlist': data = Array.isArray(watchlist) ? watchlist : []; break;
        }

            let profilePanel = '';
            try {
                const userProfile = profileData?.user_profile;
                const userType = profileData?.user_type;
                const userTypeDesc = profileData?.user_type_description;

                profilePanel = `
                    <div style="
                        background: linear-gradient(135deg, rgba(229, 9, 20, 0.1), rgba(0,0,0,0.3));
                        border: 1px solid rgba(229, 9, 20, 0.2);
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 2rem;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h3 style="margin: 0; font-size: 1.1em;">
                                🎭 观影画像 
                                <span style="color: var(--text-secondary); font-size: 0.8em; font-weight: normal;">
                                    ${userTypeDesc || ''}
                                </span>
                            </h3>
                            <span style="
                                background: ${userType === 'active' ? '#4CAF50' : userType === 'warm_start' ? '#FF9800' : '#2196F3'};
                                color: white;
                                padding: 2px 8px;
                                border-radius: 10px;
                                font-size: 0.75em;
                            ">
                                ${userType === 'active' ? '成熟用户' : userType === 'warm_start' ? '新用户' : '冷启动'}
                            </span>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h4 style="font-size: 0.9em; color: var(--text-secondary); margin-bottom: 0.8rem;">类型偏好</h4>
                            ${userProfile?.favorite_genres?.length ? userProfile.favorite_genres.map(g => `
                                <div style="margin-bottom: 0.6rem;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                                        <span style="font-size: 0.85em;">${g.genre}</span>
                                        <span style="font-size: 0.8em; color: #aaa;">${g.count}部 · ${g.percentage}%</span>
                                    </div>
                                    <div style="
                                        height: 6px;
                                        background: rgba(255,255,255,0.1);
                                        border-radius: 3px;
                                        overflow: hidden;
                                    ">
                                        <div style="
                                            width: ${g.percentage}%;
                                            height: 100%;
                                            background: linear-gradient(90deg, #e50914, #ff6b6b);
                                            border-radius: 3px;
                                            transition: width 0.5s ease;
                                        "></div>
                                    </div>
                                </div>
                            `).join('') : '<div style="color: #666; font-size: 0.85em;">暂无类型偏好数据</div>'}
                        </div>
        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                            <div style="text-align: center; padding: 0.8rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #e50914;">${stats.watched}</div>
                                <div style="font-size: 0.8em; color: #888; margin-top: 0.2rem;">已观影</div>
                            </div>
                            <div style="text-align: center; padding: 0.8rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #e50914;">${userProfile?.avg_user_rating || 0}</div>
                                <div style="font-size: 0.8em; color: #888; margin-top: 0.2rem;">平均评分</div>
                            </div>
                            <div style="text-align: center; padding: 0.8rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #e50914;">${stats.favorites}</div>
                                <div style="font-size: 0.8em; color: #888; margin-top: 0.2rem;">收藏</div>
                            </div>
                        </div>
                    </div>
                `;
            } catch (e) {
                console.warn('画像面板渲染失败:', e);
                profilePanel = '';
            }

            const userStatsHtml = typeof Components?.userStats === 'function' ? Components.userStats(stats) : '';
            const tabButtonsHtml = typeof Components?.tabButtons === 'function' ? Components.tabButtons(tab) : '';

            const itemsHtml = data.length > 0 && typeof Components?.historyItem === 'function'
                ? data.map(item => Components.historyItem(item)).join('')
                : '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">暂无数据</div>';

            main.innerHTML = `
                <div style="padding: 2rem 0;">
                    <h2 style="margin-bottom: 2rem;">
                        <i class="fas fa-user-circle" style="color: var(--primary);"></i> 
                        个人中心
                    </h2>
                    ${profilePanel}
                    ${userStatsHtml}
                    ${tabButtonsHtml}
                    <div>${itemsHtml}</div>
                </div>
            `;

            console.log('main.innerHTML 已更新');
        } catch (error) {
            console.error('loadProfile 致命错误:', error);
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }

    bindEvents() {
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                const page = e.target.dataset.page;
                console.log('点击导航:', page);

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
                    <a href="#" onclick="app.navigate('profile'); return false;" style="color: white; text-decoration: none;">
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
        // 在 main.innerHTML 的标题后面添加
            const profileHtml = data.user_profile ? `
                <div style="
                    background: rgba(255,255,255,0.05);
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1.5rem;
                ">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1em;">🎭 你的观影画像</h3>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        ${data.user_profile.favorite_genres.map(g => `
                            <div style="
                                background: rgba(76, 175, 80, 0.2);
                                padding: 4px 12px;
                                border-radius: 12px;
                                font-size: 0.85em;
                            ">
                                ${g.genre} ${g.percentage}%
                            </div>
                        `).join('')}
                    </div>
                    <div style="margin-top: 0.5rem; color: #888; font-size: 0.8em;">
                        平均评分: ${data.user_profile.avg_user_rating} · 
                        已观影: ${data.user_profile.total_watched || 0}部
                    </div>
                </div>
            ` : '';
            // 构建带解释的推荐卡片
            const recommendationsHtml = data.recommendations.map(item => {
                const movie = item.movie;
                const algoColors = {
                    'content_based': '#4CAF50',
                    'collaborative_filtering': '#2196F3',
                    'cold_start_popular': '#FF9800'
                };
                const algoNames = {
                    'content_based': '基于内容',
                    'collaborative_filtering': '协同过滤',
                    'cold_start_popular': '热门推荐'
                };

                return `
                    <div class="recommendation-card" style="position: relative; margin-bottom: 1rem;">
                        ${Components.movieCard(movie)}
                        <div style="
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: ${algoColors[item.algorithm] || '#666'};
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 0.75em;
                            font-weight: bold;
                        ">
                            ${algoNames[item.algorithm] || item.algorithm}
                        </div>
                        <div style="
                            background: rgba(0,0,0,0.8);
                            padding: 10px;
                            border-radius: 0 0 8px 8px;
                            margin-top: -5px;
                        ">
                            <div style="color: #aaa; font-size: 0.85em; margin-bottom: 5px;">
                                💡 ${item.explanation}
                            </div>
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="
                                    flex: 1;
                                    height: 4px;
                                    background: rgba(255,255,255,0.2);
                                    border-radius: 2px;
                                ">
                                    <div style="
                                        width: ${(item.confidence * 100)}%;
                                        height: 100%;
                                        background: linear-gradient(90deg, #4CAF50, #8BC34A);
                                        border-radius: 2px;
                                        transition: width 0.5s;
                                    "></div>
                                </div>
                                <span style="color: #888; font-size: 0.8em;">
                                    ${(item.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            main.innerHTML = `
                <div style="padding: 2rem 0;">
                    <h2 style="margin-bottom: 0.5rem;">
                        <i class="fas fa-magic" style="color: var(--primary);"></i> 
                        为你推荐
                        <small style="color: var(--text-secondary); font-size: 0.6em; margin-left: 1rem;">
                            🎯 个性化推荐
                        </small>
                    </h2>
                    <div style="margin-bottom: 1.5rem; color: var(--text-secondary); font-size: 0.9em;">
                        ${data.user_type_description} · 
                        算法分布：内容推荐 ${(data.algorithm_breakdown.content_based * 100).toFixed(0)}% · 
                        协同过滤 ${(data.algorithm_breakdown.collaborative_filtering * 100).toFixed(0)}% · 
                        热门补充 ${(data.algorithm_breakdown.cold_start_popular * 100).toFixed(0)}%
                    </div>
                    <div class="movie-grid">
                        ${recommendationsHtml}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('推荐加载错误:', error);
            main.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
        }
    }



    // 添加辅助方法
    getAlgorithmColor(algorithm) {
        const colors = {
            'cold_start_popular': '#FF9800',
            'content_based': '#4CAF50',
            'collaborative_filtering': '#2196F3'
        };
        return colors[algorithm] || '#666';
    }

    getAlgorithmName(algorithm) {
        const names = {
            'cold_start_popular': '热门推荐',
            'content_based': '基于内容',
            'collaborative_filtering': '协同过滤'
        };
        return names[algorithm] || algorithm;
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
            case 'profile':
                console.log('准备调用 loadProfile');  //
                this.loadProfile();
                console.log('loadProfile 已调用');    //
                break;
            case 'movies':
            case 'tv':
            case 'anime':
                const typeMap = { movies: 'movie', tv: 'tv', anime: 'anime' };
                await this.loadCategory(typeMap[page]);
                break;
            case 'leaderboard':
                this.showLeaderboard();
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
                           Components.movieGrid(data.results || data);
        } catch (error) {
            main.innerHTML = `<div class="loading">搜索失败</div>`;
        }
    }
    async showLeaderboard() {
        const main = document.getElementById('mainContent');
        main.innerHTML = '<div class="loading">加载排行榜...</div>';

        try {
            const [topRated, mostPopular] = await Promise.all([
                API.getTopRated(),
                API.getMostPopular()
            ]);

            main.innerHTML = `
                <div class="leaderboard-page">
                    ${Components.leaderboard('🏆 评分排行榜', topRated)}
                    ${Components.leaderboard('🔥 热度排行榜', mostPopular)}
                </div>
            `;
        } catch (error) {
            main.innerHTML = '<div class="loading">加载失败</div>';
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
