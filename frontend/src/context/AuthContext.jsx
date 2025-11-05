/**
 * PDI Finance - Auth Context
 * Context para gerenciar estado de autenticação
 */

import { createContext, useState, useEffect } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Carregar usuário ao montar o componente
  useEffect(() => {
    loadUser();
  }, []);

  /**
   * Carrega usuário do localStorage ou da API
   */
  async function loadUser() {
    try {
      if (authService.isAuthenticated()) {
        // Tentar pegar do localStorage primeiro
        const storedUser = authService.getStoredUser();
        
        if (storedUser) {
          setUser(storedUser);
        }
        
        // Buscar dados atualizados da API
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        } catch (err) {
          // Se falhar, usar dados do localStorage
          console.error('Erro ao carregar usuário da API:', err);
        }
      }
    } catch (err) {
      console.error('Erro ao carregar usuário:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  /**
   * Realiza login
   */
  async function login(email, senha) {
    try {
      setLoading(true);
      setError(null);
      
      const data = await authService.login(email, senha);
      setUser(data.user);
      
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  /**
   * Realiza logout
   */
  async function logout() {
    try {
      setLoading(true);
      await authService.logout();
      setUser(null);
    } catch (err) {
      console.error('Erro ao fazer logout:', err);
    } finally {
      setLoading(false);
    }
  }

  /**
   * Verifica se usuário tem permissão
   */
  function hasPermission(permission) {
    if (!user) return false;
    
    // Admin tem todas as permissões
    if (user.perfil === 'Admin') return true;
    
    // Verificar permissões específicas
    const permissions = user.permissions || {};
    return permissions[permission] === true;
  }

  /**
   * Verifica se usuário tem um dos perfis
   */
  function hasRole(roles) {
    if (!user) return false;
    
    const rolesArray = Array.isArray(roles) ? roles : [roles];
    return rolesArray.includes(user.perfil);
  }

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}