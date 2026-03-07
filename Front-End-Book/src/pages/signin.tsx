/**
 * Signin page route for Better-Auth.
 * This page is served at /signin and wraps the SigninPage component.
 */
import React from 'react';
import Layout from '@theme/Layout';
import { SigninPage } from '../components/Auth/SigninPage';

export default function SigninPageRoute() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <SigninPage />
    </Layout>
  );
}
