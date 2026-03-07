/**
 * User signup page with registration form and background questionnaire.
 * Allows new users to create accounts with optional background info.
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';
import styles from './Auth.module.css';

interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  softwareBackground?: string;
  hardwareBackground?: string;
  rosExperience?: string;
  pythonLevel?: string;
  learningGoal?: string;
  availableHardware?: string;
}

export const SignupPage: React.FC = () => {
  const { register, handleSubmit, formState: { errors }, watch } = useForm<SignupFormData>();
  const { signup, isLoading, error: authError } = useAuth();
  const history = useHistory();
  const [localError, setLocalError] = useState<string | null>(null);
  const password = watch('password');

  const onSubmit = async (data: SignupFormData) => {
    setLocalError(null);

    if (data.password !== data.confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    try {
      await signup(data.email, data.password, data.fullName, {
        software_background: data.softwareBackground,
        hardware_background: data.hardwareBackground,
        ros_experience: data.rosExperience,
        python_level: data.pythonLevel,
        learning_goal: data.learningGoal,
        available_hardware: data.availableHardware,
      });

      history.push('/');
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Signup failed');
    }
  };

  const displayError = localError || authError;

  return (
    <div className={styles.container}>
      <div className={styles.formWrapper}>
        <h1>Create Account</h1>

        {displayError && (
          <div className={styles.errorMessage}>{displayError}</div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Basic Information */}
          <fieldset>
            <legend>Account Information</legend>

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
              <label htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                {...register('fullName', {
                  required: 'Full name is required',
                  minLength: { value: 2, message: 'Name must be at least 2 characters' },
                })}
                disabled={isLoading}
              />
              {errors.fullName && <span className={styles.error}>{errors.fullName.message}</span>}
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 8, message: 'Password must be at least 8 characters' },
                })}
                disabled={isLoading}
              />
              {errors.password && <span className={styles.error}>{errors.password.message}</span>}
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                {...register('confirmPassword', {
                  required: 'Please confirm your password',
                })}
                disabled={isLoading}
              />
              {errors.confirmPassword && (
                <span className={styles.error}>{errors.confirmPassword.message}</span>
              )}
            </div>
          </fieldset>

          {/* Background Questionnaire */}
          <fieldset>
            <legend>Background (Optional)</legend>

            <div className={styles.formGroup}>
              <label htmlFor="pythonLevel">Python Experience Level</label>
              <select id="pythonLevel" {...register('pythonLevel')} disabled={isLoading}>
                <option value="">Select level...</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="rosExperience">ROS Experience</label>
              <input
                id="rosExperience"
                type="text"
                placeholder="e.g., 2 years with ROS2"
                {...register('rosExperience')}
                disabled={isLoading}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="softwareBackground">Software Background</label>
              <textarea
                id="softwareBackground"
                placeholder="Describe your software development background..."
                {...register('softwareBackground')}
                disabled={isLoading}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="hardwareBackground">Hardware Background</label>
              <textarea
                id="hardwareBackground"
                placeholder="Describe your hardware/robotics experience..."
                {...register('hardwareBackground')}
                disabled={isLoading}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="learningGoal">Learning Goal</label>
              <textarea
                id="learningGoal"
                placeholder="What do you hope to learn?"
                {...register('learningGoal')}
                disabled={isLoading}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="availableHardware">Available Hardware</label>
              <input
                id="availableHardware"
                type="text"
                placeholder="e.g., Raspberry Pi, Arduino, ROS-compatible robot"
                {...register('availableHardware')}
                disabled={isLoading}
              />
            </div>
          </fieldset>

          <button
            type="submit"
            disabled={isLoading}
            className={styles.submitButton}
          >
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <p className={styles.signinLink}>
          Already have an account? <a href="/signin">Sign in</a>
        </p>
      </div>
    </div>
  );
};
