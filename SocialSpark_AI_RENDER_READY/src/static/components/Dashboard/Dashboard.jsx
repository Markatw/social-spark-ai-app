import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import { 
  TrendingUp, Users, FileText, Zap, Calendar, Clock, 
  Target, Award, Sparkles, ArrowUpRight, Plus
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import API_BASE_URL from '../../config/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalContent: 0,
    thisWeek: 0,
    platforms: 0,
    avgPerDay: 0
  });
  const [recentContent, setRecentContent] = useState([]);
  const [platformData, setPlatformData] = useState([]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch dashboard analytics
      const analyticsResponse = await fetch(`${API_BASE_URL}/analytics/dashboard`, {
        headers: { 'x-access-token': token }
      });
      
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setStats(analyticsData.stats);
        setPlatformData(analyticsData.platformData);
        setWeeklyData(analyticsData.weeklyData);
      }

      // Fetch recent content
      const contentResponse = await fetch(`${API_BASE_URL}/content/recent?limit=5`, {
        headers: { 'x-access-token': token }
      });
      
      if (contentResponse.ok) {
        const contentData = await contentResponse.json();
        setRecentContent(contentData.content);
      }
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  const quickActions = [
    {
      title: 'Generate Content',
      description: 'Create new AI-powered content',
      icon: Sparkles,
      action: () => navigate('/generate'),
      color: 'bg-blue-500'
    },
    {
      title: 'View Saved',
      description: 'Browse your content library',
      icon: FileText,
      action: () => navigate('/saved'),
      color: 'bg-green-500'
    },
    {
      title: 'Profile Settings',
      description: 'Update your preferences',
      icon: Users,
      action: () => navigate('/profile'),
      color: 'bg-purple-500'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's your content overview.</p>
        </div>
        <Button onClick={() => navigate('/generate')} className="gap-2">
          <Plus className="h-4 w-4" />
          Generate Content
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Content</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalContent}</div>
            <p className="text-xs text-muted-foreground">
              +{stats.thisWeek} this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Platforms</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.platforms}</div>
            <p className="text-xs text-muted-foreground">
              Active platforms
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Average</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avgPerDay}</div>
            <p className="text-xs text-muted-foreground">
              Content per day
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Week</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.thisWeek}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+12%</span> from last week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with common tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, index) => (
              <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow" onClick={action.action}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <action.icon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Activity</CardTitle>
            <CardDescription>Content generation over the past week</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="content" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Platform Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Platform Distribution</CardTitle>
            <CardDescription>Content breakdown by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={platformData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {platformData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Content */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Content</CardTitle>
          <CardDescription>Your latest generated content</CardDescription>
        </CardHeader>
        <CardContent>
          {recentContent.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">No content generated yet. Start creating!</p>
              <Button onClick={() => navigate('/generate')} className="mt-4">
                Generate Your First Content
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {recentContent.map((content, index) => (
                <div key={index} className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="secondary">{content.platform}</Badge>
                      <Badge variant="outline">{content.content_type}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {new Date(content.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="font-medium mb-1">{content.topic}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {content.content}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => navigate('/saved')}>
                    <ArrowUpRight className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

