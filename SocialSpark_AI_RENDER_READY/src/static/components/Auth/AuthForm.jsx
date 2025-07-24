import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiConfig } from '../../config/api';

const AuthForm = ({ type }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [message, setMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    const url = type === 'login' ? `${apiConfig.baseURL}/auth/login` : `${apiConfig.baseURL}/auth/register`;
    const body = type === 'login' ? { email, password } : { username, email, password };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        if (type === 'login' && data.token) {
          login(data.token);
          navigate('/dashboard'); // Redirect to dashboard on successful login
        }
      } else {
        setMessage(data.message || 'An error occurred');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Network error or server is unreachable');
    }
  };

  return (
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-2xl">{type === 'login' ? 'Login' : 'Register'}</CardTitle>
        <CardDescription>
          {type === 'login' ? 'Enter your email below to login to your account' : 'Enter your information to create an account'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="grid gap-4">
          {type === 'register' && (
            <div className="grid gap-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Your Username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          )}
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full">
            {type === 'login' ? 'Login' : 'Create an account'}
          </Button>
        </form>
        {message && <p className="mt-4 text-center text-sm text-red-500">{message}</p>}
        <div className="mt-4 text-center text-sm">
          {type === 'login' ? (
            <>Don't have an account? <a href="#" className="underline" onClick={() => navigate('/register')}>Sign up</a></>
          ) : (
            <>Already have an account? <a href="#" className="underline" onClick={() => navigate('/login')}>Login</a></>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AuthForm;


