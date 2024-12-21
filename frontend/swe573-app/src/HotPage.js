import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function HotPage() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/posts/hot`, { credentials: 'include' })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch hot posts");
        }
        return res.json();
      })
      .then((data) => setPosts(data))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="container mt-5 text-center"><p>Error: {error}</p></div>;
  }

  return (
    <div className="container mt-5">
      <h1>🔥 Hot Posts</h1>
      <div className="mb-3 text-end">
        <Link to="/posts/" className="btn btn-success">All Posts</Link>
      </div>
      {posts.length === 0 && <p>No hot posts available yet.</p>}
      <div className="row">
        {posts.map(post => (
          <div className="col-md-4 mb-4" key={post.id}>
            <div className="card">
              {post.image_url && (
                <img src={`${process.env.REACT_APP_BACKEND_URL}${post.image_url}`} className="card-img-top" alt={post.title} />
              )}
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <p className="card-text">Interest: {post.interest_count}</p>
                <Link to={`/posts/${post.id}`} className="btn btn-primary">View Details</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HotPage;
