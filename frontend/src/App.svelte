<script>
    import { Router, Route } from 'svelte-routing';
    import Home from './Home.svelte';
    import Register from './Register.svelte';
    import Login from './Login.svelte';
</script>

<Router>
    <Route path="/" component={Home} />
    <Route path="/register" component={Register} />
    <Route path="/login" component={Login} />
</Router>
