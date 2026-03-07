/**
 * User profile page with background questionnaire editing.
 * Allows authenticated users to view and update their profile information.
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../hooks/useAuth';
import { ProtectedRoute } from './ProtectedRoute';
import styles from './ProfilePage.module.css';

interface ProfileFormData {
  fullName?: string;
  softwareBackground?: string;
  hardwareBackground?: string;
  rosExperience?: string;
  pythonLevel?: string;
  learningGoal?: string;
  availableHardware?: string;
}

export const ProfilePage: React.FC = () => {
  return (
    <ProtectedRoute>
      <ProfilePageContent />
    </ProtectedRoute>
  );
};

const ProfilePageContent: React.FC = () => {
  const { user, updateProfile, isLoading, error: authError } = useAuth();
  const { register, handleSubmit, formState: { errors }, reset } = useForm<ProfileFormData>({
    defaultValues: {
      fullName: user?.full_name || '',
      softwareBackground: user?.background?.software_background || '',
      hardwareBackground: user?.background?.hardware_background || '',
      rosExperience: user?.background?.ros_experience || '',
      pythonLevel: user?.background?.python_level || '',
      learningGoal: user?.background?.learning_goal || '',
      availableHardware: user?.background?.available_hardware || '',
    },
  });
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const onSubmit = async (data: ProfileFormData) => {
    setLocalError(null);
    setSuccessMessage(null);

    try {
      await updateProfile({
        full_name: data.fullName,
        background: {
          software_background: data.softwareBackground,
          hardware_background: data.hardwareBackground,
          ros_experience: data.rosExperience,
          python_level: data.pythonLevel,
          learning_goal: data.learningGoal,
          available_hardware: data.availableHardware,
        },
      });

      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Update failed');
    }
  };

  const displayError = localError || authError;

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <h1>Your Profile</h1>

        <div className={styles.accountInfo}>
          <div className={styles.infoItem}>
            <label>Email</label>
            <p>{user.email}</p>
          </div>

          <div className={styles.infoItem}>
            <label>Member Since</label>
            <p>{new Date(user.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        {displayError && (
          <div className={styles.errorMessage}>{displayError}</div>
        )}

        {successMessage && (
          <div className={styles.successMessage}>{successMessage}</div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <fieldset>
            <legend>Personal Information</legend>

            <div className={styles.formGroup}>
              <label htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                {...register('fullName')}
                disabled={isLoading}
              />
              {errors.fullName && <span className={styles.error}>{errors.fullName.message}</span>}
            </div>
          </fieldset>

          <fieldset>
            <legend>Background & Experience</legend>

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

          <div className={styles.buttonGroup}>
            <button
              type="submit"
              disabled={isLoading}
              className={styles.submitButton}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>

            <button
              type="button"
              onClick={() => reset()}
              disabled={isLoading}
              className={styles.cancelButton}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
