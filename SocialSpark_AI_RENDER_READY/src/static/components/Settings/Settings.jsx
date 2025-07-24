import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { 
  Settings as SettingsIcon, Bell, Palette, Shield, Key, 
  Download, Upload, Trash2, Save, Moon, Sun, Monitor,
  Globe, Lock, Eye, EyeOff
} from 'lucide-react';
import API_BASE_URL from '../../config/api';

const Settings = () => {
  const [settings, setSettings] = useState({
    theme: 'system',
    language: 'en',
    notifications: {
      email: true,
      push: false,
      marketing: false
    },
    privacy: {
      profilePublic: false,
      showStats: true,
      allowAnalytics: true
    },
    defaults: {
      platform: 'instagram',
      tone: 'casual',
      contentType: 'post'
    }
  });
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/user/settings`, {
        headers: { 'x-access-token': token }
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data.settings);
      }
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/user/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': token
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        setMessage('Settings saved successfully!');
      } else {
        const data = await response.json();
        setMessage(data.message || 'Failed to save settings');
      }
    } catch (err) {
      setMessage('Network error. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const changePassword = async () => {
    if (passwords.new !== passwords.confirm) {
      setMessage('New passwords do not match');
      return;
    }

    if (passwords.new.length < 8) {
      setMessage('Password must be at least 8 characters long');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/user/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': token
        },
        body: JSON.stringify({
          currentPassword: passwords.current,
          newPassword: passwords.new
        })
      });

      if (response.ok) {
        setMessage('Password changed successfully!');
        setPasswords({ current: '', new: '', confirm: '' });
      } else {
        const data = await response.json();
        setMessage(data.message || 'Failed to change password');
      }
    } catch (err) {
      setMessage('Network error. Please try again.');
    }
  };

  const exportData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/user/export`, {
        headers: { 'x-access-token': token }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'socialspark-data.json';
        a.click();
        window.URL.revokeObjectURL(url);
        setMessage('Data exported successfully!');
      }
    } catch (err) {
      setMessage('Failed to export data');
    }
  };

  const deleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/user/delete`, {
        method: 'DELETE',
        headers: { 'x-access-token': token }
      });

      if (response.ok) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } catch (err) {
      setMessage('Failed to delete account');
    }
  };

  const updateSetting = (path, value) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <SettingsIcon className="h-6 w-6 text-primary" />
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Appearance
              </CardTitle>
              <CardDescription>Customize how SocialSpark AI looks and feels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Theme</Label>
                <Select value={settings.theme} onValueChange={(value) => updateSetting('theme', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">
                      <div className="flex items-center gap-2">
                        <Sun className="h-4 w-4" />
                        Light
                      </div>
                    </SelectItem>
                    <SelectItem value="dark">
                      <div className="flex items-center gap-2">
                        <Moon className="h-4 w-4" />
                        Dark
                      </div>
                    </SelectItem>
                    <SelectItem value="system">
                      <div className="flex items-center gap-2">
                        <Monitor className="h-4 w-4" />
                        System
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Language</Label>
                <Select value={settings.language} onValueChange={(value) => updateSetting('language', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Content Defaults</CardTitle>
              <CardDescription>Set your preferred defaults for content generation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Default Platform</Label>
                  <Select value={settings.defaults.platform} onValueChange={(value) => updateSetting('defaults.platform', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="twitter">Twitter</SelectItem>
                      <SelectItem value="facebook">Facebook</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                      <SelectItem value="tiktok">TikTok</SelectItem>
                      <SelectItem value="youtube">YouTube</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Default Tone</Label>
                  <Select value={settings.defaults.tone} onValueChange={(value) => updateSetting('defaults.tone', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="humorous">Humorous</SelectItem>
                      <SelectItem value="inspirational">Inspirational</SelectItem>
                      <SelectItem value="educational">Educational</SelectItem>
                      <SelectItem value="promotional">Promotional</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Default Content Type</Label>
                  <Select value={settings.defaults.contentType} onValueChange={(value) => updateSetting('defaults.contentType', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="post">Post</SelectItem>
                      <SelectItem value="caption">Caption</SelectItem>
                      <SelectItem value="story">Story</SelectItem>
                      <SelectItem value="ad">Advertisement</SelectItem>
                      <SelectItem value="blog">Blog</SelectItem>
                      <SelectItem value="announcement">Announcement</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>Choose how you want to be notified</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive updates via email</p>
                </div>
                <Switch
                  checked={settings.notifications.email}
                  onCheckedChange={(checked) => updateSetting('notifications.email', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label>Push Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive browser notifications</p>
                </div>
                <Switch
                  checked={settings.notifications.push}
                  onCheckedChange={(checked) => updateSetting('notifications.push', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label>Marketing Communications</Label>
                  <p className="text-sm text-muted-foreground">Receive product updates and tips</p>
                </div>
                <Switch
                  checked={settings.notifications.marketing}
                  onCheckedChange={(checked) => updateSetting('notifications.marketing', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="privacy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy Settings
              </CardTitle>
              <CardDescription>Control your privacy and data sharing preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Public Profile</Label>
                  <p className="text-sm text-muted-foreground">Make your profile visible to other users</p>
                </div>
                <Switch
                  checked={settings.privacy.profilePublic}
                  onCheckedChange={(checked) => updateSetting('privacy.profilePublic', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label>Show Statistics</Label>
                  <p className="text-sm text-muted-foreground">Display your content statistics publicly</p>
                </div>
                <Switch
                  checked={settings.privacy.showStats}
                  onCheckedChange={(checked) => updateSetting('privacy.showStats', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label>Analytics</Label>
                  <p className="text-sm text-muted-foreground">Help improve our service with usage analytics</p>
                </div>
                <Switch
                  checked={settings.privacy.allowAnalytics}
                  onCheckedChange={(checked) => updateSetting('privacy.allowAnalytics', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Change Password
              </CardTitle>
              <CardDescription>Update your account password</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.current ? "text" : "password"}
                    value={passwords.current}
                    onChange={(e) => setPasswords(prev => ({ ...prev, current: e.target.value }))}
                    placeholder="Enter current password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                  >
                    {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>New Password</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.new ? "text" : "password"}
                    value={passwords.new}
                    onChange={(e) => setPasswords(prev => ({ ...prev, new: e.target.value }))}
                    placeholder="Enter new password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                  >
                    {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Confirm New Password</Label>
                <div className="relative">
                  <Input
                    type={showPasswords.confirm ? "text" : "password"}
                    value={passwords.confirm}
                    onChange={(e) => setPasswords(prev => ({ ...prev, confirm: e.target.value }))}
                    placeholder="Confirm new password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                  >
                    {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <Button onClick={changePassword} className="gap-2">
                <Key className="h-4 w-4" />
                Change Password
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
              <CardDescription>Export or delete your data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-medium">Export Data</h3>
                    <p className="text-sm text-muted-foreground">Download all your content and settings</p>
                  </div>
                  <Button onClick={exportData} variant="outline" className="gap-2">
                    <Download className="h-4 w-4" />
                    Export
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
                  <div>
                    <h3 className="font-medium text-red-900">Delete Account</h3>
                    <p className="text-sm text-red-700">Permanently delete your account and all data</p>
                  </div>
                  <Button onClick={deleteAccount} variant="destructive" className="gap-2">
                    <Trash2 className="h-4 w-4" />
                    Delete Account
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <div className="flex items-center justify-between">
        {message && (
          <div className={`text-sm ${message.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
            {message}
          </div>
        )}
        <Button onClick={saveSettings} disabled={isSaving} className="gap-2 ml-auto">
          {isSaving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Saving...
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default Settings;

