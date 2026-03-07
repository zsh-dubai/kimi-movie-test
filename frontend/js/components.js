const Components = {

    // 临时测试：移除 onerror
    movieCard(movie) {
        const posterUrl = movie.poster_url || '';

        // 如果 poster_url 为空，用占位图
        if (!posterUrl) {
            return `
                <div class="movie-card">
                    <div style="width:200px;height:300px;background:#2a2a2a;display:flex;align-items:center;justify-content:center;color:white;">
                        ${movie.title}
                    </div>
                </div>
            `;
        }

        return `
            <div class="movie-card" onclick="app.showDetail(${movie.id})">
                <img src="${posterUrl}" 
                     alt="${movie.title}" 
                     style="width:200px;height:300px;object-fit:cover;">
                <div class="movie-info">
                    <div class="movie-title">${movie.title}</div>
                    <div class="movie-meta">
                        <span>${movie.rating || 'N/A'}</span>
                    </div>
                </div>
            </div>
        `;
    },


    movieGrid(movies) {
        if (!movies || movies.length === 0) {
            return '<div class="loading">暂无数据</div>';
        }
        return `<div class="movie-grid">${movies.map(m => this.movieCard(m)).join('')}</div>`;
    },

    movieDetail(movie, status = {}) {
        const posterUrl = movie.poster_url || `https://placehold.co/300x450/2a2a2a/FFF?text=Movie+${movie.id}`;

        // 从 status 获取状态，不使用 movie 里的字段
        const isFavorited = status.is_favorite || false;
        const inWatchlist = status.in_watchlist || false;
        const isWatched = status.is_watched || false;

        // 根据状态显示不同的文字和样式
        const favText = isFavorited ? '已收藏' : '收藏';
        const favIcon = isFavorited ? 'fas fa-heart' : 'far fa-heart';
        const favBg = isFavorited ? 'var(--primary)' : 'rgba(255,255,255,0.2)';

        const watchText = inWatchlist ? '已想看' : '想看';
        const watchBg = inWatchlist ? 'var(--primary)' : 'rgba(255,255,255,0.2)';

        const watchedText = isWatched ? '已看' : '标记已看';
        const watchedBg = isWatched ? 'var(--primary)' : 'rgba(255,255,255,0.2)';

        // 判断是否有播放链接
        const hasPlayUrl = movie.play_url && movie.play_url.trim() !== '';
        const playButton = hasPlayUrl
            ? `<a href="${movie.play_url}" target="_blank" style="text-decoration: none;">
                 <button class="btn-primary" style="padding: 0.8rem 1.5rem; background: #e50914; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem;">
                   <i class="fas fa-play"></i> 立即播放
                 </button>
               </a>`
            : `<button disabled style="padding: 0.8rem 1.5rem; background: #555; color: #999; border: none; border-radius: 4px; cursor: not-allowed;">
                 <i class="fas fa-play"></i> 暂无播放源
               </button>`;

        return `
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 2rem;">
                <div>
                    <img src="${posterUrl}" 
                         style="width: 100%; border-radius: 8px;"
                         onerror="this.src='https://placehold.co/300x450/2a2a2a/FFF?text=Movie+${movie.id}'">
                </div>
                <div>
                    <h2>${movie.title}</h2>
                    <p style="color: var(--text-secondary);">${movie.original_title || ''}</p>
                    <div style="margin: 1rem 0;">
                        <span style="color: #ffd700;"><i class="fas fa-star"></i> ${movie.rating}</span>
                        <span style="margin-left: 1rem; color: var(--text-secondary);">${movie.release_date}</span>
                        <span style="margin-left: 1rem; color: var(--text-secondary);">${movie.duration}分钟</span>
                    </div>
                    <div style="margin: 1rem 0;">
                        ${movie.genres ? movie.genres.map(g => `<span style="display: inline-block; padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.1); border-radius: 20px; margin-right: 0.5rem; font-size: 0.85rem;">${g.name}</span>`).join('') : ''}
                    </div>
                    <p style="line-height: 1.8; color: var(--text-secondary);">${movie.description}</p>
                    
                    <!-- 三个操作按钮 -->
                    <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                        <button class="btn-primary" onclick="app.toggleFavorite(${movie.id})" style="padding: 0.8rem 1.5rem; background: ${favBg}; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            <i class="${favIcon}"></i> <span id="fav-text-${movie.id}">${favText}</span>
                        </button>
                        <button class="btn-secondary" onclick="app.addToWatchlist(${movie.id})" style="padding: 0.8rem 1.5rem; background: ${watchBg}; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            <i class="fas fa-bookmark"></i> ${watchText}
                        </button>
                        <button class="btn-secondary" onclick="app.markAsWatched(${movie.id})" style="padding: 0.8rem 1.5rem; background: ${watchedBg}; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            <i class="fas fa-check"></i> ${watchedText}
                        </button>
                        
                        <!-- 播放按钮 -->
                        ${playButton}
                    </div>
                </div>
            </div>
        `;
    },


    reviewItem(review) {
        return `
            <div style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: bold;">${review.user_nickname || review.user}</span>
                    <span style="color: var(--text-secondary); font-size: 0.85rem;">
                        ${new Date(review.created_at).toLocaleDateString()}
                    </span>
                </div>
                <div style="color: #ffd700; margin-bottom: 0.5rem;">
                    ${'★'.repeat(Math.floor(review.rating))}${'☆'.repeat(10 - Math.floor(review.rating))}
                    <span style="color: var(--text-secondary); margin-left: 0.5rem;">${review.rating}分</span>
                </div>
                <p style="line-height: 1.6;">${review.content}</p>
            </div>
        `;
    },

    reviewList(reviews) {
        if (!reviews || reviews.length === 0) {
            return '<div style="padding: 2rem; text-align: center; color: var(--text-secondary);">暂无评论</div>';
        }
        return `<div>${reviews.map(r => this.reviewItem(r)).join('')}</div>`;
    },

    reviewForm(movieId) {
        return `
            <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <h3>发表评论</h3>
                <form id="reviewForm" onsubmit="app.submitReview(event, ${movieId})">
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; margin-bottom: 0.5rem;">评分</label>
                        <select name="rating" style="padding: 0.5rem; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px;">
                            ${[10,9,8,7,6,5,4,3,2,1].map(n => `<option value="${n}">${n}分</option>`).join('')}
                        </select>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; margin-bottom: 0.5rem;">评论内容</label>
                        <textarea name="content" rows="4" style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; resize: vertical; box-sizing: border-box;" placeholder="写下你的观影感受..." required></textarea>
                    </div>
                    <button type="submit" class="btn-primary">发表评论</button>
                </form>
            </div>
        `;
    },

    userStats(stats) {
    return `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">
            <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <div style="font-size: 2rem; color: var(--primary);">${stats.favorites || 0}</div>
                <div style="color: var(--text-secondary);">收藏</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <div style="font-size: 2rem; color: var(--primary);">${stats.watched || 0}</div>
                <div style="color: var(--text-secondary);">已看</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <div style="font-size: 2rem; color: var(--primary);">${stats.reviews || 0}</div>
                <div style="color: var(--text-secondary);">评论</div>
            </div>
        </div>
    `;
},

    historyItem(item) {
        const movie = item.movie;
        const interactionId = item.id;
        return `
            <div style="display: flex; gap: 1rem; padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); cursor: pointer; transition: all 0.3s;" 
                 onmouseover="this.style.background='rgba(255,255,255,0.05)'" 
                 onmouseout="this.style.background='transparent'"
                 onclick="app.showDetail(${movie.id})">
                <img src="${movie.poster_url || `https://placehold.co/100x150/2a2a2a/FFF?text=${movie.id}`}" 
                     style="width: 80px; height: 120px; object-fit: cover; border-radius: 4px;">
                <div style="flex: 1;">
                    <h4 style="margin-bottom: 0.5rem;">${movie.title}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">
                        ${movie.release_date ? movie.release_date.split('-')[0] : ''} · ${movie.genres ? movie.genres.map(g => g.name).join('/') : ''}
                    </p>
                    <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 0.5rem;">
                        ${item.interaction_type === 'favorite' ? '❤️ 收藏' : 
                          item.interaction_type === 'watchlist' ? '🔖 想看' : 
                          item.interaction_type === 'watched' ? '✅ 已看' : '👁️ 浏览过'} 
                        · ${new Date(item.timestamp).toLocaleDateString()}
                    </p>
                </div>
                <button onclick="event.stopPropagation(); app.removeInteraction(${interactionId})" 
                        style="padding: 0.5rem 1rem; background: rgba(255,0,0,0.2); color: #ff6666; border: none; border-radius: 4px; cursor: pointer; align-self: center; opacity: 0; transition: opacity 0.3s;"
                        onmouseover="this.style.opacity='1'"
                        onmouseout="this.style.opacity='0'">
                    移除
                </button>
            </div>
        `;
    },


    tabButtons(activeTab) {
        const tabs = [
            { id: 'history', label: '观看历史', icon: 'fa-history' },
            { id: 'favorites', label: '我的收藏', icon: 'fa-heart' },
            { id: 'watchlist', label: '想看', icon: 'fa-bookmark' }
        ];

        return `
            <div style="display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                ${tabs.map(tab => `
                    <button onclick="app.loadProfile('${tab.id}')" 
                            style="padding: 1rem 2rem; background: none; border: none; color: ${activeTab === tab.id ? 'var(--primary)' : 'var(--text-secondary)'}; 
                                   border-bottom: 2px solid ${activeTab === tab.id ? 'var(--primary)' : 'transparent'}; cursor: pointer; transition: all 0.3s;">
                        <i class="fas ${tab.icon}"></i> ${tab.label}
                    </button>
                `).join('')}
            </div>
        `;
    },
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
            API.getHistory().catch(() => ({ results: [] })),
            API.getFavorites().catch(() => ({ results: [] })),
            API.getWatchlist().catch(() => ({ results: [] }))
        ]);

        const stats = {
            watched: history.results ? history.results.filter(h => h.interaction_type === 'watched').length : 0,
            favorites: favorites.results ? favorites.results.length : 0,
            reviews: 0 // 可以从其他地方获取
        };

        let content = '';
        let data = [];

        switch(tab) {
            case 'history':
                data = history.results || [];
                break;
            case 'favorites':
                data = favorites.results || [];
                break;
            case 'watchlist':
                data = watchlist.results || [];
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

};
