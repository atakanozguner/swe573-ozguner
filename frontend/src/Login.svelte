<script>
    import { user, isAuthenticated } from './stores';
    let username = '';
    let password = '';
    let error = '';

    async function login() {
        const response = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            // Store the token and username in localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', username);  // Store the username
            user.set(username);  // Set the user store
            isAuthenticated.set(true);  // Set authentication status
            window.location.href = '/';  // Redirect to the homepage
        } else {
            error = data.detail || 'Login failed';
        }
    }
</script>

<h2>Login</h2>
<form on:submit|preventDefault={login}>
    <label>Username: <input type="text" bind:value={username} required /></label>
    <label>Password: <input type="password" bind:value={password} required /></label>
    <button type="submit">Login</button>
    {#if error}<p style="color: red;">{error}</p>{/if}
</form>
