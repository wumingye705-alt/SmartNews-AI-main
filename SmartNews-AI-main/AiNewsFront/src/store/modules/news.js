import { defineStore } from 'pinia'
import axios from 'axios'
import { apiConfig } from '../../config/api'

// 配置axios请求超时（全局/局部均可，这里局部配置更灵活）
const axiosInstance = axios.create({
  timeout: 10000, // 10秒超时
  baseURL: apiConfig.baseURL
})

export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    categories: [],
    currentCategory: 1,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false
  }),
  
  actions: {
    // 获取新闻分类
    async getCategories() {
      if (this.categoriesLoading) return;
      
      this.categoriesLoading = true;
      
      try {
        const response = await axiosInstance.get('/api/news/categories');
        
        if (response.data && response.data.code === 200) {
          let categoryData = [];
          
          // 兼容不同的数据结构
          if (Array.isArray(response.data.data)) {
            categoryData = response.data.data;
          } else if (response.data.data?.list) {
            categoryData = response.data.data.list;
          } else if (response.data.data?.categories) {
            categoryData = response.data.data.categories;
          }
          
          // 避免"更多"分类ID冲突：找到最大ID+1作为"更多"的ID
          const maxId = categoryData.length 
            ? Math.max(...categoryData.map(item => item.id)) 
            : 9;
          // 添加"更多"分类，ID自动避免冲突
          this.categories = [...categoryData, { id: maxId + 1, name: '更多' }];
          
          // 确保当前分类有效
          if (this.categories.length > 0) {
            const hasCurrent = this.categories.some(item => item.id === this.currentCategory);
            if (!hasCurrent) {
              this.currentCategory = this.categories[0].id;
            }
          }
        }
      } catch (error) {
        console.error('获取新闻分类失败:', error);
        // 设置默认分类兜底
        this.categories = [
          { id: 1, name: '头条' },
          { id: 2, name: '社会' },
          { id: 3, name: '国内' },
          { id: 4, name: '国际' },
          { id: 5, name: '娱乐' },
          { id: 6, name: '体育' },
          { id: 7, name: '科技' }
        ];
      } finally {
        this.categoriesLoading = false;
      }
    },
    
    // 切换新闻分类（仅保留一个正确版本）
    changeCategory(categoryId) {
      // 仅当分类ID不同时才触发请求，避免无效请求
      if (this.currentCategory !== categoryId) {
        this.currentCategory = categoryId;
        this.newsList = [];
        this.finished = false;
        // 切换分类时强制刷新，确保数据最新
        this.getNewsList(true);
      }
    },
    
    // 获取新闻列表
    async getNewsList(isRefresh = false) {
      // 加载中/已加载完则直接返回，避免重复请求
      if (this.loading || (this.finished && !isRefresh)) return;
      
      if (isRefresh) {
        this.refreshing = true;
        this.newsList = [];
        this.finished = false;
      }
      
      this.loading = true;
      
      try {
        const page = isRefresh ? 1 : Math.floor(this.newsList.length / 10) + 1;
        const params = {
          categoryId: this.currentCategory,
          page,
          pageSize: 10
        };
        
        const response = await axiosInstance.get('/api/news/list', { params });
        
        if (response.data && response.data.code === 200) {
          const newsData = response.data.data?.list || [];
          
          // 更新新闻列表
          this.newsList = isRefresh ? newsData : [...this.newsList, ...newsData];
          
          // 判断是否加载完成（数据不足一页则标记为加载完）
          this.finished = newsData.length < params.pageSize;
        } else {
          console.error('获取新闻列表失败：接口返回非200状态码', response.data);
          // 非200状态码也标记为加载完，避免无限请求
          this.finished = true;
        }
      } catch (error) {
        console.error('获取新闻列表失败:', error);
        // 异常时也标记为加载完，避免重复请求
        this.finished = true;
      } finally {
        this.loading = false;
        this.refreshing = false;
      }
    },
    
    // 获取新闻详情
    async getNewsDetail(id) {
      // 清空之前的详情
      this.newsDetail = {};
      
      try {
        const response = await axiosInstance.get(`/api/news/detail`, {
          params: { newsId: id } // 使用params传参更规范
        });
        
        if (response.data && response.data.code === 200) {
          this.newsDetail = response.data.data || {};
          return;
        }
        
        console.error('获取新闻详情失败: 接口返回错误', response.data);
        // 接口返回错误但无异常时，尝试从本地列表获取
        this._setMockNewsDetail(id);
      } catch (error) {
        console.error('获取新闻详情失败:', error);
        // 网络异常时，使用模拟数据兜底
        this._setMockNewsDetail(id);
      }
    },
    
    // 内部方法：设置模拟新闻详情（兜底用）
    _setMockNewsDetail(id) {
      const numericId = Number(id);
      // 从现有列表查找
      const existingNews = this.newsList.find(item => item.id === numericId);
      const categoryId = existingNews ? existingNews.categoryId : this.currentCategory;
      
      if (existingNews) {
        this.newsDetail = {
          ...existingNews,
          content: `这是${existingNews.title}的详细内容。这是一篇关于${this.getCategoryName(categoryId)}的新闻报道，内容丰富详实。
新闻事件发生在最近，引起了广泛关注。多方消息人士透露，该事件的影响将持续一段时间。
专家表示，此类事件的出现有其必然性，也反映了当前社会的某些问题。我们应当理性看待，并从中吸取经验教训。`,
          relatedNews: Array.from({ length: 3 }, (_, i) => ({
            id: 1000 + i,
            title: `相关${this.getCategoryName(categoryId)}新闻${i + 1}`,
            image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`
          }))
        };
      } else {
        // 生成全新模拟数据
        this.newsDetail = {
          id: numericId,
          title: `${this.getCategoryName(categoryId)}新闻${numericId}`,
          description: `这是一条关于${this.getCategoryName(categoryId)}的新闻简介`,
          image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`,
          author: '新闻资讯',
          publishTime: new Date().toLocaleString(),
          categoryId,
          views: Math.floor(Math.random() * 10000),
          content: `这是${this.getCategoryName(categoryId)}新闻${numericId}的详细内容。这是一篇关于${this.getCategoryName(categoryId)}的新闻报道，内容丰富详实。`,
          relatedNews: Array.from({ length: 3 }, (_, i) => ({
            id: 1000 + i,
            title: `相关${this.getCategoryName(categoryId)}新闻${i + 1}`,
            image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`
          }))
        };
      }
    },
    
    // 获取分类名称
    getCategoryName(categoryId) {
      const category = this.categories.find(item => item.id === categoryId);
      return category ? category.name : '未知';
    }
  }
})