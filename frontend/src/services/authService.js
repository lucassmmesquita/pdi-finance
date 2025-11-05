/**
 * PDI Finance - Authentication Service
 * Serviço de autenticação
 */

import api from './api';

const authService = {
  /**
   * Realiza login
   * @param {string} email - Email do usuário
   * @param {string} senha - Senha do usuário
   * @returns {Promise} Dados do login
   */
  async login(email, senha) {
    try {
      const response = await api.post('/auth/login', { email, senha });
      
      const { access_token, refresh_token, user } = response.data;
      
      // Salvar no localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Erro ao fazer login' };
    }
  },

  /**
   * Realiza logout
   */
  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      // Limpar localStorage sempre
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Obtém dados do usuário atual
   * @returns {Promise} Dados do usuário
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      
      // Atualizar user no localStorage
      localStorage.setItem('user', JSON.stringify(response.data));
      
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Erro ao obter usuário' };
    }
  },

  /**
   * Verifica se usuário está autenticado
   * @returns {boolean}
   */
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  /**
   * Obtém usuário do localStorage
   * @returns {object|null}
   */
  getStoredUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Obtém token de acesso
   * @returns {string|null}
   */
  getAccessToken() {
    return localStorage.getItem('access_token');
  },

  /**
   * Renova o access token usando refresh token
   * @returns {Promise}
   */
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        throw new Error('Refresh token não encontrado');
      }
      
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken,
      });
      
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      
      return access_token;
    } catch (error) {
      // Se refresh falhar, fazer logout
      this.logout();
      throw error;
    }
  },
};

export default authService;