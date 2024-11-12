<script>
    let username = '';
    let password = '';
    let error = '';

    async function register() {
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) {
            error = data.detail || 'Registration failed';
        } else {
            alert('Registration successful! Please proceed to login.');
            window.location.href = '/login'; // Redirect to login page
        }
    }
</script>

<h2>Register</h2>
<form on:submit|preventDefault={register}>
    <label>Username: <input type="text" bind:value={username} required /></label>
    <label>Password: <input type="password" bind:value={password} required /></label>
    <button type="submit">Register</button>
    {#if error}<p style="color: red;">{error}</p>{/if}
</form>
