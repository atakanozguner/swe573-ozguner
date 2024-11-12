<script>
    import { user, isAuthenticated } from './stores';
    import { onMount } from 'svelte';

    // Check localStorage for the token and update authentication state
    onMount(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            isAuthenticated.set(true);
            user.set(localStorage.getItem('user') || '');  // Set user from localStorage if available
        } else {
            isAuthenticated.set(false);
        }
    });

    function logout() {
        localStorage.removeItem('access_token');
        user.set(null);
        isAuthenticated.set(false);
        window.location.href = '/login';  // Redirect to login page
    }
</script>

{#if $isAuthenticated}
    <h1>Welcome, {$user}!</h1>
    <button on:click={logout}>Logout</button>
{:else}
    <p>You are not logged in. <a href="/login">Login here</a> or <a href="/register">Register</a>.</p>
{/if}
