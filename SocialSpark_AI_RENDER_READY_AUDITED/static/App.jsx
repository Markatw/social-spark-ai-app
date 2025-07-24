import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet.jsx'
import { Menu, Home, Settings, User, FileText, LogOut, Bookmark, Sparkles } from 'lucide-react'
import AuthForm from './components/Auth/AuthForm.jsx'
import ProtectedRoute from './components/Auth/ProtectedRoute.jsx'
import Dashboard from './components/Dashboard/Dashboard.jsx'
import ContentGenerator from './components/Content/ContentGenerator.jsx'
import SavedContent from './components/Content/SavedContent.jsx'
import UserProfile from './components/Profile/UserProfile.jsx'
import SettingsPage from './components/Settings/Settings.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import './App.css'

function AppContent() {
  const { logout, isAuthenticated } = useAuth()
  const location = useLocation()

  const handleLogout = () => {
    logout()
  }

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard':
        return 'Dashboard'
      case '/generate':
        return 'Content Generator'
      case '/saved':
        return 'Saved Content'
      case '/profile':
        return 'Profile'
      case '/settings':
        return 'Settings'
      default:
        return 'Dashboard'
    }
  }

  const isActive = (path) => location.pathname === path
  
  // Check if current page is authentication page
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  // If not authenticated and not on auth pages, redirect to login
  if (!isAuthenticated && !isAuthPage) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <img src="/idsideSEO-logo.png" alt="idsideSEO" className="h-12" />
            </div>
            <p className="text-gray-600">AI-Powered Content Generator for SEO & Social Media</p>
          </div>
          <AuthForm type="login" />
        </div>
      </div>
    )
  }

  // If on auth pages, show clean auth layout without sidebar
  if (isAuthPage) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <img src="/idsideSEO-logo.png" alt="idsideSEO" className="h-12" />
            </div>
            <p className="text-gray-600">AI-Powered Content Generator for SEO & Social Media</p>
          </div>
          <Routes>
            <Route path="/login" element={<AuthForm type="login" />} />
            <Route path="/register" element={<AuthForm type="register" />} />
          </Routes>
        </div>
      </div>
    )
  }

  // Main authenticated app layout with sidebar
  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      {/* Desktop Sidebar - Only show when authenticated and not on auth pages */}
      <aside className="fixed inset-y-0 left-0 z-10 hidden w-64 flex-col border-r bg-background sm:flex">
        {/* Logo Section - Properly positioned at top */}
        <div className="flex h-16 items-center justify-center border-b px-4">
          <Link to="/dashboard" className="flex items-center gap-2">
            <img src="/idsideSEO-logo.png" alt="idsideSEO" className="h-8" />
          </Link>
        </div>
        
        {/* Navigation Section - Separate from logo */}
        <nav className="flex flex-1 flex-col gap-2 px-4 py-4">
          <Link 
            to="/dashboard" 
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
              isActive('/dashboard') 
                ? 'bg-[#003366] text-white' 
                : 'text-muted-foreground hover:text-[#003366] hover:bg-blue-50'
            }`}
          >
            <Home className="h-4 w-4" />
            Dashboard
          </Link>
          <Link 
            to="/generate" 
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
              isActive('/generate') 
                ? 'bg-[#00aaff] text-white' 
                : 'text-muted-foreground hover:text-[#00aaff] hover:bg-blue-50'
            }`}
          >
            <FileText className="h-4 w-4" />
            Generate Content
          </Link>
          <Link 
            to="/saved" 
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
              isActive('/saved') 
                ? 'bg-[#003366] text-white' 
                : 'text-muted-foreground hover:text-[#003366] hover:bg-blue-50'
            }`}
          >
            <Bookmark className="h-4 w-4" />
            Saved Content
          </Link>
          <Link 
            to="/profile" 
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
              isActive('/profile') 
                ? 'bg-[#00aaff] text-white' 
                : 'text-muted-foreground hover:text-[#00aaff] hover:bg-blue-50'
            }`}
          >
            <User className="h-4 w-4" />
            Profile
          </Link>
          <Link 
            to="/settings" 
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
              isActive('/settings') 
                ? 'bg-[#003366] text-white' 
                : 'text-muted-foreground hover:text-[#003366] hover:bg-blue-50'
            }`}
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          
          {/* Logout Button at bottom */}
          <div className="mt-auto">
            <Button 
              onClick={handleLogout} 
              variant="ghost"
              className="flex w-full items-center gap-3 justify-start px-3 py-2 text-muted-foreground hover:text-red-500 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-64">
        {/* Mobile Header */}
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:bg-transparent sm:px-6">
          <Sheet>
            <SheetTrigger asChild>
              <Button size="icon" variant="outline" className="sm:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle Menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="sm:max-w-xs">
              <nav className="grid gap-6 text-lg font-medium">
                <Link to="/dashboard" className="flex items-center gap-2">
                  <img src="/idsideSEO-logo.png" alt="idsideSEO" className="h-8" />
                </Link>
                <Link to="/dashboard" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground">
                  <Home className="h-5 w-5" />
                  Dashboard
                </Link>
                <Link to="/generate" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground">
                  <FileText className="h-5 w-5" />
                  Generate Content
                </Link>
                <Link to="/saved" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground">
                  <Bookmark className="h-5 w-5" />
                  Saved Content
                </Link>
                <Link to="/profile" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground">
                  <User className="h-5 w-5" />
                  Profile
                </Link>
                <Link to="/settings" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground">
                  <Settings className="h-5 w-5" />
                  Settings
                </Link>
                <Button onClick={handleLogout} variant="ghost" className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground w-full justify-start">
                  <LogOut className="h-5 w-5" />
                  Logout
                </Button>
              </nav>
            </SheetContent>
          </Sheet>
          <h1 className="text-lg font-semibold md:text-2xl">{getPageTitle()}</h1>
        </header>

        {/* Page Content */}
        <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
          <Routes>
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/generate" element={<ProtectedRoute><ContentGenerator /></ProtectedRoute>} />
            <Route path="/saved" element={<ProtectedRoute><SavedContent /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App

