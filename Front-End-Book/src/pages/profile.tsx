/**
 * Profile page route for Better-Auth.
 * This page is served at /profile and wraps the ProfilePage component.
 * Only accessible to authenticated users.
 */
import React from 'react';
import Layout from '@theme/Layout';
import { ProfilePage } from '../components/Auth/ProfilePage';

export default function ProfilePageRoute() {
  return (
    <Layout title="Your Profile" description="Manage your account and profile information">
      <ProfilePage />
    </Layout>
  );
}
