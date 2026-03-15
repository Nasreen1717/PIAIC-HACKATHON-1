/**
 * User menu component showing current user info and logout button.
 * Displays in header when user is authenticated.
 */
import React, { useState, useEffect } from 'react';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';
import styles from './UserMenu.module.css';

export const UserMenu: React.FC = () => {
  const { user, token, signout } = useAuth();
  const history = useHistory();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Ensure component is mounted before rendering to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
    console.log('UserMenu mounted - user:', user, 'token:', !!token);
  }, [user, token]);

  // Listen for auth changes from other components
  useEffect(() => {
    const handleAuthChanged = (event: any) => {
      console.log('UserMenu: Auth changed event received', event.detail);
      // The context will handle updating state, we just force a re-render
    };

    window.addEventListener('auth-changed', handleAuthChanged);
    return () => window.removeEventListener('auth-changed', handleAuthChanged);
  }, []);

  if (!mounted) {
    return <div className={styles.container} />;
  }

  if (!user || !token) {
    console.log('UserMenu: Not authenticated, showing signin/signup buttons');
    return (
      <div className={styles.container}>
        <a href="/signin" className={styles.signinLink}>
          Sign In
        </a>
        <a href="/signup" className={styles.signupLink}>
          Sign Up
        </a>
      </div>
    );
  }

  console.log('UserMenu: Authenticated as', user.email);

  const handleSignout = async () => {
    console.log('UserMenu: Signing out...');
    await signout();
    history.push('/');
  };

  return (
    <div className={styles.container}>
      <button
        className={styles.userButton}
        onClick={() => {
          console.log('UserMenu: Toggling dropdown');
          setIsOpen(!isOpen);
        }}
        aria-expanded={isOpen}
        aria-haspopup="menu"
        style={{ textDecoration: 'none' }}
      >
        <span className={styles.userName} style={{ textDecoration: 'none' }}>
          {user.full_name || user.email}
        </span>
        <span className={styles.arrow} style={{ textDecoration: 'none' }}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.userInfo}>
            <p className={styles.email}>{user.email}</p>
          </div>

          <a href="/profile" className={styles.profileLink}>
            View Profile
          </a>

          <button
            onClick={handleSignout}
            className={styles.signoutButton}
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};
