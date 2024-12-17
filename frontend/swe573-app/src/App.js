import React, { useContext, useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import HomePage from './HomePage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import PostsPage from './PostsPage';
import CreatePostPage from './CreatePostPage';
import PostDetailPage from './PostDetailPage';
import HotPage from './HotPage';
import SearchResultsPage from './SearchResultsPage';

import { UserContext } from './UserContext';

function App() {
  const { username, setUsername } = useContext(UserContext);
  const [searchQuery, setSearchQuery] = useState("");

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
          <div className="collapse navbar-collapse">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <Link className="nav-link" to="/posts">Posts</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/posts/hot">🔥 Hot</Link>
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
            <SearchForm searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        {!username && <Route path="/register" element={<RegisterPage />} />}
        <Route path="/posts" element={<PostsPage />} />
        <Route path="/posts/new" element={<CreatePostPage />} />
        <Route path="/posts/:id" element={<PostDetailPage />} />
        <Route path="/posts/hot" element={<HotPage />} />
        <Route path="/search" element={<SearchResultsPage />} />
      </Routes>
    </Router>
  );
}

function SearchForm({ searchQuery, setSearchQuery }) {
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?query=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <form className="d-flex" onSubmit={handleSearch}>
      <input
        className="form-control me-2"
        type="search"
        placeholder="Search"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button className="btn btn-outline-light" type="submit">Search</button>
    </form>
  );
}

export default App;