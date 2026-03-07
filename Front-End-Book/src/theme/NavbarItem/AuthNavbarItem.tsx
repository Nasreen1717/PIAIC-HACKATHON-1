/**
 * Custom navbar item that renders the UserMenu component.
 * Displays Sign In/Sign Up buttons when not authenticated,
 * and user menu with profile/signout when authenticated.
 */
import React from 'react';
import { UserMenu } from '@site/src/components/Auth';
import styles from './AuthNavbarItem.module.css';

interface AuthNavbarItemProps {
  className?: string;
}

export default function AuthNavbarItem({ className }: AuthNavbarItemProps): JSX.Element {
  return (
    <div className={`${styles.authNavbarItem} ${className || ''}`}>
      <UserMenu />
    </div>
  );
}
