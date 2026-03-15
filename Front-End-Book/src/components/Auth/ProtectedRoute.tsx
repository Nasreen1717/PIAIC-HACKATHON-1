/**
 * Protected route component that restricts access to authenticated users.
 * Redirects to signin page if user is not authenticated.
 */
import React from 'react';
import { Redirect } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <Redirect to="/signin" />;
  }

  return <>{children}</>;
};
