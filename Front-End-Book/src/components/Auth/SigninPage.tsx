/**
 * User signin page with email/password login form.
 * Supports remember_me for extended session duration.
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';
import styles from './Auth.module.css';

interface SigninFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export const SigninPage: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<SigninFormData>();
  const { signin, isLoading, error: authError } = useAuth();
  const history = useHistory();
  const [localError, setLocalError] = useState<string | null>(null);

  const onSubmit = async (data: SigninFormData) => {
    setLocalError(null);

    try {
      await signin(data.email, data.password, data.rememberMe);
      history.push('/');
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Signin failed');
    }
  };

  const displayError = localError || authError;

  return (
    <div className={styles.container}>
      <div className={styles.formWrapper}>
        <h1>Sign In</h1>

        {displayError && (
          <div className={styles.errorMessage}>{displayError}</div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
              disabled={isLoading}
            />
            {errors.email && <span className={styles.error}>{errors.email.message}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              {...register('password', {
                required: 'Password is required',
              })}
              disabled={isLoading}
            />
            {errors.password && <span className={styles.error}>{errors.password.message}</span>}
          </div>

          <div className={styles.checkboxGroup}>
            <input
              id="rememberMe"
              type="checkbox"
              {...register('rememberMe')}
              disabled={isLoading}
            />
            <label htmlFor="rememberMe">Remember me for 30 days</label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={styles.submitButton}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className={styles.signupLink}>
          Don't have an account? <a href="/signup">Sign up</a>
        </p>
      </div>
    </div>
  );
};
