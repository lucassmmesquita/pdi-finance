/**
 * PDI Finance - Dashboard Page
 * Dashboard moderno e responsivo
 */

import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { 
  LogOut, 
  User, 
  LayoutDashboard, 
  FolderKanban, 
  Upload, 
  FileText,
  TrendingUp,
  DollarSign,
  Users,
  Calendar,
  Menu,
  X,
  Bell,
  Settings,
  ChevronRight
} from 'lucide-react';

export function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Cards de estatísticas
  const stats = [
    { 
      label: 'Projetos Ativos', 
      value: '12', 
      change: '+2',
      icon: FolderKanban, 
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    { 
      label: 'Orçamento Total', 
      value: 'R$ 2,4M', 
      change: '+12%',
      icon: DollarSign, 
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600'
    },
    { 
      label: 'Equipe', 
      value: '45', 
      change: '+5',
      icon: Users, 
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600'
    },
    { 
      label: 'Taxa de Execução', 
      value: '87%', 
      change: '+5%',
      icon: TrendingUp, 
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600'
    },
  ];

  // Menu de navegação
  const menuItems = [
    { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard', active: true },
    { label: 'Projetos', icon: FolderKanban, href: '/projects' },
    { label: 'Importar Planilhas', icon: Upload, href: '/imports' },
    { label: 'Relatórios', icon: FileText, href: '/reports' },
  ];

  // Atividades recentes
  const recentActivities = [
    { 
      title: 'Novo projeto cadastrado', 
      description: 'Multi-PT04 foi adicionado ao sistema',
      time: 'Há 2 horas',
      icon: FolderKanban,
      color: 'bg-blue-100 text-blue-600'
    },
    { 
      title: 'Orçamento atualizado', 
      description: 'Planilha financeira importada com sucesso',
      time: 'Há 5 horas',
      icon: TrendingUp,
      color: 'bg-green-100 text-green-600'
    },
    { 
      title: 'Novo membro da equipe', 
      description: 'João Silva foi adicionado ao projeto PT03',
      time: 'Ontem',
      icon: Users,
      color: 'bg-purple-100 text-purple-600'
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
          {/* Logo */}
          <div className="flex h-20 shrink-0 items-center gap-3 border-b border-gray-100">
            <div className="h-10 w-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <LayoutDashboard className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">PDI Finance</h1>
              <p className="text-xs text-gray-500">Sistema de Gestão</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-2">
              {menuItems.map((item) => (
                <li key={item.label}>
                  <a
                    href={item.href}
                    className={`group flex gap-x-3 rounded-xl p-3 text-sm font-semibold leading-6 transition-all ${
                      item.active
                        ? 'bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-600 border-l-4 border-indigo-600'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-indigo-600 border-l-4 border-transparent'
                    }`}
                  >
                    <item.icon className="h-6 w-6 shrink-0" />
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          {/* User Profile */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center gap-x-4 p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-semibold">
                {user?.nome?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{user?.nome}</p>
                <p className="text-xs text-gray-500 truncate">{user?.perfil}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden">
          <div className="fixed inset-0 z-40 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
          <aside className="fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 animate-slide-right">
            {/* Mesmo conteúdo do sidebar desktop */}
            <div className="flex h-20 items-center justify-between px-6 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <LayoutDashboard className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold gradient-text">PDI Finance</h1>
                </div>
              </div>
              <button onClick={() => setSidebarOpen(false)}>
                <X className="h-6 w-6 text-gray-500" />
              </button>
            </div>
            {/* Navigation items... */}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="lg:pl-72">
        {/* Header */}
        <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex-1 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Dashboard</h2>
              
              <div className="flex items-center gap-4">
                <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                  <Bell className="h-6 w-6" />
                  <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
                </button>
                
                <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                  <Settings className="h-6 w-6" />
                </button>
                
                <button
                  onClick={handleLogout}
                  className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors font-medium"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Sair</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-4 sm:p-6 lg:p-8 animate-fade-in">
          {/* Welcome Message */}
          <div className="mb-8">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900">
              Bem-vindo de volta, {user?.nome?.split(' ')[0]}! 👋
            </h3>
            <p className="text-gray-600 mt-2">
              Aqui está um resumo dos seus projetos e atividades
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl shadow-soft p-6 card-hover border border-gray-100"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.bgColor} p-3 rounded-xl`}>
                    <stat.icon className={`h-6 w-6 ${stat.textColor}`} />
                  </div>
                  <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">
                    {stat.change}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <p className="text-2xl sm:text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Activities */}
            <div className="lg:col-span-2 bg-white rounded-2xl shadow-soft p-6 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900">Atividades Recentes</h3>
                <button className="text-sm text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1">
                  Ver todas
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
              
              <div className="space-y-4">
                {recentActivities.map((activity, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <div className={`${activity.color} p-2 rounded-lg shrink-0`}>
                      <activity.icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 mb-1">
                        {activity.title}
                      </p>
                      <p className="text-xs text-gray-600 mb-2">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl shadow-hard p-6 text-white">
              <h3 className="text-lg font-bold mb-6">Ações Rápidas</h3>
              
              <div className="space-y-3">
                {menuItems.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => navigate(item.href)}
                    className="w-full flex items-center gap-3 p-4 bg-white/10 backdrop-blur-lg hover:bg-white/20 rounded-xl transition-all border border-white/20 text-left group"
                  >
                    <item.icon className="h-5 w-5 shrink-0" />
                    <span className="text-sm font-medium">{item.label}</span>
                    <ChevronRight className="h-4 w-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}