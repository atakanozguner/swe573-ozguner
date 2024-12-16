import { writable } from 'svelte/store';

// Store to hold user data
export const user = writable(null);

// Store to track authentication state
export const isAuthenticated = writable(false);
