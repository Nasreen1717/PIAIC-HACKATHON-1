/**
 * Custom NavbarItem that supports 'auth' type
 * Renders AuthNavbarItem for auth type, delegates others to default
 */

import React from 'react';
import NavbarItemOriginal from '@theme-original/NavbarItem';
import AuthNavbarItem from './AuthNavbarItem';

export default function NavbarItem(props) {
  if (props.type === 'auth') {
    return <AuthNavbarItem {...props} />;
  }

  return <NavbarItemOriginal {...props} />;
}
