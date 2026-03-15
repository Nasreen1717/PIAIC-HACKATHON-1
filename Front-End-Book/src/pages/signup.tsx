/**
 * Signup page route for Better-Auth.
 * This page is served at /signup and wraps the SignupPage component.
 */
import React from 'react';
import Layout from '@theme/Layout';
import { SignupPage } from '../components/Auth/SignupPage';

export default function SignupPageRoute() {
  return (
    <Layout title="Sign Up" description="Create a new account">
      <SignupPage />
    </Layout>
  );
}
