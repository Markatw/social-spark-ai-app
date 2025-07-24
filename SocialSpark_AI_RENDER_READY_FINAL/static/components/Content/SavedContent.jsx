import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Trash2, Edit, Search, Filter, BookmarkCheck } from 'lucide-react';
import API_BASE_URL from '../../config/api';

const SavedContent = () => {
  const [savedContent, setSavedContent] = useState([]);
  const [filteredContent, setFilteredContent] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [isLoading, setIsLoading] = useState(true);

  const platforms = ['all', 'instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube'];

  useEffect(() => {
    fetchSavedContent();
  }, []);

  useEffect(() => {
    filterContent();
  }, [savedContent, searchTerm, selectedPlatform]);

  const fetchSavedContent = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/content/saved`, {
        headers: {
          'x-access-token': token
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSavedContent(data.content || []);
      }
    } catch (err) {
      console.error('Failed to fetch saved content:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filterContent = () => {
    let filtered = savedContent;

    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.topic.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedPlatform !== 'all') {
      filtered = filtered.filter(item => item.platform === selectedPlatform);
    }

    setFilteredContent(filtered);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const deleteContent = async (id) => {
    if (!confirm('Are you sure you want to delete this content?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/content/${id}`, {
        method: 'DELETE',
        headers: {
          'x-access-token': token
        }
      });

      if (response.ok) {
        setSavedContent(prev => prev.filter(item => item.id !== id));
      }
    } catch (err) {
      alert('Failed to delete content');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPlatformColor = (platform) => {
    const colors = {
      instagram: 'bg-pink-100 text-pink-800',
      twitter: 'bg-blue-100 text-blue-800',
      facebook: 'bg-blue-100 text-blue-800',
      linkedin: 'bg-blue-100 text-blue-800',
      tiktok: 'bg-purple-100 text-purple-800',
      youtube: 'bg-red-100 text-red-800'
    };
    return colors[platform] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading saved content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <BookmarkCheck className="h-6 w-6 text-primary" />
        <h1 className="text-3xl font-bold">Saved Content</h1>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search content or topics..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Tabs value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="instagram">Instagram</TabsTrigger>
                  <TabsTrigger value="twitter">Twitter</TabsTrigger>
                  <TabsTrigger value="facebook">Facebook</TabsTrigger>
                  <TabsTrigger value="linkedin">LinkedIn</TabsTrigger>
                  <TabsTrigger value="tiktok">TikTok</TabsTrigger>
                  <TabsTrigger value="youtube">YouTube</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Grid */}
      {filteredContent.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <BookmarkCheck className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No saved content found</h3>
            <p className="text-muted-foreground">
              {savedContent.length === 0 
                ? "You haven't saved any content yet. Generate some content and save your favorites!"
                : "No content matches your current search and filter criteria."
              }
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContent.map((item) => (
            <Card key={item.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium line-clamp-2">
                      {item.topic}
                    </CardTitle>
                    <div className="flex gap-2">
                      <Badge className={getPlatformColor(item.platform)}>
                        {item.platform}
                      </Badge>
                      <Badge variant="outline">
                        {item.content_type}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(item.content)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deleteContent(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-sm text-muted-foreground bg-muted p-3 rounded max-h-32 overflow-y-auto">
                    {item.content}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Saved {formatDate(item.created_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Content Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{savedContent.length}</div>
              <div className="text-sm text-muted-foreground">Total Saved</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {new Set(savedContent.map(item => item.platform)).size}
              </div>
              <div className="text-sm text-muted-foreground">Platforms</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {new Set(savedContent.map(item => item.content_type)).size}
              </div>
              <div className="text-sm text-muted-foreground">Content Types</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {savedContent.filter(item => 
                  new Date(item.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
                ).length}
              </div>
              <div className="text-sm text-muted-foreground">This Week</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SavedContent;

