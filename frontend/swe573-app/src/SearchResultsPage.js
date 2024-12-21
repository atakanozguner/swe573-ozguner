import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function SearchResultsPage() {
  const query = useQuery().get("query");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (query) {
      fetch(`${process.env.REACT_APP_BACKEND_URL}/posts/search?query=${encodeURIComponent(query)}`, {
        credentials: 'include',
      })
        .then(res => {
          if (!res.ok) throw new Error("Failed to fetch search results");
          return res.json();
        })
        .then(data => setResults(data))
        .catch(err => setError(err.message));
    }
  }, [query]);

  if (error) {
    return <div className="container mt-5 text-center"><p>Error: {error}</p></div>;
  }

  return (
    <div className="container mt-5">
      <h1>Search Results for "{query}"</h1>
      {results.length === 0 && <p>No posts match your search query.</p>}
      <div className="row">
        {results.map(post => (
          <div className="col-md-4 mb-4" key={post.id}>
            <div className="card">
              {post.image_url && (
                <img
                  src={`${process.env.REACT_APP_BACKEND_URL}${post.image_url}`}
                  className="card-img-top"
                  alt={post.title}
                />
              )}
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <p className="card-text">{post.description || "No description available"}</p>
                <Link to={`/posts/${post.id}`} className="btn btn-primary">View Details</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SearchResultsPage;
