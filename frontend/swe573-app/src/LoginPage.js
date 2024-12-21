import React, { useState, useContext } from 'react';
import { UserContext } from './UserContext';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const [usernameInput, setUsernameInput] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const { setUsername } = useContext(UserContext);
  const navigate = useNavigate(); // Hook for navigation

  const handleLogin = async () => {
    const formData = new URLSearchParams();
    formData.append("username", usernameInput);
    formData.append("password", password);

    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/login`, {
      method: "POST",
      credentials: 'include',
      body: formData
    });

    if (response.ok) {
      setMessage("Login successful!");

      // After login, fetch the user info
      const meRes = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users/me`, { credentials: 'include' });
      if (meRes.ok) {
        const meData = await meRes.json();
        setUsername(meData.username);

        navigate("/");
      }
    } else {
      const data = await response.json();
      setMessage(`Error: ${data.detail}`);
    }
  };

  return (
    <div className="container" style={{ maxWidth: "400px", marginTop: "50px" }}>
      <h2 className="mb-4">Login</h2>
      <div className="mb-3">
        <label htmlFor="login-username" className="form-label">Username</label>
        <input
          type="text"
          className="form-control"
          id="login-username"
          placeholder="Enter username"
          value={usernameInput}
          onChange={(e) => setUsernameInput(e.target.value)}
        />
      </div>

      <div className="mb-3">
        <label htmlFor="login-password" className="form-label">Password</label>
        <input
          type="password"
          className="form-control"
          id="login-password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <button className="btn btn-primary w-100" onClick={handleLogin}>
        Login
      </button>

      {message && <div className="alert alert-info mt-3">{message}</div>}
    </div>
  );
}

export default LoginPage;
