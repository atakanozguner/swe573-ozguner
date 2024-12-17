import React, { useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './HomePage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import { UserContext } from './UserContext';

function App() {
  const { username, setUsername } = useContext(UserContext);

  useEffect(() => {
    fetch("http://localhost:8000/users/me", { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject())
      .then(data => setUsername(data.username))
      .catch(() => setUsername(null));
  }, [setUsername]);

  const handleLogout = () => {
    fetch("http://localhost:8000/logout", {
      method: "POST",
      credentials: 'include'
    }).then(res => {
      if (res.ok) {
        setUsername(null);
      }
    });
  };

  return (
    <Router>
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container-fluid">
          <Link className="navbar-brand" to="/">SWE573 App</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <Link className="nav-link" to="/">Home</Link>
              </li>
              {username ? (
                <>
                  <li className="nav-item">
                    <span className="nav-link">Welcome, {username}</span>
                  </li>
                  <li className="nav-item">
                    <button className="nav-link btn btn-link" onClick={handleLogout}>Logout</button>
                  </li>
                </>
              ) : (
                <>
                  <li className="nav-item">
                    <Link className="nav-link" to="/login">Login</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/register">Register</Link>
                  </li>
                </>
              )}
            </ul>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        {!username && <Route path="/register" element={<RegisterPage />} />}
      </Routes>
    </Router>
  );
}

export default App;
