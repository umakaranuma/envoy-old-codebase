import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

// User interface based on the authUser API response structure
export interface IUser {
  id: number;
  name: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  avatar?: string;
  role?: string;
  permissions?: string[];
  entity_id?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
  [key: string]: any; // Allow for additional properties
}

// User service class for managing current user data
export class UserService {
  /**
   * Get current logged-in user details from localStorage
   * @returns IUser | null - User object or null if not found
   */
  static getCurrentUser(): IUser | null {
    try {
      const userData = getLocalStorage(local_storage.auth_user_info);
      return userData || null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  /**
   * Get current user ID
   * @returns number | null - User ID or null if not found
   */
  static getCurrentUserId(): number | null {
    const user = this.getCurrentUser();
    return user?.id || null;
  }

  /**
   * Get current user name
   * @returns string | null - User name or null if not found
   */
  static getCurrentUserName(): string | null {
    const user = this.getCurrentUser();
    return user?.name || user?.first_name || user?.username || null;
  }

  /**
   * Get current user email
   * @returns string | null - User email or null if not found
   */
  static getCurrentUserEmail(): string | null {
    const user = this.getCurrentUser();
    return user?.email || null;
  }

  /**
   * Get current user role
   * @returns string | null - User role or null if not found
   */
  static getCurrentUserRole(): string | null {
    const user = this.getCurrentUser();
    return user?.role || null;
  }

  /**
   * Get current user permissions
   * @returns string[] | null - User permissions array or null if not found
   */
  static getCurrentUserPermissions(): string[] | null {
    const user = this.getCurrentUser();
    return user?.permissions || null;
  }

  /**
   * Get current user entity ID
   * @returns string | null - User entity ID or null if not found
   */
  static getCurrentUserEntityId(): string | null {
    const user = this.getCurrentUser();
    return user?.entity_id || null;
  }

  /**
   * Get current user avatar
   * @returns string | null - User avatar URL or null if not found
   */
  static getCurrentUserAvatar(): string | null {
    const user = this.getCurrentUser();
    return user?.avatar || null;
  }

  /**
   * Check if user has a specific permission
   * @param permission - Permission to check
   * @returns boolean - True if user has permission, false otherwise
   */
  static hasPermission(permission: string): boolean {
    const permissions = this.getCurrentUserPermissions();
    return permissions ? permissions.includes(permission) : false;
  }

  /**
   * Check if user has any of the specified permissions
   * @param permissions - Array of permissions to check
   * @returns boolean - True if user has any of the permissions, false otherwise
   */
  static hasAnyPermission(permissions: string[]): boolean {
    const userPermissions = this.getCurrentUserPermissions();
    if (!userPermissions) return false;
    return permissions.some((permission) => userPermissions.includes(permission));
  }

  /**
   * Check if user has all of the specified permissions
   * @param permissions - Array of permissions to check
   * @returns boolean - True if user has all permissions, false otherwise
   */
  static hasAllPermissions(permissions: string[]): boolean {
    const userPermissions = this.getCurrentUserPermissions();
    if (!userPermissions) return false;
    return permissions.every((permission) => userPermissions.includes(permission));
  }

  /**
   * Check if user is logged in
   * @returns boolean - True if user is logged in, false otherwise
   */
  static isLoggedIn(): boolean {
    const user = this.getCurrentUser();
    return user !== null && user !== undefined;
  }

  /**
   * Get user display name (fallback to different name fields)
   * @returns string | null - Display name or null if not found
   */
  static getDisplayName(): string | null {
    const user = this.getCurrentUser();
    if (!user) return null;

    // Try different name fields in order of preference
    if (user.name) return user.name;
    if (user.first_name && user.last_name) return `${user.first_name} ${user.last_name}`;
    if (user.first_name) return user.first_name;
    if (user.username) return user.username;
    if (user.email) return user.email;

    return null;
  }

  /**
   * Get user initials for avatar display
   * @returns string | null - User initials or null if not found
   */
  static getUserInitials(): string | null {
    const user = this.getCurrentUser();
    if (!user) return null;

    let initials = '';

    if (user.first_name && user.last_name) {
      initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
    } else if (user.name) {
      const nameParts = user.name.split(' ');
      if (nameParts.length >= 2) {
        initials = `${nameParts[0].charAt(0)}${nameParts[nameParts.length - 1].charAt(0)}`.toUpperCase();
      } else {
        initials = user.name.charAt(0).toUpperCase();
      }
    } else if (user.username) {
      initials = user.username.charAt(0).toUpperCase();
    } else if (user.email) {
      initials = user.email.charAt(0).toUpperCase();
    }

    return initials || null;
  }

  /**
   * Get a specific user property
   * @param key - Property key to retrieve
   * @returns any - Property value or null if not found
   */
  static getUserProperty(key: string): any {
    const user = this.getCurrentUser();
    return user?.[key] || null;
  }

  /**
   * Check if user is active
   * @returns boolean - True if user is active, false otherwise
   */
  static isUserActive(): boolean {
    const user = this.getCurrentUser();
    return user?.is_active !== false; // Default to true if not specified
  }
}

// Export individual functions for convenience
export const getCurrentUser = UserService.getCurrentUser;
export const getCurrentUserId = UserService.getCurrentUserId;
export const getCurrentUserName = UserService.getCurrentUserName;
export const getCurrentUserEmail = UserService.getCurrentUserEmail;
export const getCurrentUserRole = UserService.getCurrentUserRole;
export const getCurrentUserPermissions = UserService.getCurrentUserPermissions;
export const getCurrentUserEntityId = UserService.getCurrentUserEntityId;
export const getCurrentUserAvatar = UserService.getCurrentUserAvatar;
export const hasPermission = UserService.hasPermission;
export const hasAnyPermission = UserService.hasAnyPermission;
export const hasAllPermissions = UserService.hasAllPermissions;
export const isLoggedIn = UserService.isLoggedIn;
export const getDisplayName = UserService.getDisplayName;
export const getUserInitials = UserService.getUserInitials;
export const getUserProperty = UserService.getUserProperty;
export const isUserActive = UserService.isUserActive;
